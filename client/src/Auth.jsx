import { API_BASE_URL } from './api';
import React, { useState } from 'react';
import './Auth.css';

const Auth = ({ onAuthSuccess }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    fullName: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    setError('');
  };

  const validateEmail = (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isLogin) {
        // LOGIN
        if (!formData.email || !formData.password) {
          setError('Email and password are required');
          setLoading(false);
          return;
        }

        if (!validateEmail(formData.email)) {
          setError('Invalid email format');
          setLoading(false);
          return;
        }

        // Call backend login endpoint
        const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: formData.email,
            password: formData.password
          })
        });

        if (!response.ok) {
          const errorData = await response.json();
          setError(errorData.detail || 'Login failed');
          setLoading(false);
          return;
        }

        const user = await response.json();

        // Store user info in localStorage
        localStorage.setItem('currentUser', JSON.stringify({
          id: user.id,
          email: user.email,
          full_name: user.full_name,
          created_at: user.created_at
        }));

        onAuthSuccess({
          id: user.id,
          email: user.email,
          fullName: user.full_name,
          createdAt: user.created_at
        });
      } else {
        // SIGNUP
        if (!formData.email || !formData.password || !formData.confirmPassword || !formData.fullName) {
          setError('All fields are required');
          setLoading(false);
          return;
        }

        if (!validateEmail(formData.email)) {
          setError('Invalid email format');
          setLoading(false);
          return;
        }

        if (formData.password.length < 6) {
          setError('Password must be at least 6 characters');
          setLoading(false);
          return;
        }

        if (formData.password !== formData.confirmPassword) {
          setError('Passwords do not match');
          setLoading(false);
          return;
        }

        // Call backend register endpoint
        const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: formData.email,
            password: formData.password,
            full_name: formData.fullName
          })
        });

        if (!response.ok) {
          const errorData = await response.json();
          setError(errorData.detail || 'Registration failed');
          setLoading(false);
          return;
        }

        const user = await response.json();

        // Store user info in localStorage
        localStorage.setItem('currentUser', JSON.stringify({
          id: user.id,
          email: user.email,
          full_name: user.full_name,
          created_at: user.created_at
        }));

        onAuthSuccess({
          id: user.id,
          email: user.email,
          fullName: user.full_name,
          createdAt: user.created_at
        });
      }
    } catch (err) {
      setError('An error occurred. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-background">
        <div className="auth-blob auth-blob-1"></div>
        <div className="auth-blob auth-blob-2"></div>
        <div className="auth-blob auth-blob-3"></div>
      </div>

      <div className="auth-wrapper">
        <div className="auth-content">
          {/* Left Section - Brand & Features */}
          <div className="auth-brand-section">
            <div className="brand-header">
              <div className="brand-icon">🌱</div>
              <h1>Green Model<br/>Advisor</h1>
            </div>
            <p className="brand-subtitle">Smart AI Selection & Carbon Tracking</p>
            
            <div className="brand-features">
              <div className="feature-item">
                <div className="feature-icon">🤖</div>
                <div className="feature-text">
                  <h4>Compare 3 AI Models</h4>
                  <p>Find the best model for your needs</p>
                </div>
              </div>
              <div className="feature-item">
                <div className="feature-icon">🌍</div>
                <div className="feature-text">
                  <h4>Track Carbon Emissions</h4>
                  <p>Monitor environmental impact</p>
                </div>
              </div>
              <div className="feature-item">
                <div className="feature-icon">💾</div>
                <div className="feature-text">
                  <h4>Save Chat History</h4>
                  <p>Access all your conversations</p>
                </div>
              </div>
              <div className="feature-item">
                <div className="feature-icon">📊</div>
                <div className="feature-text">
                  <h4>Performance Dashboard</h4>
                  <p>View detailed analytics</p>
                </div>
              </div>
            </div>
          </div>

          {/* Right Section - Auth Form */}
          <div className="auth-form-section">
            <div className="auth-card">
              <div className="form-header">
                <h2 className="form-title">{isLogin ? '👋 Welcome Back!' : '🚀 Get Started'}</h2>
                <p className="form-subtitle">
                  {isLogin 
                    ? 'Sign in to your account to continue' 
                    : 'Create your account in seconds'}
                </p>
              </div>

              <form onSubmit={handleSubmit} className="auth-form">
                {!isLogin && (
                  <div className="form-group">
                    <label>Full Name</label>
                    <div className="input-wrapper">
                      <span className="input-icon">👤</span>
                      <input
                        type="text"
                        name="fullName"
                        value={formData.fullName}
                        onChange={handleChange}
                        placeholder="John Doe"
                        disabled={loading}
                      />
                    </div>
                  </div>
                )}

                <div className="form-group">
                  <label>Email Address</label>
                  <div className="input-wrapper">
                    <span className="input-icon">✉️</span>
                    <input
                      type="email"
                      name="email"
                      value={formData.email}
                      onChange={handleChange}
                      placeholder="you@example.com"
                      disabled={loading}
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label>Password</label>
                  <div className="input-wrapper">
                    <span className="input-icon">🔒</span>
                    <input
                      type="password"
                      name="password"
                      value={formData.password}
                      onChange={handleChange}
                      placeholder="••••••••"
                      disabled={loading}
                    />
                  </div>
                  {!isLogin && (
                    <small className="input-hint">Minimum 6 characters for security</small>
                  )}
                </div>

                {!isLogin && (
                  <div className="form-group">
                    <label>Confirm Password</label>
                    <div className="input-wrapper">
                      <span className="input-icon">✓</span>
                      <input
                        type="password"
                        name="confirmPassword"
                        value={formData.confirmPassword}
                        onChange={handleChange}
                        placeholder="••••••••"
                        disabled={loading}
                      />
                    </div>
                  </div>
                )}

                {error && (
                  <div className="error-message">
                    <span className="error-icon">⚠️</span>
                    <span>{error}</span>
                  </div>
                )}

                <button 
                  type="submit" 
                  className="auth-submit-btn"
                  disabled={loading}
                >
                  <span className="btn-text">
                    {loading ? '⏳ Processing...' : (isLogin ? '🔓 Sign In' : '✨ Create Account')}
                  </span>
                  <span className="btn-arrow">→</span>
                </button>
              </form>

              <div className="auth-divider">
                <span>or</span>
              </div>

              <div className="auth-toggle">
                <p>
                  {isLogin 
                    ? "Don't have an account yet? " 
                    : 'Already have an account? '
                  }
                  <button
                    type="button"
                    onClick={() => {
                      setIsLogin(!isLogin);
                      setFormData({
                        email: '',
                        password: '',
                        confirmPassword: '',
                        fullName: ''
                      });
                      setError('');
                    }}
                    className="toggle-btn"
                  >
                    {isLogin ? '✨ Sign Up Now' : '🔓 Sign In Here'}
                  </button>
                </p>
              </div>

              <div className="auth-footer">
                <p>🔒 Your data is secure and encrypted</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Auth;
