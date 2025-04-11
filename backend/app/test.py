from pydub import AudioSegment
audio = AudioSegment.from_file("test.mp3", format="mp3")
audio.export("test.wav", format="wav")