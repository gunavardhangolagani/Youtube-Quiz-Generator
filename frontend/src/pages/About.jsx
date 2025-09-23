// src/pages/About.jsx
import React from "react";
import Layout from "../components/Layout";

export default function About() {
  return (
    <Layout>
    <div className="max-w-4xl mx-auto py-12 text-center">
      <h1 className="text-4xl font-bold">About This Project</h1>
      <p className="mt-4 text-lg">
        This YouTube Quiz Generator is a powerful tool designed to help you
        quickly create interactive quizzes from any YouTube video. Just paste a
        URL, and our system will generate a quiz based on the video's content,
        complete with detailed reports to track your learning.
      </p>
    </div>
    </Layout>
  );
}
