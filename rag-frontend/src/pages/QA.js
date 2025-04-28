import { useState } from "react";
import { getAnswer } from "../api/api";
import Layout from "../components/Layout";
import { handleError } from "../utils/errorHandler";

function QA() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!question.trim()) {
      handleError(new Error("Please enter a question"));
      return;
    }

    setIsLoading(true);
    setAnswer(""); // Clear previous answer while loading
    try {
      const res = await getAnswer(question);
      setAnswer(res.answer);
    } catch (error) {
      handleError(error);
    } finally {
      setIsLoading(false);
    }
  };

  const LoadingIndicator = () => (
    <div className="mt-8 p-4 bg-gray-50 rounded-lg">
      <h2 className="text-lg font-semibold mb-2 flex items-center">
        Thinking
        <span className="inline-flex ml-2">
          <span className="animate-bounce mx-0.5 h-1.5 w-1.5 bg-blue-600 rounded-full"></span>
          <span
            className="animate-bounce mx-0.5 h-1.5 w-1.5 bg-blue-600 rounded-full"
            style={{ animationDelay: "0.2s" }}
          ></span>
          <span
            className="animate-bounce mx-0.5 h-1.5 w-1.5 bg-blue-600 rounded-full"
            style={{ animationDelay: "0.4s" }}
          ></span>
        </span>
      </h2>
      <div className="flex items-center space-x-2 text-gray-500">
        <div className="animate-spin h-4 w-4 border-2 border-blue-500 rounded-full border-t-transparent"></div>
        <span>Processing your question, please wait...</span>
      </div>
    </div>
  );

  return (
    <Layout>
      <div className="max-w-3xl mx-auto p-4">
        <h1 className="text-2xl font-bold mb-6 text-gray-800">
          Ask a Question
        </h1>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <textarea
              className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Enter your question..."
              rows={4}
              disabled={isLoading}
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className={`w-full py-2 px-4 rounded-lg text-white font-medium ${
              isLoading
                ? "bg-blue-400 cursor-not-allowed"
                : "bg-blue-500 hover:bg-blue-600"
            }`}
          >
            {isLoading ? "Getting Answer..." : "Get Answer"}
          </button>
        </form>

        {isLoading ? (
          <LoadingIndicator />
        ) : (
          answer && (
            <div className="mt-8 p-4 bg-gray-50 rounded-lg">
              <h2 className="text-lg font-semibold mb-2">Answer:</h2>
              <p className="whitespace-pre-wrap">{answer}</p>
            </div>
          )
        )}
      </div>
    </Layout>
  );
}

export default QA;
