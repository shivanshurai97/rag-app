import React from "react";
import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";
import { logoutUser } from "../api/api"; // Make sure this path is correct

const Navbar = ({ toggleSidebar }) => {
  const { isAuthenticated, username, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await logoutUser(); // Call backend to clear session/cookie
    } catch (error) {
      console.error("Logout failed:", error);
    } finally {
      logout(); // Clear frontend state
      navigate("/login");
    }
  };

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-white shadow px-4 py-3 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <button
          className="md:hidden text-gray-700 focus:outline-none"
          onClick={toggleSidebar}
        >
          ☰
        </button>
        <h1 className="text-xl font-bold text-indigo-600">RAG Q&A App</h1>
      </div>

      {isAuthenticated && (
        <div className="flex items-center gap-4 text-sm text-gray-600">
          <span className="font-medium">Hello, {username}</span>
          <button onClick={handleLogout} className="hover:text-indigo-600">
            Logout
          </button>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
