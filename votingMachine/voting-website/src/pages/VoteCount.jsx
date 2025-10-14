import { useState, useEffect } from 'react';
import { Trophy, Vote, TrendingUp, Crown, Circle, RefreshCw } from 'lucide-react';
import firebaseService from '../services/firebase';
import './VoteCount.css';

const VoteCount = () => {
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [totalVotes, setTotalVotes] = useState(0);

  // Candidate info mapping
  const candidateInfo = {
    'Alice': {
      party: 'Progressive Party',
      symbol: '🌟',
      color: '#3b82f6',
    },
    'Bob': {
      party: 'Unity Party',
      symbol: '🏛️',
      color: '#ef4444',
    },
    'Charlie': {
      party: 'Reform Party',
      symbol: '🚀',
      color: '#10b981',
    },
  };

  const fetchVoteCounts = async () => {
    setLoading(true);
    try {
      const voteCounts = await firebaseService.getVoteCounts();
      
      // Map the vote counts with additional candidate info
      const candidatesWithInfo = voteCounts.map((candidate, index) => ({
        id: index + 1,
        name: candidate.name,
        party: candidateInfo[candidate.name]?.party || 'Independent',
        symbol: candidateInfo[candidate.name]?.symbol || '🗳️',
        votes: candidate.votes,
        percentage: candidate.percentage,
        color: candidateInfo[candidate.name]?.color || '#6b7280',
        voters: candidate.voters
      }));

      setCandidates(candidatesWithInfo);
      setTotalVotes(candidatesWithInfo.reduce((sum, candidate) => sum + candidate.votes, 0));
    } catch (error) {
      console.error('Error fetching vote counts:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchVoteCounts();
    // Auto-refresh every 15 seconds for live updates
    const interval = setInterval(fetchVoteCounts, 15000);
    return () => clearInterval(interval);
  }, []);

  const leader = candidates.length > 0 ? candidates[0] : null;

  return (
    <div className="vote-count-page">
      <div className="page-header">
        <div>
          <h1>Vote Count</h1>
          <p>Real-time vote tracking and results</p>
        </div>
        <button 
          className="refresh-btn"
          onClick={fetchVoteCounts}
          disabled={loading}
        >
          <RefreshCw className={loading ? 'spinning' : ''} size={20} />
          Refresh
        </button>
      </div>

      <div className="count-summary">
        <div className="summary-card leading">
          <Trophy className="summary-icon" size={48} />
          <div>
            <h3>Leading Candidate</h3>
            {loading ? (
              <>
                <p className="leader-name">Loading...</p>
                <p className="leader-party">-</p>
              </>
            ) : leader ? (
              <>
                <p className="leader-name">{leader.name}</p>
                <p className="leader-party">{leader.party}</p>
              </>
            ) : (
              <>
                <p className="leader-name">No votes yet</p>
                <p className="leader-party">-</p>
              </>
            )}
          </div>
        </div>
        <div className="summary-card total-votes">
          <Vote className="summary-icon" size={48} />
          <div>
            <h3>Total Votes</h3>
            <p className="total-number">{loading ? '...' : totalVotes.toLocaleString()}</p>
          </div>
        </div>
        <div className="summary-card lead-margin">
          <TrendingUp className="summary-icon" size={48} />
          <div>
            <h3>Lead Margin</h3>
            {loading ? (
              <>
                <p className="margin-number">... votes</p>
                <p className="margin-percent">...%</p>
              </>
            ) : leader && candidates.length > 1 ? (
              <>
                <p className="margin-number">{leader.votes - candidates[1].votes} votes</p>
                <p className="margin-percent">{(leader.percentage - candidates[1].percentage).toFixed(1)}%</p>
              </>
            ) : (
              <>
                <p className="margin-number">0 votes</p>
                <p className="margin-percent">0%</p>
              </>
            )}
          </div>
        </div>
      </div>

      <div className="candidates-results">
        {loading ? (
          <div className="loading-message">
            <RefreshCw className="spinning" size={32} />
            <p>Loading vote counts...</p>
          </div>
        ) : candidates.length === 0 ? (
          <div className="no-votes-message">
            <Vote size={48} />
            <p>No votes cast yet</p>
          </div>
        ) : (
          candidates.map((candidate, index) => (
            <div key={candidate.id} className="candidate-card">
              <div className="candidate-rank">
                {index === 0 && candidate.votes > 0 && <Crown className="crown" size={28} color="#ffd700" />}
                <span className="rank-number">#{index + 1}</span>
              </div>
              <div className="candidate-symbol" style={{ backgroundColor: `${candidate.color}20` }}>
                <span style={{ fontSize: '3rem' }}>{candidate.symbol}</span>
              </div>
              <div className="candidate-info">
                <h3>{candidate.name}</h3>
                <p className="party-name">{candidate.party}</p>
              </div>
              <div className="vote-stats">
                <div className="vote-count">
                  <span className="count-number">{candidate.votes.toLocaleString()}</span>
                  <span className="count-label">votes</span>
                </div>
                <div className="vote-percentage" style={{ color: candidate.color }}>
                  {candidate.percentage.toFixed(1)}%
                </div>
              </div>
              <div className="progress-bar-container">
                <div
                  className="progress-bar"
                  style={{
                    width: `${candidate.percentage}%`,
                    backgroundColor: candidate.color,
                  }}
                ></div>
              </div>
            </div>
          ))
        )}
      </div>

      <div className="live-indicator">
        <Circle className="pulse" size={12} fill="currentColor" />
        <span>Live Updates</span>
      </div>
    </div>
  );
};

export default VoteCount;
