import React from "react";

const Skeleton = ({ width = "w-full", height = "h-6", rounded = "rounded" }) => {
  return (
    <div
      className={`bg-[#1e1e1e] ${width} ${height} ${rounded} animate-pulse`}
    ></div>
  );
};

export default Skeleton;
