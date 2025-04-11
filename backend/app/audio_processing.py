import os
import re
import logging
from collections import Counter
from typing import List, Tuple
import moviepy.editor as mp
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip
from pydub import AudioSegment
import whisper
import cv2
import numpy as np
from dotenv import load_dotenv
from app.utils import ensure_directory
from gtts import gTTS
import time
import nltk
from nltk import pos_tag, word_tokenize
from nltk.corpus import wordnet as wn
import shutil
import pyttsx3

# Load environment variables
load_dotenv()

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "tiny")
TEMP_DIR = os.getenv("TEMP_DIR", "data/temp")
BASE_WORD_LIMIT = int(os.getenv("BASE_WORD_LIMIT", 10))
BASE_DURATION = float(os.getenv("BASE_DURATION", 3.0))

# NLTK Setup
nltk_available = False
try:
    nltk.download('averaged_perceptron_tagger', quiet=True, raise_on_error=True)
    nltk.download('punkt', quiet=True, raise_on_error=True)
    nltk.download('wordnet', quiet=True, raise_on_error=True)
    nltk_available = True
    logger.info("NLTK resources found/downloaded successfully.")
except Exception as e:
    logger.warning(f"Failed to download/verify NLTK resources: {str(e)}. Some features might be limited.")
    pos_tag = None
    word_tokenize = None
    wn = None

# Transformers Summarizer Setup
transformers_available = False
summarizer = None
try:
    from transformers import pipeline
    logger.info("Loading BART-large for summarization...")
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    transformers_available = True
    logger.info("Successfully loaded BART-large summarization pipeline.")
except ImportError:
    logger.warning("Transformers library not found. Summarization disabled.")
except Exception as e:
    logger.error(f"Failed to initialize summarization pipeline: {str(e)}. Summarization disabled.")

# Constants
CORRECTION_DICT = {
    'capy': 'capybara', 'koalaa': 'koala', 'koalaaia': 'koala',
    'groundhog standing': 'groundhog', 'sar': 'sari',
}
VAGUE_SUBJECTS = {'group', 'couple', 'flock', 'large', 'image', 'photo', 'picture', 'screenshot'}

# FFmpeg Check
def check_ffmpeg():
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path is None:
        logger.error("FFmpeg not found in PATH. Please install FFmpeg.")
        raise RuntimeError("FFmpeg is required but not found.")
    logger.info(f"FFmpeg found at: {ffmpeg_path}")

check_ffmpeg()

# Audio Extraction
def extract_audio(video_path: str) -> str | None:
    audio_path = os.path.join(TEMP_DIR, "audio.wav")
    video = None
    audio = None
    try:
        ensure_directory(os.path.dirname(audio_path))
        logger.info(f"Extracting audio from: {video_path}")
        video = mp.VideoFileClip(video_path)
        audio = video.audio
        if audio is None:
            logger.warning(f"No audio track found in {video_path}")
            return None
        audio.write_audiofile(audio_path, codec='pcm_s16le', logger=None)
        logger.info(f"Audio extracted successfully to: {audio_path}")
        return audio_path
    except Exception as e:
        logger.error(f"Error extracting audio from {video_path}: {str(e)}")
        return None
    finally:
        if audio: audio.close()
        if video: video.close()

# Audio Transcription
whisper_model = None

def load_whisper_model():
    global whisper_model
    if whisper_model is None:
        try:
            logger.info(f"Loading Whisper model: {WHISPER_MODEL}")
            whisper_model = whisper.load_model(WHISPER_MODEL)
            logger.info(f"Whisper model '{WHISPER_MODEL}' loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load Whisper model '{WHISPER_MODEL}': {str(e)}")
            raise
    return whisper_model

def transcribe_audio(audio_path: str) -> dict:
    if not os.path.exists(audio_path) or os.path.getsize(audio_path) == 0:
        logger.warning(f"Audio file does not exist or is empty: {audio_path}")
        return {"text": "", "segments": []}
    try:
        model = load_whisper_model()
        logger.info(f"Starting transcription for: {audio_path}")
        result = model.transcribe(audio_path, verbose=False)
        logger.info(f"Transcription complete for: {audio_path}")
        return result
    except Exception as e:
        logger.error(f"Error transcribing audio {audio_path}: {str(e)}")
        return {"text": "", "segments": []}

