import React from "react";
import Layout from "../components/Layout";

const Dashboard = () => {
  return (
    <Layout>
      <h2 className="text-2xl font-bold text-gray-800 mb-4">
        Welcome to the RAG Q&A System
      </h2>
      <p className="text-gray-600">
        Use the sidebar to manage documents or ask questions.
      </p>
    </Layout>
  );
};

export default Dashboard;
