import React, { useEffect, useState } from 'react';
import { Trophy, Target, Clock, RotateCcw, CheckCircle, XCircle } from 'lucide-react';
import { motion } from 'framer-motion';
import axios from 'axios';

const QuizReport = ({ quiz, answers, onRetakeQuiz }) => {
  const [results, setResults] = useState(null);

  useEffect(() => {
    const fetchResults = async () => {
      try {
        // POST to backend verify_answers route
        const res = await axios.post('http://localhost:8000/verify_answers', {
          quiz: quiz.questions, // original quiz
          user_answers: Object.fromEntries(
            Object.entries(answers).map(([k, v]) => [String(k), v])
          ),
        });

        // Ensure res.data is always in expected format
        if (
          res.data &&
          typeof res.data === 'object' &&
          Array.isArray(res.data.details)
        ) {
          setResults(res.data);
        } else {
          console.error('Invalid response format from backend', res.data);
          setResults({
            details: [],
            score: 0,
            total: quiz.questions.length,
            percentage: 0,
          });
        }
      } catch (error) {
        console.error('Error fetching results:', error);
        setResults({
          details: [],
          score: 0,
          total: quiz.questions.length,
          percentage: 0,
        });
      }
    };

    fetchResults();
  }, [quiz, answers]);

  if (!results) return <div>Loading results...</div>;

  const getScoreColor = (percentage) => {
    if (percentage >= 80) return 'text-emerald-600';
    if (percentage >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBg = (percentage) => {
    if (percentage >= 80) return 'bg-emerald-100';
    if (percentage >= 60) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-8"
    >
      {/* Score Overview */}
      <div className="bg-white rounded-2xl shadow-lg p-8 border border-slate-200">
        <div className="text-center mb-8">
          <div
            className={`inline-flex items-center justify-center w-20 h-20 rounded-full mb-4 ${getScoreBg(
              results.percentage
            )}`}
          >
            <Trophy className={`w-10 h-10 ${getScoreColor(results.percentage)}`} />
          </div>
          <h2 className="text-3xl font-bold text-slate-900 mb-2 font-inter">
            Quiz Complete!
          </h2>
          <p className="text-slate-600 font-roboto">Here's how you performed</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="text-center p-6 bg-slate-50 rounded-xl">
            <Target className="w-8 h-8 text-slate-600 mx-auto mb-2" />
            <div
              className={`text-2xl font-bold mb-1 ${getScoreColor(
                results.percentage
              )} font-inter`}
            >
              {results.percentage}%
            </div>
            <div className="text-sm text-slate-600 font-roboto">Overall Score</div>
          </div>

          <div className="text-center p-6 bg-slate-50 rounded-xl">
            <CheckCircle className="w-8 h-8 text-emerald-600 mx-auto mb-2" />
            <div className="text-2xl font-bold text-slate-900 mb-1 font-inter">
              {results.score}/{results.total}
            </div>
            <div className="text-sm text-slate-600 font-roboto">Correct Answers</div>
          </div>

          <div className="text-center p-6 bg-slate-50 rounded-xl">
            <Clock className="w-8 h-8 text-sky-500 mx-auto mb-2" />
            <div className="text-2xl font-bold text-slate-900 mb-1 font-inter">
              {quiz.questions.length}
            </div>
            <div className="text-sm text-slate-600 font-roboto">Total Questions</div>
          </div>
        </div>

        <div className="text-center">
          <button
            onClick={onRetakeQuiz}
            className="bg-emerald-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-emerald-700 focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 transition-colors inline-flex items-center space-x-2 font-inter"
          >
            <RotateCcw className="w-4 h-4" />
            <span>Retake Quiz</span>
          </button>
        </div>
      </div>

      {/* Detailed Results */}
      <div className="bg-white rounded-2xl shadow-lg p-8 border border-slate-200">
        <h3 className="text-xl font-bold text-slate-900 mb-6 font-inter">
          Detailed Results
        </h3>

        <div className="space-y-6">
          {results.details.map((detail, index) => (
            <div
              key={index}
              className={`p-6 rounded-xl border-2 ${
                detail.isCorrect
                  ? 'border-emerald-200 bg-emerald-50'
                  : 'border-red-200 bg-red-50'
              }`}
            >
              <div className="flex items-start space-x-3 mb-4">
                {detail.isCorrect ? (
                  <CheckCircle className="w-6 h-6 text-emerald-600 flex-shrink-0 mt-0.5" />
                ) : (
                  <XCircle className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" />
                )}
                <div className="flex-1">
                  <h4 className="font-semibold text-slate-900 mb-2 font-inter">
                    Question {index + 1}: {detail.question}
                  </h4>

                  <div className="space-y-2 text-sm font-roboto">
                    <div>
                      <span className="font-medium text-slate-700">Your answer: </span>
                      <span
                        className={
                          detail.isCorrect ? 'text-emerald-700' : 'text-red-700'
                        }
                      >
                        {detail.userAnswer ?? 'No answer'}
                      </span>
                    </div>

                    {!detail.isCorrect && (
                      <div>
                        <span className="font-medium text-slate-700">
                          Correct answer:{' '}
                        </span>
                        <span className="text-emerald-700">
                          {detail.correctAnswer}
                        </span>
                      </div>
                    )}

                    <div className="mt-3 p-3 bg-white rounded-lg">
                      <span className="font-medium text-slate-700">
                        Explanation:{' '}
                      </span>
                      <span className="text-slate-600">{detail.explanation}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </motion.div>
  );
};

export default QuizReport;
