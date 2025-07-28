import React from 'react';
import { useNavigate } from 'react-router-dom';

interface AppointmentsProps {
  doctorId: string | number | null;
  username?: string;
}

const Appointments: React.FC<AppointmentsProps> = ({ doctorId, username }) => {
  const navigate = useNavigate();

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
                className="btn nav-link fw-bold"
                style={{ 
                  border: 'none', 
                  background: 'rgba(255,255,255,0.2)', 
                  color: '#fff',
                  borderRadius: '5px'
                }}
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

      {/* Contenido principal */}
      <div className="container mt-4">
        <div className="row">
          <div className="col-12">
            <div className="bg-white rounded shadow p-4" style={{ color: '#333' }}>
              <div className="d-flex justify-content-between align-items-center mb-4">
                <h2 style={{ color: '#405de6' }}>
                  <i className="bi bi-calendar-check me-2"></i>
                  Appointment Management
                </h2>
                <button 
                  className="btn"
                  style={{ backgroundColor: '#405de6', color: '#fff' }}
                >
                  <i className="bi bi-calendar-plus me-2"></i>
                  New Appointment
                </button>
              </div>

              {/* Filtros y vista */}
              <div className="row mb-4">
                <div className="col-md-4">
                  <div className="input-group">
                    <span className="input-group-text">
                      <i className="bi bi-search"></i>
                    </span>
                    <input 
                      type="text" 
                      className="form-control" 
                      placeholder="Search by patient..."
                    />
                  </div>
                </div>
                <div className="col-md-2">
                  <select className="form-select">
                    <option value="">All</option>
                    <option value="pendiente">Pending</option>
                    <option value="confirmada">Confirmed</option>
                    <option value="completada">Completed</option>
                    <option value="cancelada">Cancelled</option>
                  </select>
                </div>
                <div className="col-md-3">
                  <input 
                    type="date" 
                    className="form-control"
                    defaultValue={new Date().toISOString().split('T')[0]}
                  />
                </div>
                <div className="col-md-3">
                  <div className="btn-group w-100" role="group">
                    <button className="btn btn-outline-primary active">
                      <i className="bi bi-list-ul me-1"></i>
                      List
                    </button>
                    <button className="btn btn-outline-primary">
                      <i className="bi bi-calendar-week me-1"></i>
                      Calendar
                    </button>
                  </div>
                </div>
              </div>

              {/* Vista de citas del día */}
              <div className="row mb-4">
                <div className="col-12">
                  <div className="p-3 bg-light rounded">
                    <h5 className="mb-3">
                      <i className="bi bi-calendar-date me-2"></i>
                      Today's Appointments - {new Date().toLocaleDateString('en-US', { 
                        weekday: 'long', 
                        year: 'numeric', 
                        month: 'long', 
                        day: 'numeric' 
                      })}
                    </h5>
                    <div className="row">
                      <div className="col-md-3">
                        <div className="card border-primary">
                          <div className="card-body text-center">
                            <h6 className="card-title text-primary">Pending</h6>
                            <h3 className="text-primary">0</h3>
                          </div>
                        </div>
                      </div>
                      <div className="col-md-3">
                        <div className="card border-success">
                          <div className="card-body text-center">
                            <h6 className="card-title text-success">Confirmed</h6>
                            <h3 className="text-success">0</h3>
                          </div>
                        </div>
                      </div>
                      <div className="col-md-3">
                        <div className="card border-info">
                          <div className="card-body text-center">
                            <h6 className="card-title text-info">Completed</h6>
                            <h3 className="text-info">0</h3>
                          </div>
                        </div>
                      </div>
                      <div className="col-md-3">
                        <div className="card border-danger">
                          <div className="card-body text-center">
                            <h6 className="card-title text-danger">Cancelled</h6>
                            <h3 className="text-danger">0</h3>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Tabla de citas */}
              <div className="table-responsive">
                <table className="table table-hover">
                  <thead style={{ backgroundColor: '#405de6', color: 'white' }}>
                    <tr>
                      <th>Time</th>
                      <th>Patient</th>
                      <th>Consultation Type</th>
                      <th>Status</th>
                      <th>Duration</th>
                      <th>Notes</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td colSpan={7} className="text-center py-5">
                        <i className="bi bi-calendar-x display-1 text-muted"></i>
                        <p className="text-muted mt-3">
                          No appointments scheduled for today.<br/>
                          <small>Data will be loaded when we connect with the backend.</small>
                        </p>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              {/* Información del doctor */}
              <div className="mt-4 p-3 bg-light rounded">
                <small className="text-muted">
                  <i className="bi bi-info-circle me-1"></i>
                  Doctor ID: <strong>{doctorId}</strong> | 
                  Session: <strong>{username}</strong>
                </small>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Appointments;
