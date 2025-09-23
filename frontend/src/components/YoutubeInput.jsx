import React, { useState } from 'react';
    import { Link, Loader2 } from 'lucide-react';
    import { motion } from 'framer-motion';

    const YouTubeInput = ({ onGenerateQuiz, isLoading }) => {
      const [url, setUrl] = useState('');
      const [error, setError] = useState('');

      const validateYouTubeUrl = (url) => {
        const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/.+/;
        return youtubeRegex.test(url);
      };

      const handleSubmit = (e) => {
        e.preventDefault();
        setError('');

        if (!url.trim()) {
          setError('Please enter a YouTube URL');
          return;
        }

        if (!validateYouTubeUrl(url)) {
          setError('Please enter a valid YouTube URL');
          return;
        }

        onGenerateQuiz(url);
      };

      return (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="bg-white rounded-2xl shadow-lg p-8 border border-slate-200"
        >
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-emerald-100 rounded-full mb-4">
              <Link className="w-8 h-8 text-emerald-600" />
            </div>
            <h2 className="text-2xl font-bold text-slate-900 mb-2 font-inter">
              Generate Quiz from YouTube
            </h2>
            <p className="text-slate-600 font-roboto">
              Paste a YouTube video URL to create an interactive quiz
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="youtube-url" className="block text-sm font-medium text-slate-700 mb-2 font-inter">
                YouTube Video URL
              </label>
              <input
                id="youtube-url"
                type="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://www.youtube.com/watch?v=..."
                className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-colors font-roboto"
                disabled={isLoading}
              />
              {error && (
                <p className="mt-2 text-sm text-red-600 font-roboto" role="alert">
                  {error}
                </p>
              )}
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-emerald-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-emerald-700 focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2 font-inter"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>Generating Quiz...</span>
                </>
              ) : (
                <span>Create Quiz</span>
              )}
            </button>
          </form>
        </motion.div>
      );
    };

    export default YouTubeInput;