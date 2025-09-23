const mockQuiz = {
  id: 'quiz-1',
  title: 'Understanding React Hooks',
  videoUrl: 'https://youtube.com/watch?v=example',
  questions: [
    {
      id: 'q1',
      question: 'What is the primary purpose of the useState hook in React?',
      options: [
        'To manage component lifecycle',
        'To manage state in functional components',
        'To handle side effects',
        'To optimize performance'
      ],
      correctAnswer: 1,
      explanation: 'useState is designed to manage state in functional components.'
    },
    {
      id: 'q2',
      question: 'Which hook is used to perform side effects in React functional components?',
      options: ['useState', 'useContext', 'useEffect', 'useReducer'],
      correctAnswer: 2,
      explanation: 'useEffect is used for side effects.'
    },
    {
      id: 'q3',
      question: 'What does the dependency array in useEffect control?',
      options: ['The return value of the effect', 'When the effect runs', 'The cleanup function', 'The component props'],
      correctAnswer: 1,
      explanation: 'The dependency array controls when the effect runs again.'
    },
    {
      id: 'q4',
      question: 'How do you prevent a useEffect from running on every render?',
      options: ['Use an empty dependency array []', 'Use useState instead', 'Return false from the effect', 'Use useCallback'],
      correctAnswer: 0,
      explanation: 'An empty dependency array runs the effect only once (after initial render).'
    },
    {
      id: 'q5',
      question: 'What is the purpose of the cleanup function in useEffect?',
      options: ['To initialize state', 'To prevent memory leaks and clean up subscriptions', 'To update component props', 'To trigger re-renders'],
      correctAnswer: 1,
      explanation: 'Cleanup prevents memory leaks by cleaning subscriptions/timers.'
    }
  ]
}

export default mockQuiz
