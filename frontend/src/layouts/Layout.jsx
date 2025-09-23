import React from 'react'
import Header from '../components/Header'
import Footer from '../components/Footer'
import { AnimatePresence, motion } from 'framer-motion'

export default function Layout({ children }) {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <AnimatePresence mode="wait">
        <motion.div
          key={location.pathname}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -8 }}
          transition={{ duration: 0.35 }}
          className="flex-1"
        >
          {children}
        </motion.div>
      </AnimatePresence>
      <Footer />
    </div>
  )
}
