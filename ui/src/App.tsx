import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import Dashboard from './pages/Dashboard'

function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 flex items-center justify-center">
      <div className="max-w-4xl mx-auto px-4 text-center">
        <h1 className="text-6xl font-bold text-white mb-6">
          Welcome to 
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400">
            {" "}SaaS Factory
          </span>
        </h1>
        <p className="text-xl text-gray-300 mb-8 max-w-2xl mx-auto">
          Your AI-powered platform for building scalable SaaS applications with React, FastAPI, and Google Cloud.
        </p>
        <div className="space-y-4">
          <button className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-semibold py-4 px-8 rounded-full text-lg transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105 block mx-auto">
            It works 🚀
          </button>
          <Link 
            to="/dashboard"
            className="inline-block bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 text-white font-semibold py-3 px-6 rounded-full text-base transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105"
          >
            View Agent Dashboard →
          </Link>
        </div>
      </div>
    </div>
  )
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/dashboard" element={<Dashboard />} />
      </Routes>
    </Router>
  )
}

export default App
