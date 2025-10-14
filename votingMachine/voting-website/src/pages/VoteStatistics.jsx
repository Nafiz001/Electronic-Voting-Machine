import { useState, useEffect } from 'react';
import { BarChart, Bar, PieChart, Pie, Cell, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TrendingUp, Zap, Award, Clock, Lightbulb, Users as UsersIcon, MapPin, RefreshCw } from 'lucide-react';
import firebaseService from '../services/firebase';
import './VoteStatistics.css';

const VoteStatistics = () => {
  const [candidateData, setCandidateData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    turnoutRate: '0%',
    totalVotes: 0,
    totalVoters: 0,
    leadingCandidate: 'None'
  });

  const fetchStatistics = async () => {
    setLoading(true);
    try {
      const [voteCounts, dashboardStats] = await Promise.all([
        firebaseService.getVoteCounts(),
        firebaseService.getDashboardStats()
      ]);

      // Prepare candidate data for charts
      const chartData = voteCounts.map(candidate => ({
        name: candidate.name,
        votes: candidate.votes,
        fill: candidate.name === 'Alice' ? '#3b82f6' : 
              candidate.name === 'Bob' ? '#ef4444' : '#10b981'
      }));

      setCandidateData(chartData);
      setStats({
        turnoutRate: `${dashboardStats.turnoutRate}%`,
        totalVotes: dashboardStats.totalVotes,
        totalVoters: dashboardStats.totalVoters,
        leadingCandidate: chartData.length > 0 ? chartData[0].name : 'None'
      });
    } catch (error) {
      console.error('Error fetching statistics:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatistics();
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchStatistics, 30000);
    return () => clearInterval(interval);
  }, []);

  const hourlyData = [
    { hour: '8 AM', votes: 45 },
    { hour: '9 AM', votes: 89 },
    { hour: '10 AM', votes: 156 },
    { hour: '11 AM', votes: 234 },
    { hour: '12 PM', votes: 198 },
    { hour: '1 PM', votes: 170 },
  ];

  const districtData = [
    { district: 'District 1', votes: 387 },
    { district: 'District 2', votes: 298 },
    { district: 'District 3', votes: 207 },
  ];

  const ageGroupData = [
    { name: '18-25', value: 145 },
    { name: '26-35', value: 267 },
    { name: '36-45', value: 223 },
    { name: '46-60', value: 189 },
    { name: '60+', value: 68 },
  ];

  const COLORS = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#43e97b'];

  return (
    <div className="statistics-page">
      <div className="page-header">
        <div>
          <h1>Vote Statistics</h1>
          <p>Comprehensive analysis and insights</p>
        </div>
        <button 
          className="refresh-btn"
          onClick={fetchStatistics}
          disabled={loading}
        >
          <RefreshCw className={loading ? 'spinning' : ''} size={20} />
          Refresh
        </button>
      </div>

      <div className="stats-overview">
        <div className="stat-box">
          <TrendingUp className="stat-icon" size={40} />
          <h3>Turnout Rate</h3>
          <p className="stat-value">{loading ? '...' : stats.turnoutRate}</p>
          <span className="stat-change">Live data from Firebase</span>
        </div>
        <div className="stat-box">
          <Zap className="stat-icon" size={40} />
          <h3>Total Votes</h3>
          <p className="stat-value">{loading ? '...' : stats.totalVotes}</p>
          <span className="stat-change">Real-time count</span>
        </div>
        <div className="stat-box">
          <Award className="stat-icon" size={40} />
          <h3>Leading Candidate</h3>
          <p className="stat-value">{loading ? '...' : stats.leadingCandidate}</p>
          <span className="stat-change">Current leader</span>
        </div>
        <div className="stat-box">
          <Clock className="stat-icon" size={40} />
          <h3>Total Voters</h3>
          <p className="stat-value">{loading ? '...' : stats.totalVoters}</p>
          <span className="stat-change">Registered voters</span>
        </div>
      </div>

      <div className="charts-grid">
        <div className="chart-card large">
          <h2>Votes by Candidate (Live Data)</h2>
          {loading ? (
            <div className="chart-loading">
              <RefreshCw className="spinning" size={32} />
              <p>Loading chart data...</p>
            </div>
          ) : candidateData.length === 0 ? (
            <div className="chart-no-data">
              <p>No votes cast yet</p>
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={candidateData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="name" tick={{ fill: '#4a5568' }} />
                <YAxis tick={{ fill: '#4a5568' }} />
                <Tooltip 
                  contentStyle={{ 
                    background: 'white', 
                    border: '1px solid #e2e8f0',
                    borderRadius: '8px'
                  }} 
                />
                <Bar dataKey="votes" fill="#667eea" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>

        <div className="chart-card">
          <h2>Age Group Distribution</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={ageGroupData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {ageGroupData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card large">
          <h2>Hourly Voting Trend</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={hourlyData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="hour" tick={{ fill: '#4a5568' }} />
              <YAxis tick={{ fill: '#4a5568' }} />
              <Tooltip 
                contentStyle={{ 
                  background: 'white', 
                  border: '1px solid #e2e8f0',
                  borderRadius: '8px'
                }} 
              />
              <Line 
                type="monotone" 
                dataKey="votes" 
                stroke="#667eea" 
                strokeWidth={3}
                dot={{ fill: '#667eea', r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <h2>Votes by District</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={districtData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis type="number" tick={{ fill: '#4a5568' }} />
              <YAxis dataKey="district" type="category" tick={{ fill: '#4a5568' }} />
              <Tooltip 
                contentStyle={{ 
                  background: 'white', 
                  border: '1px solid #e2e8f0',
                  borderRadius: '8px'
                }} 
              />
              <Bar dataKey="votes" fill="#764ba2" radius={[0, 8, 8, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="insights-section">
        <h2>Key Insights</h2>
        <div className="insights-grid">
          <div className="insight-card">
            <Lightbulb className="insight-icon" size={32} />
            <h3>High Turnout</h3>
            <p>Voter turnout is 5.2% higher than the previous election, indicating increased civic engagement.</p>
          </div>
          <div className="insight-card">
            <UsersIcon className="insight-icon" size={32} />
            <h3>Youth Participation</h3>
            <p>The 26-35 age group shows the highest participation rate at 29.9% of total votes.</p>
          </div>
          <div className="insight-card">
            <MapPin className="insight-icon" size={32} />
            <h3>District Performance</h3>
            <p>District 1 leads with 43.4% of total votes, followed by District 2 at 33.4%.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VoteStatistics;
