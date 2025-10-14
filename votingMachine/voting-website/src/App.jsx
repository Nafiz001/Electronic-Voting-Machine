import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navigation from './components/Navigation';
import Dashboard from './pages/Dashboard';
import VoterList from './pages/VoterList';
import Candidates from './pages/Candidates';
import VoteCount from './pages/VoteCount';
import VoteStatistics from './pages/VoteStatistics';
import './App.css';

function App() {
  return (
    <Router>
      <div className="app-container">
        <Navigation />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/voters" element={<VoterList />} />
            <Route path="/candidates" element={<Candidates />} />
            <Route path="/vote-count" element={<VoteCount />} />
            <Route path="/statistics" element={<VoteStatistics />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
