import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { LoginResponse } from '../../types';
import { useAuth } from '../../hooks/useAuth';
import ApiService from '../../services/apiService';

interface LoginProps {
  onLogin: (success: boolean, doctorId?: string | number, username?: string) => void;
}

const Login: React.FC<LoginProps> = ({ onLogin }) => {
  const [userName, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await ApiService.login({ userName, password });
      const data: LoginResponse = await response.json();
      
      // Usar el hook useAuth para manejar el login
      if (data.token && data.doctorId) {
        const username = data.user?.username || userName;
        login(data.token, data.doctorId, username);
        onLogin(true, data.doctorId, username);
        
        // Generate a new conversation_id for this session
        // Generated after doctor information is saved
        // para que el conversation_id incluya el doctorId correcto
        setTimeout(() => {
          // Disparar evento personalizado para indicar que se hizo login
          window.dispatchEvent(new CustomEvent('userLoginSuccess', {
            detail: { doctorId: data.doctorId, username }
          }));
        }, 100);
      } else {
        throw new Error('Invalid response from server');
      }
      navigate('/home');
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Error inesperado.');
      }
      onLogin(false);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div 
      className="min-vh-100 d-flex align-items-center py-4" 
      style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}
    >
      {loading && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            width: '100vw',
            height: '100vh',
            background: 'rgba(255,255,255,0.7)',
            zIndex: 9999,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}
        >
          <div className="spinner-border text-primary" role="status" style={{ width: '4rem', height: '4rem' }}>
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      )}
      <div className="container">
        <div className="row justify-content-center">
          <div className="col-12 col-md-8 col-lg-6 col-xl-5">
            <div className="card shadow-lg border-0" style={{ borderRadius: '15px' }}>
              <div className="card-header text-center py-4" style={{ 
                background: 'linear-gradient(135deg, #405de6 0%, #5a67d8 100%)', 
                color: 'white',
                borderRadius: '15px 15px 0 0'
              }}>
                <div className="mb-2">
                  <i className="bi bi-shield-lock-fill" style={{ fontSize: '2.5rem' }}></i>
                </div>
                <h2 className="mb-0 fw-bold">Sign In</h2>
              </div>
              
              <div className="card-body p-4">
                {error && (
                  <div className="alert alert-danger d-flex align-items-center mb-4" role="alert">
                    <i className="bi bi-exclamation-triangle me-2"></i>
                    {error}
                  </div>
                )}

                <form onSubmit={handleLogin}>
                  <div className="mb-3">
                    <label htmlFor="username" className="form-label fw-semibold">
                      <i className="bi bi-person me-1"></i>
                      Username <span className="text-danger">*</span>
                    </label>
                    <input
                      type="text"
                      className="form-control form-control-lg"
                      id="username"
                      value={userName}
                      onChange={(e) => setUsername(e.target.value)}
                      placeholder="Enter your username"
                      required
                      style={{ borderRadius: '10px' }}
                    />
                  </div>
                  
                  <div className="mb-3">
                    <label htmlFor="password" className="form-label fw-semibold">
                      <i className="bi bi-lock me-1"></i>
                      Password <span className="text-danger">*</span>
                    </label>
                    <input
                      type="password"
                      className="form-control form-control-lg"
                      id="password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="Enter your password"
                      required
                      style={{ borderRadius: '10px' }}
                    />
                  </div>
                  
                  <div className="form-check mb-4">
                    <input type="checkbox" className="form-check-input" id="rememberMe" />
                    <label className="form-check-label text-muted" htmlFor="rememberMe">
                      Remember me
                    </label>
                  </div>
                  
                  <div className="d-grid gap-2 mb-3">
                    <button 
                      type="submit" 
                      className="btn btn-lg fw-bold"
                      disabled={loading}
                      style={{
                        background: 'linear-gradient(135deg, #405de6 0%, #5a67d8 100%)',
                        color: 'white',
                        border: 'none',
                        borderRadius: '10px',
                        padding: '15px'
                      }}
                    >
                      {loading ? (
                        <>
                          <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                          Signing In...
                        </>
                      ) : (
                        <>
                          <i className="bi bi-box-arrow-in-right me-2"></i>
                          Sign In
                        </>
                      )}
                    </button>
                  </div>

                  <div className="text-center">
                    <p className="mb-0 text-muted">
                      Don't have an account?{' '}
                      <Link
                        to="/register"
                        className="fw-semibold"
                        style={{ color: '#405de6', textDecoration: 'none' }}
                      >
                        Register
                      </Link>
                    </p>
                  </div>
                </form>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
