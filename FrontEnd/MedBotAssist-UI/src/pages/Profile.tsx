import React from 'react';
import { useNavigate } from 'react-router-dom';

interface ProfileProps {
  doctorId: string | number | null;
  username?: string;
}

const Profile: React.FC<ProfileProps> = ({ doctorId, username }) => {
  const navigate = useNavigate();

  const handleBack = () => {
    navigate('/home');
  };

  const handleLogout = () => {
    localStorage.removeItem('authToken');
    localStorage.removeItem('doctorId');
    localStorage.removeItem('username');
    navigate('/');
  };

  const handleProfile = () => {
    navigate('/profile');
  };

  return (
    <div style={{ minHeight: '100vh', background: 'linear-gradient(180deg, #ffffff, #405de6)', color: 'white' }}>
      {/* Navbar */}
      <nav className="navbar navbar-expand-lg navbar-dark px-4 pt-3" style={{ backgroundColor: '#405de6' }}>
        <span className="navbar-brand fw-bold text-white">MedBotAssist</span>
        <button
          className="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbarMenu"
          style={{ borderColor: '#ffffff' }}
        >
          <span className="navbar-toggler-icon"></span>
        </button>
        <div className="collapse navbar-collapse" id="navbarMenu">
          {/* Menu de navegación */}
          <ul className="navbar-nav me-auto">
            <li className="nav-item">
              <button
                className="btn nav-link text-white fw-bold"
                onClick={() => navigate('/home')}
                style={{ border: 'none', background: 'transparent' }}
              >
                <i className="bi bi-house me-2"></i>
                Home
              </button>
            </li>
            <li className="nav-item">
              <button
                className="btn nav-link text-white fw-bold"
                onClick={() => navigate('/patients')}
                style={{ border: 'none', background: 'transparent' }}
              >
                <i className="bi bi-people me-2"></i>
                Patients
              </button>
            </li>
            <li className="nav-item">
              <button
                className="btn nav-link text-white fw-bold"
                onClick={() => navigate('/appointments')}
                style={{ border: 'none', background: 'transparent' }}
              >
                <i className="bi bi-calendar-check me-2"></i>
                Appointments
              </button>
            </li>
          </ul>
          
          {/* Usuario dropdown */}
          <ul className="navbar-nav">
            <li className="nav-item dropdown">
              <button
                className="btn dropdown-toggle d-flex align-items-center"
                style={{
                  backgroundColor: 'rgba(255,255,255,0.2)',
                  color: '#fff',
                  border: '1px solid rgba(255,255,255,0.3)',
                  fontWeight: 'bold'
                }}
                type="button"
                data-bs-toggle="dropdown"
                aria-expanded="false"
              >
                <i className="bi bi-person-circle me-2"></i>
                {username || 'Usuario'}
              </button>
              <ul className="dropdown-menu dropdown-menu-end">
                <li>
                  <button 
                    className="dropdown-item d-flex align-items-center" 
                    onClick={handleProfile}
                  >
                    <i className="bi bi-person me-2"></i>
                    Profile
                  </button>
                </li>
                <li><hr className="dropdown-divider" /></li>
                <li>
                  <button 
                    className="dropdown-item d-flex align-items-center text-danger" 
                    onClick={handleLogout}
                  >
                    <i className="bi bi-box-arrow-right me-2"></i>
                    Logout
                  </button>
                </li>
              </ul>
            </li>
          </ul>
        </div>
      </nav>

      {/* Contenido del perfil */}
      <div className="container mt-5">
        <div className="row justify-content-center">
          <div className="col-md-8">
            <div className="bg-white rounded shadow p-4" style={{ color: '#333' }}>
              <h2 className="text-center mb-4" style={{ color: '#405de6' }}>
                <i className="bi bi-person-circle me-2"></i>
                Doctor Profile
              </h2>
              
              <div className="row">
                <div className="col-md-6">
                  <div className="mb-3">
                    <label className="form-label fw-bold">Username:</label>
                    <p className="form-control-plaintext border rounded px-3 py-2 bg-light">
                      {username || 'Not available'}
                    </p>
                  </div>
                </div>
                <div className="col-md-6">
                  <div className="mb-3">
                    <label className="form-label fw-bold">Doctor ID:</label>
                    <p className="form-control-plaintext border rounded px-3 py-2 bg-light">
                      {doctorId || 'Not available'}
                    </p>
                  </div>
                </div>
              </div>

              <div className="mb-3">
                <label className="form-label fw-bold">Specialty:</label>
                <p className="form-control-plaintext border rounded px-3 py-2 bg-light">
                  To be defined
                </p>
              </div>

              <div className="mb-3">
                <label className="form-label fw-bold">Email:</label>
                <p className="form-control-plaintext border rounded px-3 py-2 bg-light">
                  To be defined
                </p>
              </div>

              <div className="text-center mt-4">
                <button 
                  className="btn btn-outline-primary me-3"
                  style={{ borderColor: '#405de6', color: '#405de6' }}
                >
                  <i className="bi bi-pencil me-2"></i>
                  Edit Profile
                </button>
                <button 
                  className="btn"
                  style={{ backgroundColor: '#405de6', color: '#fff' }}
                  onClick={handleBack}
                >
                  <i className="bi bi-house me-2"></i>
                  Go to Dashboard
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;
