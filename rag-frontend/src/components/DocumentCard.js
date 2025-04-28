import React from "react";

const DocumentCard = ({ title, description }) => {
  return (
    <div className="bg-white rounded-lg shadow p-4 hover:shadow-lg transition duration-200">
      <h3 className="text-lg font-semibold text-gray-800">{title}</h3>
      <p className="text-sm text-gray-600">{description}</p>
    </div>
  );
};

export default DocumentCard;