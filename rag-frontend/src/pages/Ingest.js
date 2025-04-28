import { useState, useEffect } from "react";
import { getDocuments, uploadDocument, selectDocuments } from "../api/api";
import Layout from "../components/Layout";
import { handleError, showSuccess } from "../utils/errorHandler";

function Ingest() {
  const [docs, setDocs] = useState([]);
  const [file, setFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);

  const fetchDocuments = async () => {
    try {
      setIsLoading(true);
      const data = await getDocuments();
      setDocs(data);
    } catch (error) {
      handleError(error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setUploadStatus("");
    }
  };

  const handleUpload = async () => {
    if (!file) {
      handleError(new Error("Please select a file first."));
      return;
    }

    try {
      setIsUploading(true);
      setUploadStatus("Uploading...");
      await uploadDocument(file);
      showSuccess("Document uploaded successfully!");
      setFile(null);
      setUploadStatus("");
      // Reset the file input by clearing its value
      const fileInput = document.querySelector('input[type="file"]');
      if (fileInput) fileInput.value = "";
      fetchDocuments(); // Refresh the document list
    } catch (error) {
      handleError(error);
    } finally {
      setIsUploading(false);
      setUploadStatus("");
    }
  };

  const handleToggleQA = async (docId, currentStatus) => {
    try {
      setIsLoading(true);
      await selectDocuments([docId]);
      showSuccess(`Document ${currentStatus ? "disabled" : "enabled"} for QA`);
      fetchDocuments(); // Refresh the document list
    } catch (error) {
      handleError(error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Layout>
      <div className="p-4">
        <h1 className="text-2xl font-bold mb-4">Ingest Documents</h1>

        <div className="mb-6">
          <input
            type="file"
            className="mb-2 border p-2 w-full"
            onChange={handleFileChange}
            disabled={isUploading}
          />

          <button
            onClick={handleUpload}
            className={`px-4 py-2 rounded mb-2 ${
              isUploading
                ? "bg-gray-400 cursor-not-allowed"
                : "bg-green-500 hover:bg-green-600"
            } text-white`}
            disabled={!file || isUploading}
          >
            {isUploading ? "Uploading..." : "Upload Document"}
          </button>

          {uploadStatus && (
            <div className="text-red-600 text-sm">{uploadStatus}</div>
          )}
        </div>

        {isLoading ? (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto"></div>
            <p className="mt-2 text-gray-600">Loading documents...</p>
          </div>
        ) : docs.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            No documents uploaded yet
          </div>
        ) : (
          <ul className="space-y-2">
            {docs.map((doc) => (
              <li
                key={doc.id}
                className="p-3 border rounded-lg bg-white shadow-sm"
              >
                <div className="flex justify-between items-center">
                  <div>
                    <h3 className="font-medium">{doc.name}</h3>
                    <p className="text-sm text-gray-500">
                      Uploaded on{" "}
                      {new Date(doc.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <button
                    onClick={() => handleToggleQA(doc.id, doc.enabled_for_qa)}
                    className={`px-3 py-1 text-sm rounded-full transition-colors ${
                      doc.enabled_for_qa
                        ? "bg-green-100 text-green-800 hover:bg-green-200"
                        : "bg-gray-100 text-gray-800 hover:bg-gray-200"
                    }`}
                  >
                    {doc.enabled_for_qa
                      ? "Enabled for QA"
                      : "Click to Enable QA"}
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </Layout>
  );
}

export default Ingest;
