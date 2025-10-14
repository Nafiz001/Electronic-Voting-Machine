import { Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, Users, Target, Vote, TrendingUp, Check } from 'lucide-react';
import './Navigation.css';

const Navigation = () => {
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/voters', label: 'Voter List', icon: Users },
    { path: '/candidates', label: 'Candidates', icon: Target },
    { path: '/vote-count', label: 'Vote Count', icon: Vote },
    { path: '/statistics', label: 'Statistics', icon: TrendingUp },
  ];

  return (
    <nav className="navigation">
      <div className="nav-header">
        <Check className="nav-logo" size={32} />
        <h1 className="nav-title">Voting System</h1>
      </div>
      <ul className="nav-list">
        {navItems.map((item) => {
          const IconComponent = item.icon;
          return (
            <li key={item.path}>
              <Link
                to={item.path}
                className={`nav-link ${location.pathname === item.path ? 'active' : ''}`}
              >
                <IconComponent className="nav-icon" size={24} />
                <span className="nav-label">{item.label}</span>
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
};

export default Navigation;