# Dialogue Detection
def detect_dialogue_segments(transcription: dict) -> list:
    segments = transcription.get("segments", [])
    dialogue_segments = []
    if not segments:
        return []
    for segment in segments:
        text = segment.get("text", "").strip()
        if text:
            dialogue_segments.append({
                "start": segment.get("start", 0.0),
                "end": segment.get("end", 0.0),
                "text": text
            })
    return dialogue_segments

# Audio Description Helpers
def is_animate(subject: str) -> bool | None:
    if not nltk_available or wn is None:
        if subject.lower() in ['person', 'people', 'man', 'woman', 'child', 'children', 'animal', 'dog', 'cat']:
            return True
        if subject.endswith('s'):
            return True
        return None
    try:
        synsets = wn.synsets(subject, pos=wn.NOUN)
        if not synsets:
            return None if subject not in ['person', 'people', 'man', 'woman', 'child', 'children'] else True
        target_synsets = {wn.synset('person.n.01'), wn.synset('animal.n.01')}
        for synset in synsets:
            closure = set(synset.closure(lambda s: s.hypernyms()))
            closure.add(synset)
            if target_synsets.intersection(closure):
                return True
        artifact_synset = wn.synset('artifact.n.01')
        object_synset = wn.synset('object.n.01')
        for synset in synsets:
            closure = set(synset.closure(lambda s: s.hypernyms()))
            closure.add(synset)
            if artifact_synset in closure or object_synset in closure:
                return False
        return False
    except Exception as e:
        logger.warning(f"WordNet lookup failed for '{subject}': {e}")
        return None

def generate_scene_summary_nltk(scene_descriptions: List[str], word_limit: int, prev_summaries: set) -> str:
    if not nltk_available or not scene_descriptions:
        return scene_descriptions[0] if scene_descriptions else "A scene unfolds."

    subjects = Counter()
    locations = Counter()
    actions = Counter()
    for desc in scene_descriptions:
        try:
            tokens = word_tokenize(desc.lower())
            tags = pos_tag(tokens)
            for word, tag in tags:
                if tag.startswith('NN') and word not in VAGUE_SUBJECTS and len(word) > 2:
                    word_index = tokens.index(word)
                    if word_index > 0 and tokens[word_index-1] in ['in', 'on', 'at', 'near', 'by', 'under', 'over']:
                        locations[word] += 1
                    else:
                        subjects[word] += 1
                elif tag.startswith('VB'):
                    if word.endswith('ing'):
                        actions[word] += 1
                    elif word.endswith('inging'):
                        actions[word[:-3] + 'ing'] += 1
        except Exception as e:
            logger.warning(f"NLTK processing failed for '{desc}': {e}")
            continue

    top_subjects = subjects.most_common(2)
    top_location = locations.most_common(1)[0][0] if locations else None
    top_action = actions.most_common(1)[0][0] if actions else None

    summary = ""
    if len(top_subjects) >= 2:
        subj1, subj2 = top_subjects[0][0], top_subjects[1][0]
        article1 = "An" if subj1[0].lower() in 'aeiou' else "A"
        article2 = "an" if subj2[0].lower() in 'aeiou' else "a"
        summary = f"{article1} {subj1} and {article2} {subj2}"
        if top_action:
            summary += f" are {top_action}"
    elif top_subjects:
        subj = top_subjects[0][0]
        article = "An" if subj[0].lower() in 'aeiou' else "A"
        summary = f"{article} {subj}"
        if top_action:
            summary += f" is {top_action}"

    if top_location:
        prep = "in" if top_location in ['car', 'building', 'room', 'water'] else \
               "on" if top_location in ['table', 'floor', 'ground', 'road'] else "at"
        summary += f" {prep} the {top_location}"
    if not summary:
        summary = scene_descriptions[0]

    summary = summary.strip() + "."
    summary_words = summary.split()
    if len(summary_words) > word_limit:
        summary = " ".join(summary_words[:word_limit]) + "..."

    # Ensure diversity
    base_summary = summary
    suffix = ""
    count = 1
    while summary in prev_summaries:
        summary = f"{base_summary[:-1]} {count}."
        count += 1
    logger.info(f"NLTK-based summary: {summary}")
    return summary

