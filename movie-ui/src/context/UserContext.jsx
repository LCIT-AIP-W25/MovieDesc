// src/context/UserContext.jsx
import React, { createContext, useState, useEffect } from "react";

export const UserContext = createContext();

export const UserProvider = ({ children }) => {
  const [user, setUser] = useState(null);

  // ✅ Load from localStorage on mount
  useEffect(() => {
    const storedEmail = localStorage.getItem("userEmail");
    const fetchUser = async () => {
      if (storedEmail) {
        try {
          const res = await fetch(`http://127.0.0.1:8000/auth/user?email=${storedEmail}`);
          const data = await res.json();
          if (!data.error) setUser(data);
        } catch (err) {
          console.error("Failed to fetch user info", err);
        }
      }
    };
    fetchUser();
  }, []);

  return (
    <UserContext.Provider value={{ user, setUser }}>
      {children}
    </UserContext.Provider>
  );
};
