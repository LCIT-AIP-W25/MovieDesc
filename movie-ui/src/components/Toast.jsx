import React, { useEffect, useState } from "react";
import { IoClose, IoCheckmarkCircle, IoWarning } from "react-icons/io5";

const Toast = ({ message, type = "success", onClose }) => {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    setVisible(true);
    const timer = setTimeout(() => {
      setVisible(false);
      setTimeout(onClose, 300); // Wait for animation
    }, 3000);
    return () => clearTimeout(timer);
  }, [onClose]);

  return (
    <div
      className={`fixed top-20 right-6 z-[999999] transition-all duration-800 transform ${
        visible ? "translate-x-0 opacity-100" : "translate-x-10 opacity-0"
      }`}
    >
      <div
        className={`
          relative px-5 py-3 rounded-xl shadow-xl text-sm font-medium 
          text-white backdrop-blur-md bg-white/10 border border-white/20
          flex items-center gap-3
          ${type === "success" ? "border-emerald-400/30" : "border-rose-400/30"}
        `}
      >
        <span className="text-xl">
          {type === "success" ? (
            <IoCheckmarkCircle className="text-green-400" />
          ) : (
            <IoWarning className="text-yellow-400" />
          )}
        </span>
        <span className="whitespace-pre-wrap">{message}</span>

        {/* ❌ Close button */}
        <button
          onClick={() => setVisible(false) || setTimeout(onClose, 300)}
          className="absolute button-reset top-1 right-2 text-white hover:text-[#00ffc3] transition"
        >
          <IoClose size={18} />
        </button>
      </div>
    </div>
  );
};

export default Toast;