def create_audio_descriptions(
    visual_descriptions: List[str],
    frame_times: List[float],
    video_duration: float,
    transcription: str = "",
    has_actual_dialogue: bool = False
) -> List[Tuple[str, float, float]]:
    logger.info("Using updated create_audio_descriptions with gTTS (version 2025-04-10).")
    description_audios_details = []
    prev_summaries = set()

    if not visual_descriptions or not frame_times:
        logger.warning("No visual descriptions or frame times provided.")
        return []

    try:
        if len(visual_descriptions) != len(frame_times):
            logger.warning(f"Mismatch between descriptions ({len(visual_descriptions)}) and frame times ({len(frame_times)}).")
            min_len = min(len(visual_descriptions), len(frame_times))
            visual_descriptions = visual_descriptions[:min_len]
            frame_times = frame_times[:min_len]
            if min_len == 0:
                return []

        word_limit = BASE_WORD_LIMIT + 5  # Increased for more detail
        duration_limit = BASE_DURATION
        if video_duration < 5:
            word_limit = max(5, BASE_WORD_LIMIT)
            duration_limit = max(1.5, BASE_DURATION - 1.0)
        elif video_duration > 30:
            word_limit = BASE_WORD_LIMIT + 10
            duration_limit = BASE_DURATION + 1.0
        if has_actual_dialogue:
            word_limit = max(5, word_limit - 2)
            duration_limit = max(1.5, duration_limit - 0.5)
        logger.info(f"Adjusted word_limit: {word_limit}, duration_limit: {duration_limit}s")

        def clean_description(desc):
            desc = desc.lower().strip()
            desc = re.sub(r'\s+', ' ', desc)
            words = desc.split()
            corrected_words = [CORRECTION_DICT.get(word, word) for word in words]
            desc = " ".join(corrected_words)
            desc = re.sub(r'^(a photo of|a picture of|an image of|screenshot of)\s+', '', desc)
            desc = re.sub(r'\s+(in the background|on the screen)$', '', desc)
            return desc

        cleaned_descriptions_with_times = [(clean_description(desc), frame_time)
                                           for desc, frame_time in zip(visual_descriptions, frame_times)
                                           if desc and isinstance(desc, str)]

        if cleaned_descriptions_with_times and cleaned_descriptions_with_times[0][1] > 0.0:
            earliest_desc = min(cleaned_descriptions_with_times, key=lambda x: x[1])
            cleaned_descriptions_with_times.insert(0, (earliest_desc[0], 0.0))
            logger.info("Added description for first frame at 0.0s.")

        unique_descriptions = list(dict.fromkeys([desc for desc, _ in cleaned_descriptions_with_times]))
        meta_terms = {'clip', 'video', 'audio', 'description', 'track', 'watch', 'share', 'movie', 'scene', 'animated', 'disney', 'logo', 'watermark', 'copyright', 'subscribe'}
        filtered_descriptions_with_times = []
        for desc, frame_time in cleaned_descriptions_with_times:
            if desc and not any(term in desc for term in meta_terms) and desc not in VAGUE_SUBJECTS:
                if not filtered_descriptions_with_times or desc != filtered_descriptions_with_times[-1][0]:
                    filtered_descriptions_with_times.append((desc, frame_time))
        if not filtered_descriptions_with_times:
            logger.warning("No suitable descriptions after filtering.")
            if cleaned_descriptions_with_times:
                filtered_descriptions_with_times = [(cleaned_descriptions_with_times[0][0], cleaned_descriptions_with_times[0][1])]
            else:
                return []
        logger.info(f"Filtered descriptions: {len(filtered_descriptions_with_times)}")

        scenes = []
        if not filtered_descriptions_with_times:
            return []
        current_scene_descriptions = []
        current_scene_start_time = filtered_descriptions_with_times[0][1]
        for i, (desc, frame_time) in enumerate(filtered_descriptions_with_times):
            start_new_scene = False
            if not current_scene_descriptions:
                start_new_scene = False
            else:
                if frame_time - current_scene_start_time > 8.0:
                    start_new_scene = True
                else:
                    prev_desc = current_scene_descriptions[-1]
                    common_words = len(set(desc.split()) & set(prev_desc.split()))
                    if common_words < 2:
                        start_new_scene = True
            if start_new_scene:
                scenes.append({
                    'descriptions': list(current_scene_descriptions),
                    'start_time': current_scene_start_time,
                })
                current_scene_descriptions = [desc]
                current_scene_start_time = frame_time
            else:
                current_scene_descriptions.append(desc)
        if current_scene_descriptions:
            scenes.append({
                'descriptions': list(current_scene_descriptions),
                'start_time': current_scene_start_time,
            })
        logger.info(f"Grouped into {len(scenes)} scenes.")

        ensure_directory(TEMP_DIR)
        temp_files_to_clean = []

        pyttsx3_engine = None
        try:
            pyttsx3_engine = pyttsx3.init()
            pyttsx3_engine.setProperty('rate', 150)
            pyttsx3_engine.setProperty('volume', 0.9)
            voices = pyttsx3_engine.getProperty('voices')
            if voices:
                pyttsx3_engine.setProperty('voice', voices[0].id)
            logger.info("Initialized pyttsx3 as fallback TTS engine.")
        except Exception as e:
            logger.warning(f"Failed to initialize pyttsx3: {str(e)}. Using silent WAV if gTTS fails.")

        transcription_text = transcription if transcription else ""
        for idx, scene in enumerate(scenes):
            scene_descriptions = scene['descriptions']
            scene_start_time = scene['start_time']
            if not scene_descriptions:
                continue

            summary_text = "No description available."
            use_ai_summary = transformers_available and summarizer is not None and len(scene_descriptions) > 1
            if use_ai_summary:
                try:
                    combined_text = ". ".join(scene_descriptions)
                    if transcription_text:
                        combined_text += f" Dialogue: {transcription_text[:100]}..."  # Add dialogue context
                    max_input_len = 1024
                    if len(combined_text) > max_input_len:
                        combined_text = combined_text[:max_input_len]
                    summary_result = summarizer(
                        combined_text,
                        max_length=word_limit + 10,
                        min_length=max(5, word_limit),
                        do_sample=False,
                        num_beams=8,
                        length_penalty=1.2,
                        no_repeat_ngram_size=3
                    )
                    if summary_result and isinstance(summary_result, list):
                        summary = summary_result[0]['summary_text'].strip()
                        if len(summary.split()) >= 5 and summary.lower() not in [d.lower() for d in scene_descriptions]:
                            summary_text = summary if summary.endswith('.') else summary + '.'
                            logger.info(f"Scene {idx}: AI Summary: {summary_text}")
                        else:
                            use_ai_summary = False
                    else:
                        use_ai_summary = False
                except Exception as e:
                    logger.warning(f"Scene {idx}: AI summarization failed: {str(e)}")
                    use_ai_summary = False
            if not use_ai_summary:
                summary_text = generate_scene_summary_nltk(scene_descriptions, word_limit, prev_summaries)

            summary_text = re.sub(r'\s+a\.$', '.', summary_text)
            summary_text = re.sub(r'\.\s*\w+\.$', '.', summary_text)
            summary_text = summary_text.strip()
            if not summary_text.endswith('.'):
                summary_text += '.'
            prev_summaries.add(summary_text)
            logger.info(f"Scene {idx}: Cleaned summary text: {summary_text}")

            tts_success = False
            wav_path = os.path.join(TEMP_DIR, f"desc_audio_{idx}_{int(time.time())}.wav")
            mp3_path = os.path.join(TEMP_DIR, f"desc_audio_{idx}_{int(time.time())}.mp3")
            if summary_text and summary_text != "No description available.":
                try:
                    ensure_directory(os.path.dirname(wav_path))
                    tts = gTTS(text=summary_text, lang='en', slow=False)
                    tts.save(mp3_path)
                    logger.info(f"Scene {idx}: Generated MP3 with gTTS: {mp3_path}")
                    audio_segment = AudioSegment.from_file(mp3_path, format="mp3")
                    audio_segment.export(wav_path, format="wav")
                    os.remove(mp3_path)
                    logger.info(f"Scene {idx}: Converted MP3 to WAV: {wav_path}")

                    audio_segment = AudioSegment.from_wav(wav_path)
                    duration_sec = len(audio_segment) / 1000.0
                    if duration_sec > duration_limit:
                        audio_segment = audio_segment[:int(duration_limit * 1000)]
                        audio_segment.export(wav_path, format="wav")
                        duration_sec = duration_limit
                        logger.info(f"Scene {idx}: Truncated audio to {duration_limit}s")
                    description_audios_details.append((wav_path, scene_start_time, duration_sec))
                    tts_success = True
                    temp_files_to_clean.append(wav_path)
                    logger.info(f"Scene {idx}: Generated TTS for '{summary_text}' (Duration: {duration_sec:.2f}s) -> {wav_path}")
                except Exception as e:
                    logger.error(f"Scene {idx}: TTS generation failed: {str(e)}")
                    if pyttsx3_engine:
                        try:
                            pyttsx3_engine.save_to_file(summary_text, wav_path)
                            pyttsx3_engine.runAndWait()
                            audio_segment = AudioSegment.from_wav(wav_path)
                            duration_sec = len(audio_segment) / 1000.0
                            if duration_sec > duration_limit:
                                audio_segment = audio_segment[:int(duration_limit * 1000)]
                                audio_segment.export(wav_path, format="wav")
                                duration_sec = duration_limit
                            description_audios_details.append((wav_path, scene_start_time, duration_sec))
                            tts_success = True
                            temp_files_to_clean.append(wav_path)
                            logger.info(f"Scene {idx}: Generated TTS with pyttsx3 for '{summary_text}' (Duration: {duration_sec:.2f}s)")
                        except Exception as e:
                            logger.error(f"Scene {idx}: pyttsx3 failed: {str(e)}")
                    if not tts_success:
                        silent_audio = AudioSegment.silent(duration=1000)
                        silent_audio.export(wav_path, format="wav")
                        description_audios_details.append((wav_path, scene_start_time, 1.0))
                        temp_files_to_clean.append(wav_path)
                        logger.info(f"Scene {idx}: Used silent WAV fallback (Duration: 1.00s)")

        return description_audios_details

    except Exception as e:
        logger.error(f"Error creating audio descriptions: {str(e)}")
        for temp_file in temp_files_to_clean:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        return description_audios_details

