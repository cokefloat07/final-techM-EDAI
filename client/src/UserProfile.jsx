import { API_BASE_URL } from './api';
import React, { useState } from 'react';
import './UserProfile.css';

const UserProfile = ({ user, onLogout }) => {
  const [showMenu, setShowMenu] = useState(false);
  const [showProfile, setShowProfile] = useState(false);

  const handleLogout = () => {
    localStorage.removeItem('currentUser');
    onLogout();
    setShowMenu(false);
  };

  const getUserStats = () => {
    const userData = JSON.parse(localStorage.getItem(`userData_${user.email}`) || '{}');
    return {
      totalChats: userData.chats ? userData.chats.length : 0,
      totalEstimates: userData.estimates ? userData.estimates.length : 0,
      memberSince: new Date(user.createdAt).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    };
  };

  const stats = getUserStats();
  const fullName = user.fullName || user.email?.split('@')[0] || 'User';
  const firstLetter = (fullName.charAt(0) || 'U').toUpperCase();

  return (
    <>
      <div className="user-profile-button">
        <button 
          className="profile-avatar"
          onClick={() => setShowMenu(!showMenu)}
          title={fullName}
        >
          {firstLetter}
        </button>

        {showMenu && (
          <div className="profile-dropdown">
            <div className="dropdown-header">
              <div className="dropdown-avatar">{firstLetter}</div>
              <div className="dropdown-info">
                <p className="dropdown-name">{fullName}</p>
                <p className="dropdown-email">{user.email}</p>
              </div>
            </div>

            <div className="dropdown-divider"></div>

            <button 
              className="dropdown-item"
              onClick={() => {
                setShowProfile(true);
                setShowMenu(false);
              }}
            >
              👤 View Profile
            </button>

            <button 
              className="dropdown-item logout"
              onClick={handleLogout}
            >
              🚪 Logout
            </button>
          </div>
        )}
      </div>

      {showProfile && (
        <div className="profile-modal">
          <div className="profile-modal-content">
            <button 
              className="modal-close"
              onClick={() => setShowProfile(false)}
            >
              ✕
            </button>

            <div className="profile-header">
              <div className="profile-avatar-large">{firstLetter}</div>
              <div>
                <h2>{fullName}</h2>
                <p className="profile-email">{user.email}</p>
              </div>
            </div>

            <div className="profile-stats">
              <div className="stat">
                <div className="stat-number">{stats.totalChats}</div>
                <div className="stat-label">Total Chats</div>
              </div>
              <div className="stat">
                <div className="stat-number">{stats.totalEstimates}</div>
                <div className="stat-label">Estimates</div>
              </div>
              <div className="stat">
                <div className="stat-label">Member Since</div>
                <div className="stat-date">{stats.memberSince}</div>
              </div>
            </div>

            <div className="profile-actions">
              <button 
                className="btn-secondary"
                onClick={() => setShowProfile(false)}
              >
                Close
              </button>
              <button 
                className="btn-logout"
                onClick={handleLogout}
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      )}

      {showMenu && (
        <div 
          className="overlay"
          onClick={() => setShowMenu(false)}
        ></div>
      )}
    </>
  );
};

export default UserProfile;
