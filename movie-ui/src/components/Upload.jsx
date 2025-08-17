import React, { useState, useEffect } from "react";
import Toast from "../components/Toast";
import Skeleton from "./Skeleton";
import axios from "axios";
import AudioPlayer from "../components/AudioPlayer"; // update path if needed

const Upload = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [metaData, setMetaData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [isFreshUpload, setIsFreshUpload] = useState(false);
  const [viewMode, setViewMode] = useState(null); // "chapters", "summary", "transcript", "narration"
  const [expandedChapters, setExpandedChapters] = useState({});
  const userEmail = localStorage.getItem("userEmail");
  const [toastMessage, setToastMessage] = useState("");
  const [toast, setToast] = useState({ message: "", type: "" });
  const [uploadProgress, setUploadProgress] = useState(0);

  const handleFileChange = (event) => setSelectedFile(event.target.files[0]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!selectedFile || !userEmail)
      return setToast({
        message: "Please, Login and Select a File",
        type: "error",
      });

    setLoading(true);
    setUploadProgress(0);
    setMetaData(null);
    setViewMode(null);
    setExpandedChapters({});

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const response = await axios.post(
        `http://127.0.0.1:8000/upload?email=${encodeURIComponent(userEmail)}`,
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
          onUploadProgress: (progressEvent) => {
            const percent = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            );
            setUploadProgress(percent);
          },
        }
      );

      const data = response.data; 
      if (data?.error) throw new Error(data.error);

      setToast({ message: "Upload Sucessful", type: "success" });
      setMetaData(data);
      setIsFreshUpload(true); // ✅ Only true when freshly uploaded
    } catch (error) {
      console.error("Upload error:", error);
      setToast({ message: "Upload Failed !!!", type: "error" });
    } finally {
      setLoading(false);
      setUploadProgress(0);
    }
  };

  const toggleChapter = (index) => {
    setExpandedChapters((prev) => ({ ...prev, [index]: !prev[index] }));
  };

  const fetchPreviousResults = async () => {
    if (!userEmail) return;
    try {
      const res = await fetch(
        `http://127.0.0.1:8000/model-results?email=${encodeURIComponent(
          userEmail
        )}`
      );
      const data = await res.json();
      if (Array.isArray(data) && data.length > 0) {
        setMetaData(data[data.length - 1]);
        setIsFreshUpload(false);
      }
    } catch (err) {
      console.error("Failed to fetch previous results", err);
    }
  };

  useEffect(() => {
    fetchPreviousResults();
  }, []);

  return (
    <section className="relative py-40 px-6 text-white overflow-hidden z-10">
      {toastMessage && (
        <Toast message={toastMessage} onClose={() => setToastMessage("")} />
      )}
      <div className="relative z-10 max-w-3xl mx-auto text-center">
        <div className="flex items-center justify-center mb-12 space-x-2">
          <hr className="flex-grow border-t-2 border-[#00ffc3] w-1/4" />
          <h2 className="text-4xl md:text-5xl font-bold text-[#00ffc3] whitespace-nowrap">
            Upload Your Video
          </h2>
          <hr className="flex-grow border-t-2 border-[#00ffc3] w-1/4" />
        </div>

        {toast.message && (
          <Toast
            message={toast.message}
            type={toast.type}
            onClose={() => setToast({ message: "", type: "" })}
          />
        )}

        {/* Upload Form */}
        <form
          className="space-y-6 bg-white/5 backdrop-blur-3xl border border-white/10 rounded-2xl p-7 text-white shadow-md"
          onSubmit={handleSubmit}
        >
          <label
            htmlFor="video"
            className="block border-2 border-dashed border-gray-600 rounded-xl p-6 text-gray-300 cursor-pointer hover:border-[#00ffc3] transition duration-300"
          >
            <input
              type="file"
              id="video"
              accept="video/mp4"
              onChange={handleFileChange}
              className="hidden"
            />
            {selectedFile ? (
              <div className="flex items-center justify-center space-x-3 text-[#00ffc3] font-medium">
                <svg
                  className="w-6 h-6 text-green-500"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
                <span>{selectedFile.name} selected</span>
              </div>
            ) : (
              <span className="text-gray-400">
                Click to select an MP4 video
              </span>
            )}
          </label>

          <button
            type="submit"
            className="mt-8 w-full px-8 py-3 bg-[#00ffc3] text-black font-semibold rounded-xl shadow-md hover:bg-[#02e6b0] transition-all duration-300 disabled:opacity-50"
            disabled={loading}
          >
            {loading ? "Processing..." : "Upload Now"}
          </button>
        </form>

        {/* ⏳ Loading */}
        {loading && uploadProgress > 0 && (
          <div className="w-full mt-4 text-center">
            <p className="text-sm text-gray-300 mb-1">
              Uploading... {uploadProgress}%
            </p>
            <div className="w-full bg-gray-700 h-2 rounded overflow-hidden">
              <div
                className="bg-[#00ffc3] h-full transition-all duration-200"
                style={{ width: `${uploadProgress}%` }}
              ></div>
            </div>
          </div>
        )}

        {/* 🚀 View Mode Buttons */}
        {!loading && metaData && isFreshUpload && (
          <div className="mt-10 grid grid-cols-2 sm:flex sm:flex-wrap justify-center gap-4 sm:gap-11">
            <button
              onClick={() => setViewMode("chapters")}
              className="px-6 py-2 rounded-full bg-[#00ffc3] text-black font-semibold hover:bg-[#02e6b0]"
            >
              Chapters
            </button>
            <button
              onClick={() => setViewMode("summary")}
              className="px-6 py-2 rounded-full bg-[#00ffc3] text-black font-semibold hover:bg-[#02e6b0]"
            >
              Summary
            </button>
            <button
              onClick={() => setViewMode("transcript")}
              className="px-6 py-2 rounded-full bg-[#00ffc3] text-black font-semibold hover:bg-[#02e6b0]"
            >
              Transcription
            </button>
            <button
              onClick={() => setViewMode("narration")}
              className="px-6 py-2 rounded-full bg-[#00ffc3] text-black font-semibold hover:bg-[#02e6b0]"
            >
              Narration
            </button>
          </div>
        )}

        {/* 📚 Chapters */}
        {viewMode === "chapters" && metaData?.chapters?.length > 0 && (
          <div className="mt-8 text-left bg-white/5 backdrop-blur-lg p-6 rounded-xl border border-white/10">
            <h3 className="text-2xl font-semibold text-[#00ffc3] mb-4 text-center">
              Chapters
            </h3>
            <ul className="space-y-4">
              {metaData.chapters.map((chap, index) => (
                <li key={index} className="p-4 rounded-lg">
                  <button
                    onClick={() => toggleChapter(index)}
                    className="w-50 px-4 py-2 bg-[#00ffc3] text-black font-semibold rounded-xl shadow-md hover:bg-[#02e6b0] transition-all duration-300"
                  >
                    {chap.title || `Chapter ${index + 1}`} — ⏱ {chap.start_time}{" "}
                    → {chap.end_time}
                  </button>

                  {expandedChapters[index] && (
                    <div className="mt-3 text-gray-300 text-sm space-y-2">
                      <p className="text-base text-gray-300 whitespace-pre-wrap mb-0 text-justify">
                        {chap.summary}
                      </p>

                      {chap.narration_path && (
                        <div className="mt-2">
                          <audio controls className="w-full">
                            <source
                              src={`http://localhost:8000/download/narration/chapters/${chap.narration_path
                                .split("/")
                                .pop()}`}
                              type="audio/mpeg"
                            />
                          </audio>
                          <button
                            onClick={() => {
                              const link = document.createElement("a");
                              link.href = `http://localhost:8000/download/narration/chapters/${chap.narration_path
                                .split("/")
                                .pop()}`;
                              link.download = `chapter_${
                                index + 1
                              }_narration.mp3`;
                              document.body.appendChild(link);
                              link.click();
                              document.body.removeChild(link);
                            }}
                            className="block mx-auto mt-4 px-4 py-1 bg-[#00ffc3] text-black text-md font-semibold rounded-xl shadow-md hover:bg-[#02e6b0] transition-all duration-300"
                          >
                            Download Narration
                          </button>
                        </div>
                      )}
                    </div>
                  )}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* 📝 Summary */}
        {viewMode === "summary" && metaData?.summary && (
          <div className="mt-8 text-left bg-white/5 backdrop-blur-lg p-6 rounded-xl border border-white/10">
            <h3 className="text-2xl text-center pb-5 font-semibold text-[#00ffc3] mb-2">
              Summary
            </h3>
            <p className="text-base text-gray-300 whitespace-pre-wrap mb-0 text-justify">
              {metaData.summary}
            </p>
          </div>
        )}

        {/* 📜 Transcription */}
        {viewMode === "transcript" && metaData?.transcription && (
          <div className="mt-8 text-left bg-white/5 backdrop-blur-lg p-6 rounded-xl border border-white/10">
            <h3 className="text-2xl text-center pb-5 font-semibold text-[#00ffc3] mb-2">
              Full Transcription
            </h3>
            <p className="text-sm text-gray-300 whitespace-pre-wrap mb-0 text-justify">
              {metaData.transcription}
            </p>
          </div>
        )}

        {/* 🔊 Narration (Full) */}
        {viewMode === "narration" && metaData?.narration && (
          <div className="mt-8 text-center">
            <div className="text-left bg-white/5 backdrop-blur-lg p-6 rounded-xl border border-white/10">
              <h3 className="text-2xl text-center pb-5 font-semibold text-[#00ffc3] mb-4">
                Full Narration
              </h3>

              <AudioPlayer src={`http://localhost:8000${metaData.narration}`} />

              <button
                onClick={() => {
                  const link = document.createElement("a");
                  link.href = `http://localhost:8000/download/narration/${metaData.narration
                    .split("/")
                    .pop()}`;
                  link.download = selectedFile
                    ? selectedFile.name.replace(/\.[^/.]+$/, "") +
                      "_narration.mp3"
                    : "narration.mp3";
                  document.body.appendChild(link);
                  link.click();
                  document.body.removeChild(link);
                }}
                className="block mx-auto mt-4 px-4 py-1 bg-[#00ffc3] text-black text-md font-semibold rounded-xl shadow-md hover:bg-[#02e6b0] transition-all duration-300"
              >
                Download Narration
              </button>
            </div>
          </div>
        )}
      </div>
    </section>
  );
};

export default Upload;