# Audio Integration
def create_frozen_frame(video_path: str, freeze_start: float, duration_sec: float, fps: float = 30.0) -> VideoFileClip:
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"OpenCV: Failed to open video {video_path}")
    cap.set(cv2.CAP_PROP_POS_MSEC, freeze_start * 1000)
    ret, frame = cap.read()
    if not ret:
        cap.release()
        raise RuntimeError(f"OpenCV: Failed to read frame at {freeze_start}s from {video_path}")
    height, width = frame.shape[:2]
    cap.release()
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    temp_freeze_path = os.path.join(TEMP_DIR, f"freeze_{int(time.time() * 1000)}.mp4")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(temp_freeze_path, fourcc, fps, (width, height))
    num_frames = int(duration_sec * fps)
    for _ in range(num_frames):
        out.write(frame_rgb)
    out.release()
    return VideoFileClip(temp_freeze_path)

def detect_low_volume_segments(audio_segment: AudioSegment, duration_ms: int, threshold_db: float = -30.0, min_duration_ms: int = 1000) -> List[Tuple[int, int]]:
    low_volume_segments = []
    chunk_size_ms = 100
    i = 0
    while i < duration_ms:
        chunk = audio_segment[i:i + chunk_size_ms]
        if chunk.dBFS < threshold_db:
            start_ms = i
            while i < duration_ms and audio_segment[i:i + chunk_size_ms].dBFS < threshold_db:
                i += chunk_size_ms
            end_ms = min(i, duration_ms)
            if end_ms - start_ms >= min_duration_ms:
                low_volume_segments.append((start_ms, end_ms))
        else:
            i += chunk_size_ms
    return low_volume_segments

