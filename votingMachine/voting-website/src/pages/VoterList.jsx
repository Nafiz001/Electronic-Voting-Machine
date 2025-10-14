import { useState, useEffect } from 'react';
import { Search, CheckCircle, Clock, Users, RefreshCw } from 'lucide-react';
import firebaseService from '../services/firebase';
import './VoterList.css';

const VoterList = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [voters, setVoters] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchVoters = async () => {
    setLoading(true);
    try {
      const votersData = await firebaseService.getVotersWithStatus();
      setVoters(votersData);
    } catch (error) {
      console.error('Error fetching voters:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchVoters();
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchVoters, 30000);
    return () => clearInterval(interval);
  }, []);

  const filteredVoters = voters.filter((voter) => {
    const matchesSearch =
      voter.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      voter.id.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesFilter =
      filterStatus === 'all' ||
      (filterStatus === 'voted' && voter.hasVoted) ||
      (filterStatus === 'not-voted' && !voter.hasVoted);

    return matchesSearch && matchesFilter;
  });

  const votedCount = voters.filter(v => v.hasVoted).length;
  const notVotedCount = voters.length - votedCount;

  return (
    <div className="voter-list-page">
      <div className="page-header">
        <div>
          <h1>Voter List</h1>
          <p>Manage and track registered voters</p>
        </div>
        <button 
          className="refresh-btn"
          onClick={fetchVoters}
          disabled={loading}
        >
          <RefreshCw className={loading ? 'spinning' : ''} size={20} />
          Refresh
        </button>
      </div>

      <div className="voter-stats">
        <div className="mini-stat voted">
          <CheckCircle className="mini-stat-icon" size={32} />
          <div>
            <h3>{votedCount}</h3>
            <p>Voted</p>
          </div>
        </div>
        <div className="mini-stat pending">
          <Clock className="mini-stat-icon" size={32} />
          <div>
            <h3>{notVotedCount}</h3>
            <p>Not Voted</p>
          </div>
        </div>
        <div className="mini-stat total">
          <Users className="mini-stat-icon" size={32} />
          <div>
            <h3>{voters.length}</h3>
            <p>Total Voters</p>
          </div>
        </div>
      </div>

      <div className="voter-controls">
        <div className="search-box">
          <Search className="search-icon" size={20} />
          <input
            type="text"
            placeholder="Search by name or voter ID..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <div className="filter-buttons">
          <button
            className={`filter-btn ${filterStatus === 'all' ? 'active' : ''}`}
            onClick={() => setFilterStatus('all')}
          >
            All
          </button>
          <button
            className={`filter-btn ${filterStatus === 'voted' ? 'active' : ''}`}
            onClick={() => setFilterStatus('voted')}
          >
            Voted
          </button>
          <button
            className={`filter-btn ${filterStatus === 'not-voted' ? 'active' : ''}`}
            onClick={() => setFilterStatus('not-voted')}
          >
            Not Voted
          </button>
        </div>
      </div>

      <div className="voter-table-container">
        <table className="voter-table">
          <thead>
            <tr>
              <th>Voter ID</th>
              <th>Name</th>
              <th>Age</th>
              <th>District</th>
              <th>Status</th>
              <th>Voted At</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan="6" className="loading-cell">
                  <RefreshCw className="spinning" size={20} />
                  Loading voters...
                </td>
              </tr>
            ) : filteredVoters.length === 0 ? (
              <tr>
                <td colSpan="6" className="no-data-cell">
                  No voters found
                </td>
              </tr>
            ) : (
              filteredVoters.map((voter) => (
                <tr key={voter.id}>
                  <td className="voter-id">{voter.id}</td>
                  <td className="voter-name">{voter.name}</td>
                  <td>-</td>
                  <td>-</td>
                  <td>
                    <span className={`status-badge ${voter.hasVoted ? 'voted' : 'pending'}`}>
                      {voter.hasVoted ? (
                        <>
                          <CheckCircle size={16} /> Voted for {voter.votedFor}
                        </>
                      ) : (
                        <>
                          <Clock size={16} /> Pending
                        </>
                      )}
                    </span>
                  </td>
                  <td>{voter.votedAt || '-'}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default VoterList;
