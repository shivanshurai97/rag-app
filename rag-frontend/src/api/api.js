import axios from "axios";

// Get the API URL from environment variables, fallback to localhost if not set
const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

// ✅ Global Axios config
const api = axios.create({
  baseURL: API_URL,
  withCredentials: true, // 🔐 Allow cookies to be sent
});

export const validateUser = async () => {
  const response = await api.get("auth/validate");
  return response.data; // should be { username: '...' }
};

// ✅ Auth APIs
export const loginUser = async (username, password) => {
  try {
    const formData = new URLSearchParams();
    formData.append("username", username);
    formData.append("password", password);

    const response = await api.post("auth/login", formData, {
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
    });

    return response.data;
  } catch (error) {
    console.error(
      "Login error:",
      error.response?.data?.detail || error.message
    );
    throw error;
  }
};

export const signupUser = async (username, email, password) => {
  try {
    const response = await api.post("auth/signup", {
      username,
      email,
      password,
    });
    return response.data;
  } catch (error) {
    console.log("API Error:", error); // Debug log
    console.log("API Error Response:", error.response); // Debug log
    throw error;
  }
};

export const logoutUser = async () => {
  try {
    await api.post("auth/logout");
  } catch (error) {
    console.error(
      "Logout error:",
      error.response?.data?.detail || error.message
    );
    throw error;
  }
};

// 📄 Example: Upload document
export const uploadDocument = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await api.post("documents/upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data;
  } catch (error) {
    console.error(
      "Upload error:",
      error.response?.data?.detail || error.message
    );
    throw error;
  }
};

// 📄 Document APIs
export const getDocuments = async () => {
  try {
    const response = await api.get("documents/list");
    return response.data;
  } catch (error) {
    console.error(
      "Error fetching documents:",
      error.response?.data?.detail || error.message
    );
    throw error;
  }
};

export const selectDocuments = async (documentIds) => {
  try {
    const response = await api.post("documents/select", {
      session_id: "default", // This can be removed if not needed in backend
      document_ids: documentIds,
    });
    return response.data;
  } catch (error) {
    console.error(
      "Error selecting documents:",
      error.response?.data?.detail || error.message
    );
    throw error;
  }
};

// 🤖 RAG QA API
export const getAnswer = async (question) => {
  try {
    const response = await api.post("rag/query", {
      question: question,
    });
    return response.data;
  } catch (error) {
    console.error(
      "Error getting answer:",
      error.response?.data?.detail || error.message
    );
    throw error;
  }
};
