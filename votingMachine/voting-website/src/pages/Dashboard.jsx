import { useState, useEffect } from 'react';
import { Users, CheckCircle, Target, TrendingUp, Lock, RefreshCw } from 'lucide-react';
import firebaseService from '../services/firebase';
import './Dashboard.css';

const Dashboard = () => {
  const [stats, setStats] = useState([
    { label: 'Total Voters', value: '0', icon: Users, color: '#2563eb' },
    { label: 'Votes Cast', value: '0', icon: CheckCircle, color: '#059669' },
    { label: 'Candidates', value: '3', icon: Target, color: '#0891b2' },
    { label: 'Turnout Rate', value: '0%', icon: TrendingUp, color: '#4b5563' },
  ]);
  const [loading, setLoading] = useState(true);

  const fetchStats = async () => {
    setLoading(true);
    try {
      const data = await firebaseService.getDashboardStats();
      setStats([
        { label: 'Total Voters', value: data.totalVoters.toString(), icon: Users, color: '#2563eb' },
        { label: 'Votes Cast', value: data.totalVotes.toString(), icon: CheckCircle, color: '#059669' },
        { label: 'Candidates', value: data.candidates.toString(), icon: Target, color: '#0891b2' },
        { label: 'Turnout Rate', value: `${data.turnoutRate}%`, icon: TrendingUp, color: '#4b5563' },
      ]);
    } catch (error) {
      console.error('Error fetching dashboard stats:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchStats, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="dashboard">
      <div className="page-header">
        <div>
          <h1>Dashboard</h1>
          <p>Overview of voting system statistics</p>
        </div>
        <button 
          className="refresh-btn"
          onClick={fetchStats}
          disabled={loading}
        >
          <RefreshCw className={loading ? 'spinning' : ''} size={20} />
          Refresh
        </button>
      </div>

      <div className="stats-grid">
        {stats.map((stat, index) => {
          const IconComponent = stat.icon;
          return (
            <div key={index} className="stat-card" style={{ borderLeftColor: stat.color }}>
              <IconComponent size={40} color={stat.color} strokeWidth={2} />
              <div className="stat-info">
                <h3>{stat.value}</h3>
                <p>{stat.label}</p>
              </div>
            </div>
          );
        })}
      </div>

      <div className="dashboard-content">
        <div className="info-card">
          <h2><Lock className="inline-icon" size={28} /> Secure Voting System</h2>
          <p>
            Welcome to the Voting Machine Dashboard. This system provides real-time
            monitoring of the voting process, voter management, and comprehensive
            statistics analysis.
          </p>
          <ul>
            <li><CheckCircle size={18} className="list-icon" /> Real-time vote tracking</li>
            <li><CheckCircle size={18} className="list-icon" /> Secure voter authentication</li>
            <li><CheckCircle size={18} className="list-icon" /> Comprehensive analytics</li>
            <li><CheckCircle size={18} className="list-icon" /> Transparent counting process</li>
          </ul>
        </div>

      </div>
    </div>
  );
};

export default Dashboard;