def integrate_audio_descriptions(
    video_path: str,
    original_audio_path: str | None,
    description_audios: List[Tuple[str, float, float]],
    output_path: str,
    target_duration_limit: float = 3.0,
    low_volume_threshold_db: float = -30.0,
    subtle_volume_reduction_db: float = -10.0,
    dialogue_volume_reduction_db: float = -25.0,  # Increased reduction
    dialogue_boost_db: float = 5.0  # Boost original dialogue
):
    final_audio_path = os.path.join(TEMP_DIR, f"final_integrated_audio_{int(time.time())}.wav")
    video = None
    final_audio_clip = None
    original_audio_segment = None
    video_segments = []
    temp_files_to_clean = []

    try:
        video = VideoFileClip(video_path)
        video_duration = video.duration
        video_duration_ms = int(video_duration * 1000)
        logger.info(f"Original video duration: {video_duration:.2f} seconds.")

        if original_audio_path and os.path.exists(original_audio_path) and os.path.getsize(original_audio_path) > 0:
            logger.info(f"Loading original audio from: {original_audio_path}")
            original_audio_segment = AudioSegment.from_wav(original_audio_path)
            original_audio_duration_ms = len(original_audio_segment)
            if original_audio_duration_ms > video_duration_ms:
                original_audio_segment = original_audio_segment[:video_duration_ms]
            elif original_audio_duration_ms < video_duration_ms:
                silence_needed = video_duration_ms - original_audio_duration_ms
                original_audio_segment += AudioSegment.silent(duration=silence_needed)
            final_audio = original_audio_segment
            transcription = transcribe_audio(original_audio_path)
            dialogue_segments = detect_dialogue_segments(transcription)
            logger.info(f"Dialogue segments detected: {len(dialogue_segments)}")

            # Boost dialogue segments
            for seg in dialogue_segments:
                start_ms = int(seg['start'] * 1000)
                end_ms = int(seg['end'] * 1000)
                dialogue_segment = final_audio[start_ms:end_ms]
                boosted_segment = dialogue_segment + dialogue_boost_db
                final_audio = final_audio.overlay(boosted_segment, position=start_ms)
        else:
            logger.info("No valid original audio. Creating silent base track.")
            final_audio = AudioSegment.silent(duration=video_duration_ms)
            dialogue_segments = []

        low_volume_segments = []
        if original_audio_segment:
            low_volume_segments = detect_low_volume_segments(
                original_audio_segment, video_duration_ms, threshold_db=low_volume_threshold_db, min_duration_ms=1000
            )
            logger.info(f"Detected {len(low_volume_segments)} low-volume segments: {low_volume_segments}")

        occupied_slots_ms = []
        dialogue_buffer_ms = 200
        for seg in dialogue_segments:
            start_ms = max(0, int(seg['start'] * 1000) - dialogue_buffer_ms)
            end_ms = int(seg['end'] * 1000) + dialogue_buffer_ms
            occupied_slots_ms.append((start_ms, end_ms))
        occupied_slots_ms.sort(key=lambda x: x[0])
        logger.debug(f"Occupied slots (dialogue): {occupied_slots_ms}")

        description_audios.sort(key=lambda x: x[1])
        logger.info(f"Processing {len(description_audios)} description audios.")

        current_timestamp = 0.0
        original_timestamp = 0.0
        description_idx = 0
        last_placement_end_ms = 0

        while description_idx < len(description_audios):
            desc_path, intended_start_sec, desc_duration_sec = description_audios[description_idx]
            if not os.path.exists(desc_path) or os.path.getsize(desc_path) == 0:
                logger.warning(f"Description audio missing or empty: {desc_path}. Skipping.")
                description_idx += 1
                continue

            desc_audio = AudioSegment.from_wav(desc_path)
            desc_duration_ms = len(desc_audio)
            desc_duration_sec = desc_duration_ms / 1000.0
            logger.info(f"Description {description_idx}: Full duration is {desc_duration_sec:.2f}s")

            intended_start_ms = int(intended_start_sec * 1000)
            current_try_start_ms = max(last_placement_end_ms, intended_start_ms)

            # Try to fit in low-volume segment first
            placement_found = False
            placement_start_ms = -1
            subtle_placement = False
            for low_start_ms, low_end_ms in low_volume_segments:
                gap_duration_ms = low_end_ms - low_start_ms
                if low_start_ms <= current_try_start_ms <= low_end_ms and gap_duration_ms >= desc_duration_ms:
                    is_overlapping = False
                    for occ_start, occ_end in occupied_slots_ms:
                        if max(current_try_start_ms, occ_start) < min(current_try_start_ms + desc_duration_ms, occ_end):
                            is_overlapping = True
                            break
                    if not is_overlapping:
                        placement_found = True
                        placement_start_ms = current_try_start_ms
                        subtle_placement = True
                        if desc_duration_sec > (low_end_ms - low_start_ms) / 1000.0:
                            desc_audio = desc_audio[:low_end_ms - low_start_ms]
                            desc_duration_ms = low_end_ms - low_start_ms
                            desc_duration_sec = desc_duration_ms / 1000.0
                            logger.info(f"Description {description_idx}: Trimmed to fit gap: {desc_duration_sec:.2f}s")
                        break

            # If no suitable gap, overlap with dialogue but adjust volume
            if not placement_found:
                placement_start_ms = current_try_start_ms
                placement_start_sec = placement_start_ms / 1000.0
                if placement_start_sec + desc_duration_sec > video_duration:
                    placement_start_sec = max(0, video_duration - desc_duration_sec)
                    placement_start_ms = int(placement_start_sec * 1000)

                dialogue_overlap = False
                for occ_start, occ_end in occupied_slots_ms:
                    if max(placement_start_ms, occ_start) < min(placement_start_ms + desc_duration_ms, occ_end):
                        dialogue_overlap = True
                        break

                if dialogue_overlap:
                    desc_audio = desc_audio + dialogue_volume_reduction_db
                    logger.info(f"Description {description_idx}: Reduced volume by {dialogue_volume_reduction_db}dB due to dialogue overlap.")
                elif subtle_placement:
                    desc_audio = desc_audio + subtle_volume_reduction_db
                    logger.info(f"Description {description_idx}: Reduced volume by {subtle_volume_reduction_db}dB for subtle overlay.")

                if original_timestamp < placement_start_sec:
                    segment_duration = placement_start_sec - original_timestamp
                    if segment_duration > 0:
                        video_segment = video.subclip(original_timestamp, min(placement_start_sec, video_duration))
                        video_segments.append(video_segment)
                        current_timestamp += segment_duration
                        logger.info(f"Added video segment from {original_timestamp:.2f}s to {placement_start_sec:.2f}s (duration: {segment_duration:.2f}s)")

                # Only freeze if absolutely necessary
                if placement_start_sec + desc_duration_sec > video_duration or dialogue_overlap:
                    freeze_start = min(placement_start_sec, video_duration - 0.01)
                    try:
                        freeze_frame = create_frozen_frame(video_path, freeze_start, desc_duration_sec, fps=30.0)
                        temp_files_to_clean.append(freeze_frame.filename)
                    except Exception as e:
                        logger.error(f"Failed to create frozen frame at {freeze_start}s: {str(e)}")
                        freeze_end = min(freeze_start + 0.01, video_duration)
                        freeze_frame = video.subclip(freeze_start, freeze_end).set_duration(desc_duration_sec)
                    video_segments.append(freeze_frame)
                    logger.info(f"Froze frame at {freeze_start:.2f}s for {desc_duration_sec:.2f}s")
                    current_timestamp += desc_duration_sec
                else:
                    current_timestamp = placement_start_sec + desc_duration_sec

                final_audio = final_audio.overlay(desc_audio, position=placement_start_ms)
                occupied_slots_ms.append((placement_start_ms, placement_start_ms + desc_duration_ms))
                occupied_slots_ms.sort(key=lambda x: x[0])
                last_placement_end_ms = placement_start_ms + desc_duration_ms
                original_timestamp = placement_start_sec
                logger.info(f"Placed description {description_idx} at {placement_start_sec:.2f}s (duration: {desc_duration_sec:.2f}s)")

            else:
                placement_start_sec = placement_start_ms / 1000.0
                if original_timestamp < placement_start_sec:
                    segment_duration = placement_start_sec - original_timestamp
                    if segment_duration > 0:
                        video_segment = video.subclip(original_timestamp, min(placement_start_sec, video_duration))
                        video_segments.append(video_segment)
                        current_timestamp += segment_duration
                        logger.info(f"Added video segment from {original_timestamp:.2f}s to {placement_start_sec:.2f}s (duration: {segment_duration:.2f}s)")

                if subtle_placement:
                    desc_audio = desc_audio + subtle_volume_reduction_db
                    logger.info(f"Description {description_idx}: Reduced volume by {subtle_volume_reduction_db}dB for subtle overlay")
                final_audio = final_audio.overlay(desc_audio, position=placement_start_ms)
                occupied_slots_ms.append((placement_start_ms, placement_start_ms + desc_duration_ms))
                occupied_slots_ms.sort(key=lambda x: x[0])
                original_timestamp = placement_start_sec
                last_placement_end_ms = placement_start_ms + desc_duration_ms
                current_timestamp = placement_start_sec + desc_duration_sec
                logger.info(f"Placed description {description_idx} at {placement_start_sec:.2f}s (duration: {desc_duration_sec:.2f}s)")

            description_idx += 1

        if original_timestamp < video_duration:
            remaining_segment = video.subclip(original_timestamp, video_duration)
            video_segments.append(remaining_segment)
            logger.info(f"Added remaining video segment from {original_timestamp:.2f}s to {video_duration:.2f}s")
            current_timestamp = video_duration

        final_video = concatenate_videoclips(video_segments)
        new_video_duration = final_video.duration
        logger.info(f"New video duration after processing: {new_video_duration:.2f}s")

        final_audio_duration_ms = int(new_video_duration * 1000)
        if len(final_audio) < final_audio_duration_ms:
            final_audio += AudioSegment.silent(duration=final_audio_duration_ms - len(final_audio))
        elif len(final_audio) > final_audio_duration_ms:
            final_audio = final_audio[:final_audio_duration_ms]

        logger.info(f"Exporting final integrated audio to: {final_audio_path}")
        final_audio.export(final_audio_path, format="wav")
        final_audio_clip = AudioFileClip(final_audio_path)
        final_video = final_video.set_audio(final_audio_clip)

        logger.info(f"Writing final video to: {output_path}")
        final_video.write_videofile(output_path, codec="libx264", audio_codec="aac", logger=None, threads=4, preset='medium')
        logger.info("Final video writing complete.")

    except Exception as e:
        logger.error(f"Error integrating audio descriptions: {str(e)}")
        raise
    finally:
        logger.info("Cleaning up integration resources...")
        if final_audio_clip: final_audio_clip.close()
        if video: video.close()
        for segment in video_segments: segment.close()
        if os.path.exists(final_audio_path):
            os.remove(final_audio_path)
            logger.info(f"Removed intermediate audio file: {final_audio_path}")
        for temp_file in temp_files_to_clean:
            if os.path.exists(temp_file):
                os.remove(temp_file)
                logger.info(f"Removed temporary file: {temp_file}")
