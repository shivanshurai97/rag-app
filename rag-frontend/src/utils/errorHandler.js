import { toast } from "react-toastify";

const toastConfig = {
  position: "top-center",
  autoClose: 5000,
  hideProgressBar: false,
  closeOnClick: true,
  pauseOnHover: true,
  draggable: true,
  progress: undefined,
  theme: "light",
};

export const handleError = (error) => {
  console.log("Error in handleError:", error); // Debug log

  // Handle different error formats
  let errorMessage = "An unexpected error occurred";

  // Handle axios error response
  if (error.response?.data) {
    const errorData = error.response.data;
    console.log("Error data:", errorData); // Debug log

    // Handle error with code and message
    if (errorData.error?.code && errorData.error?.message) {
      errorMessage = errorData.error.message;
    }
    // Handle error with detail
    else if (errorData.detail) {
      errorMessage = errorData.detail;
    }
    // Handle error with message
    else if (errorData.message) {
      errorMessage = errorData.message;
    }
  }
  // Handle regular error
  else if (error.message) {
    errorMessage = error.message;
  }

  console.log("Final error message:", errorMessage); // Debug log

  // Check for specific error types
  if (
    error.response?.data?.error?.code === "VALIDATION_ERROR" ||
    error.response?.data?.type === "ValidationError"
  ) {
    toast.error(`Validation Error: ${errorMessage}`, toastConfig);
  } else if (error.response?.data?.type === "DatabaseError") {
    toast.error(`Database Error: ${errorMessage}`, toastConfig);
  } else if (error.response?.data?.type === "NotFoundError") {
    toast.error(`Not Found: ${errorMessage}`, toastConfig);
  } else if (error.response?.data?.type === "ConflictError") {
    toast.error(`Conflict: ${errorMessage}`, toastConfig);
  } else if (error.response?.data?.type === "FileError") {
    toast.error(`File Error: ${errorMessage}`, toastConfig);
  } else {
    toast.error(errorMessage, toastConfig);
  }
};

export const showSuccess = (message) => {
  toast.success(message, toastConfig);
};
