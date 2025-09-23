import React, { useState } from 'react';
import { toast } from 'react-toastify';
import Header from '../components/Header';
import Footer from '../components/Footer';
import YouTubeInput from '../components/YoutubeInput';
import QuizInterface from '../components/QuizInterface';
import QuizReport from '../components/QuizReport';

const Home = () => {
  const [currentStep, setCurrentStep] = useState('input'); // 'input', 'quiz', 'report'
  const [isLoading, setIsLoading] = useState(false);
  const [quiz, setQuiz] = useState(null);
  const [userAnswers, setUserAnswers] = useState({});

  const handleGenerateQuiz = async (url) => {
    setIsLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/youtube_link/", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({
          youtube_url: url,
          target_lang: "en",
          difficulty: "medium"
        })
      });

      if (!response.ok) {
        throw new Error("Failed to fetch quiz");
      }

      const data = await response.json();
      console.log("Backend response:", data);

      // ✅ backend returns { transcript, summary, quiz }
      const formattedQuiz = {
        title: "Generated Quiz",
        questions: (Array.isArray(data.quiz) ? data.quiz : []).map((q, idx) => ({
          question: q.question || `Question ${idx + 1}`,
          options: q.options || [],
          correctAnswer: q.correctAnswer ?? 0,
          explanation: q.explanation || ""
        }))
      };

      if (!formattedQuiz.questions.length) {
        throw new Error("No quiz questions returned from backend");
      }

      setQuiz(formattedQuiz);
      setCurrentStep("quiz");
      toast.success("Quiz generated successfully!");
    } catch (error) {
      console.error(error);
      toast.error("Failed to generate quiz. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmitQuiz = (answers) => {
    setUserAnswers(answers);
    setCurrentStep('report');
    toast.success('Quiz submitted successfully!');
  };

  const handleRetakeQuiz = () => {
    setUserAnswers({});
    setCurrentStep('quiz');
  };

  const handleStartOver = () => {
    setCurrentStep('input');
    setQuiz(null);
    setUserAnswers({});
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <Header />
      
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {currentStep === 'input' && (
          <div className="text-center mb-12">
            <h1 className="text-4xl md:text-5xl font-bold text-slate-900 mb-4 font-inter">
              Transform YouTube Videos into
              <span className="text-emerald-600"> Interactive Quizzes</span>
            </h1>
            <p className="text-xl text-slate-600 mb-8 max-w-2xl mx-auto font-roboto">
              Generate engaging quizzes from any YouTube video and track your learning progress with detailed analytics.
            </p>
            <YouTubeInput onGenerateQuiz={handleGenerateQuiz} isLoading={isLoading} />
          </div>
        )}

        {currentStep === 'quiz' && quiz && (
          <div>
            <div className="text-center mb-8">
              <button
                onClick={handleStartOver}
                className="text-emerald-600 hover:text-emerald-700 font-medium font-inter"
              >
                ← Start Over
              </button>
            </div>
            <QuizInterface quiz={quiz} onSubmitQuiz={handleSubmitQuiz} />
          </div>
        )}

        {currentStep === 'report' && quiz && (
          <div>
            <div className="text-center mb-8">
              <button
                onClick={handleStartOver}
                className="text-emerald-600 hover:text-emerald-700 font-medium font-inter"
              >
                ← Create New Quiz
              </button>
            </div>
            <QuizReport 
              quiz={quiz} 
              answers={userAnswers} 
              onRetakeQuiz={handleRetakeQuiz}
            />
          </div>
        )}
      </main>

      <Footer />
    </div>
  );
};

export default Home;
