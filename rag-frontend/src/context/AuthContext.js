// AuthContext.js
import { createContext, useContext, useEffect, useState } from "react";
import { validateUser, logoutUser } from "../api/api";

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [username, setUsername] = useState(null);

  useEffect(() => {
    const checkSession = async () => {
      try {
        const data = await validateUser();
        setUsername(data.username);
        setIsAuthenticated(true);
      } catch (err) {
        setIsAuthenticated(false);
        setUsername(null);
      } finally {
        setLoading(false);
      }
    };

    checkSession(); // ✅ Always validate session
  }, []);

  const login = (username) => {
    setIsAuthenticated(true);
    setUsername(username);
  };
  const logout = async () => {
    await logoutUser();
    setIsAuthenticated(false);
    setUsername(null);
  };

  return (
    <AuthContext.Provider
      value={{ isAuthenticated, login, logout, username, loading }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
