import React, { useRef, useState, useEffect } from "react";
import { FaPlay, FaPause } from "react-icons/fa";

const AudioPlayer = ({ src }) => {
  const audioRef = useRef(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState(0);
  const [duration, setDuration] = useState(0);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const updateProgress = () => {
      setProgress((audio.currentTime / audio.duration) * 100);
    };

    const setAudioDuration = () => {
      setDuration(audio.duration);
    };

    audio.addEventListener("timeupdate", updateProgress);
    audio.addEventListener("loadedmetadata", setAudioDuration);

    return () => {
      audio.removeEventListener("timeupdate", updateProgress);
      audio.removeEventListener("loadedmetadata", setAudioDuration);
    };
  }, []);

  const togglePlay = () => {
    const audio = audioRef.current;
    if (!audio) return;

    if (isPlaying) {
      audio.pause();
    } else {
      audio.play();
    }

    setIsPlaying(!isPlaying);
  };

  const formatTime = (secs) => {
    if (isNaN(secs)) return "0:00";
    const minutes = Math.floor(secs / 60);
    const seconds = Math.floor(secs % 60).toString().padStart(2, "0");
    return `${minutes}:${seconds}`;
  };

  return (
    <div className="w-full bg-[#1a1a1a] p-4 rounded-xl shadow-md border border-[#333] text-white">
      <audio ref={audioRef} src={src} preload="metadata" />

      <div className="flex items-center space-x-4">
        <button
          onClick={togglePlay}
          className="button-reset"
        >
          {isPlaying ? <FaPause /> : <FaPlay />}
        </button>

        <div className="flex-1 relative h-2 bg-gray-700 rounded-full">
          <div
            className="absolute top-0 left-0 h-2 bg-[#00ffc3] rounded-full"
            style={{ width: `${progress}%` }}
          />
        </div>

        <span className="text-xs text-gray-400 min-w-[40px] text-right">
          {formatTime(duration)}
        </span>
      </div>
    </div>
  );
};

export default AudioPlayer;
