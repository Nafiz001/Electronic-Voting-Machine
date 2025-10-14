import { CheckCircle, Calendar, Clock, MapPin, CreditCard, Info } from 'lucide-react';
import './Candidates.css';

const Candidates = () => {
  const candidates = [
    {
      id: 1,
      name: 'Alice',
      party: 'Progressive Party',
      symbol: '🌟',
      slogan: 'Innovation for Tomorrow',
      color: '#3b82f6',
      experience: '12 years in technology and public service',
      agenda: ['Digital Transformation', 'Education Reform', 'Healthcare Innovation', 'Economic Growth'],
    },
    {
      id: 2,
      name: 'Bob',
      party: 'Unity Party',
      symbol: '🏛️',
      slogan: 'Building Bridges Together',
      color: '#ef4444',
      experience: '15 years in community development',
      agenda: ['Infrastructure Development', 'Community Unity', 'Social Welfare', 'Job Creation'],
    },
    {
      id: 3,
      name: 'Charlie',
      party: 'Reform Party',
      symbol: '🚀',
      slogan: 'Forward Into the Future',
      color: '#10b981',
      experience: '10 years in environmental and social advocacy',
      agenda: ['Environmental Protection', 'Government Reform', 'Youth Empowerment', 'Sustainable Development'],
    },
  ];

  return (
    <div className="candidates-page">
      <div className="page-header">
        <h1>Candidates</h1>
        <p>Meet the candidates and their platforms</p>
      </div>

      <div className="candidates-grid">
        {candidates.map((candidate) => (
          <div key={candidate.id} className="candidate-profile-card">
            <div className="card-header" style={{ background: `linear-gradient(135deg, ${candidate.color} 0%, ${candidate.color}dd 100%)` }}>
              <div className="candidate-symbol-large">
                {candidate.symbol}
              </div>
              <h2>{candidate.name}</h2>
              <p className="party-name-large">{candidate.party}</p>
            </div>

            <div className="card-body">
              <div className="slogan-section">
                <span className="quote-icon">"</span>
                <p className="slogan">{candidate.slogan}</p>
              </div>

              <div className="info-section">
                <h3><Info size={20} /> Experience</h3>
                <p>{candidate.experience}</p>
              </div>

              <div className="info-section">
                <h3><CheckCircle size={20} /> Key Agenda</h3>
                <ul className="agenda-list">
                  {candidate.agenda.map((item, index) => (
                    <li key={index}>
                      <CheckCircle size={16} className="checkmark" />
                      {item}
                    </li>
                  ))}
                </ul>
              </div>

              <div className="card-footer">
                <button className="learn-more-btn" style={{ backgroundColor: candidate.color }}>
                  Learn More
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="election-info">
        <h2><Calendar size={28} /> Election Information</h2>
        <div className="info-grid">
          <div className="info-item">
            <Calendar className="info-icon" size={40} />
            <div>
              <h4>Election Date</h4>
              <p>November 5, 2025</p>
            </div>
          </div>
          <div className="info-item">
            <Clock className="info-icon" size={40} />
            <div>
              <h4>Voting Hours</h4>
              <p>8:00 AM - 6:00 PM</p>
            </div>
          </div>
          <div className="info-item">
            <MapPin className="info-icon" size={40} />
            <div>
              <h4>Polling Stations</h4>
              <p>Check your district</p>
            </div>
          </div>
          <div className="info-item">
            <CreditCard className="info-icon" size={40} />
            <div>
              <h4>Required Documents</h4>
              <p>Valid ID & Voter Card</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Candidates;
