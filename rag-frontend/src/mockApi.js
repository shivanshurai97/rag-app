export const getDocuments = async () => [
  { id: 1, title: "Doc 1", description: "First doc" },
  { id: 2, title: "Doc 2", description: "Second doc" },
];

export const getAnswer = async (question) => {
  return {
    answer: `Mocked response for: "${question}"`,
  };
};