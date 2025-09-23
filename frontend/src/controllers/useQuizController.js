import { useState } from 'react'
import quizService from '../services/quizService'
import mockQuiz from '../data/mockQuiz'
import { toast } from 'react-toastify'

export default function useQuizController() {
  const [currentStep, setCurrentStep] = useState('input') // input | quiz | results
  const [isLoading, setIsLoading] = useState(false)
  const [quiz, setQuiz] = useState(null)
  const [results, setResults] = useState(null)

  const createQuiz = async (videoUrl) => {
    setIsLoading(true)
    toast.info('Analyzing video content...')
    try {
      const generated = await quizService.generateQuiz(videoUrl)
      // ensure structure
      const normalized = generated || mockQuiz
      setQuiz(normalized)
      setCurrentStep('quiz')
      toast.success('Quiz generated successfully!')
    } catch (err) {
      console.error(err)
      toast.error('Failed to generate quiz. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const submitQuiz = (answers) => {
    if (!quiz) return
    const totalQuestions = quiz.questions.length
    let correctAnswers = 0
    quiz.questions.forEach(q => {
      if (answers[q.id] === q.correctAnswer) correctAnswers++
    })
    const percentage = Math.round((correctAnswers / totalQuestions) * 100)
    const res = { score: correctAnswers, totalQuestions, percentage, answers, quiz }
    setResults(res)
    setCurrentStep('results')
    toast.success(`Quiz completed! You scored ${percentage}%`)
  }

  const retakeQuiz = () => {
    setResults(null)
    setCurrentStep('quiz')
  }

  const startOver = () => {
    setResults(null)
    setQuiz(null)
    setCurrentStep('input')
  }

  return {
    currentStep,
    isLoading,
    quiz,
    results,
    createQuiz,
    submitQuiz,
    retakeQuiz,
    startOver
  }
}
