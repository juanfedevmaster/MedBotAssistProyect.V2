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
    <div className="d-flex justify-content-center align-items-center vh-100" style={{ background: 'linear-gradient(180deg, #ffffff, #405de6)' }}>
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
            <span className="visually-hidden">Cargando...</span>
          </div>
        </div>
      )}
      <div className="bg-white p-4 rounded shadow" style={{ width: '100%', maxWidth: '400px' }}>
        <h2 className="text-center mb-4">LOGIN</h2>
        <form onSubmit={handleLogin}>
          <div className="mb-3">
            <label htmlFor="username" className="form-label">Username</label>
            <input
              type="text"
              className="form-control"
              id="username"
              value={userName}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Correo electrónico"
              required
            />
          </div>
          <div className="mb-3">
            <label htmlFor="password" className="form-label">Contraseña</label>
            <input
              type="password"
              className="form-control"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
            />
          </div>
          <div className="form-check mb-3">
            <input type="checkbox" className="form-check-input" id="rememberMe" />
            <label className="form-check-label" htmlFor="rememberMe">Recordarme</label>
          </div>
          <button type="submit" className="btn btn-primary w-100">Iniciar sesión</button>
          {error && <div className="alert alert-danger mt-3">{error}</div>}
        </form>
        <p className="text-center mt-3">
          ¿No tienes cuenta? <Link to="/register">Regístrate</Link>
        </p>
      </div>
    </div>
  );
};

export default Login;
