import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { PatientInfoResponseDto } from '../types';
import { useAuth } from '../hooks/useAuth';
import ApiService from '../services/apiService';
import TokenManager from '../utils/tokenManager';

interface PatientsProps {
  doctorId: string | number | null;
  username?: string;
}

const Patients: React.FC<PatientsProps> = ({ doctorId, username }) => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [patients, setPatients] = useState<PatientInfoResponseDto[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>('');
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('');

  const fetchPatients = useCallback(async () => {
    if (!isAuthenticated) {
      setError('User not authenticated');
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError('');

      const response = await ApiService.getAllPatients();
      const data: PatientInfoResponseDto[] = await response.json();
      setPatients(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated]);

  useEffect(() => {
    fetchPatients();
  }, [fetchPatients]);

  const filteredPatients = patients.filter(patient => {
    const matchesSearch = patient.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         patient.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         patient.patientId.toLowerCase().includes(searchTerm.toLowerCase());
    
    // For now we don't have status filter in DTO, so we ignore statusFilter
    return matchesSearch;
  });

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US');
  };

  const handleLogout = () => {
    TokenManager.clearSessionData(); // Usar clearSessionData para mantener conversation_id
    navigate('/');
  };

  const handleProfile = () => {
    navigate('/profile');
  };

  return (
    <div style={{ minHeight: '100vh', background: 'linear-gradient(180deg, #ffffff, #405de6)', color: 'white' }}>
      <style>
        {`
          .spin {
            animation: spin 1s linear infinite;
          }
          @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
          }
        `}
      </style>
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
          {/* Navigation menu */}
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
                className="btn nav-link fw-bold"
                style={{ 
                  border: 'none', 
                  background: 'rgba(255,255,255,0.2)', 
                  color: '#fff',
                  borderRadius: '5px'
                }}
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

      {/* Contenido principal */}
      <div className="container mt-4">
        <div className="row">
          <div className="col-12">
            <div className="bg-white rounded shadow p-4" style={{ color: '#333' }}>
              <div className="d-flex justify-content-between align-items-center mb-4">
                <h2 style={{ color: '#405de6' }}>
                  <i className="bi bi-people me-2"></i>
                  Patient Management
                </h2>
                <div className="d-flex gap-2">
                  <button 
                    className="btn btn-outline-primary"
                    onClick={fetchPatients}
                    disabled={loading}
                    title="Refresh patients list"
                  >
                    <i className={`bi bi-arrow-clockwise ${loading ? 'spin' : ''}`}></i>
                  </button>
                  <button 
                    className="btn"
                    style={{ backgroundColor: '#405de6', color: '#fff' }}
                    onClick={() => navigate('/patients/new')}
                  >
                    <i className="bi bi-person-plus me-2"></i>
                    Add Patient
                  </button>
                </div>
              </div>

              {/* Search bar */}
              <div className="row mb-4">
                <div className="col-md-6">
                  <div className="input-group">
                    <span className="input-group-text">
                      <i className="bi bi-search"></i>
                    </span>
                    <input 
                      type="text" 
                      className="form-control" 
                      placeholder="Search patient by name, ID or email..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                    />
                  </div>
                </div>
                <div className="col-md-3">
                  <select 
                    className="form-select"
                    value={statusFilter}
                    onChange={(e) => setStatusFilter(e.target.value)}
                  >
                    <option value="">All statuses</option>
                    <option value="active">Active</option>
                    <option value="inactive">Inactive</option>
                  </select>
                </div>
                <div className="col-md-3">
                  <button className="btn btn-outline-primary w-100">
                    <i className="bi bi-funnel me-2"></i>
                    Filter
                  </button>
                </div>
              </div>

              {/* Statistics */}
              {!loading && !error && (
                <div className="row mb-3">
                  <div className="col-12">
                    <div className="alert alert-info d-flex align-items-center">
                      <i className="bi bi-info-circle me-2"></i>
                      <span>
                        Showing {filteredPatients.length} of {patients.length} patients
                        {searchTerm && ` matching "${searchTerm}"`}
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {/* Tabla de pacientes */}
              <div className="table-responsive">
                <table className="table table-hover">
                  <thead style={{ backgroundColor: '#405de6', color: 'white' }}>
                    <tr>
                      <th>Patient ID</th>
                      <th>Full Name</th>
                      <th>Identification</th>
                      <th>Date of Birth</th>
                      <th>Age</th>
                      <th>Phone</th>
                      <th>Email</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {loading ? (
                      <tr>
                        <td colSpan={8} className="text-center py-5">
                          <div className="spinner-border text-primary" role="status">
                            <span className="visually-hidden">Loading...</span>
                          </div>
                          <p className="text-muted mt-3">Loading patients...</p>
                        </td>
                      </tr>
                    ) : error ? (
                      <tr>
                        <td colSpan={8} className="text-center py-5">
                          <i className="bi bi-exclamation-triangle display-1 text-danger"></i>
                          <p className="text-danger mt-3">
                            Error loading patients: {error}<br/>
                            <button 
                              className="btn btn-outline-primary mt-2"
                              onClick={fetchPatients}
                            >
                              <i className="bi bi-arrow-clockwise me-2"></i>
                              Try Again
                            </button>
                          </p>
                        </td>
                      </tr>
                    ) : filteredPatients.length === 0 ? (
                      <tr>
                        <td colSpan={8} className="text-center py-5">
                          <i className="bi bi-inbox display-1 text-muted"></i>
                          <p className="text-muted mt-3">
                            {searchTerm ? 'No patients found matching your search.' : 'No patients registered yet.'}
                          </p>
                        </td>
                      </tr>
                    ) : (
                      filteredPatients.map((patient) => (
                        <tr key={patient.patientId}>
                          <td>
                            <span className="badge bg-primary">{patient.patientId}</span>
                          </td>
                          <td className="fw-bold">{patient.name}</td>
                          <td>{patient.identificationNumber}</td>
                          <td>{formatDate(patient.dateOfBirth)}</td>
                          <td>
                            <span className="badge bg-info">{patient.age} years</span>
                          </td>
                          <td>{patient.phoneNumber}</td>
                          <td>{patient.email}</td>
                          <td>
                            <div className="btn-group btn-group-sm" role="group">
                              <button 
                                className="btn btn-outline-primary"
                                title="View Patient"
                                onClick={() => navigate(`/patients/view/${patient.patientId}`, { 
                                  state: { patient } 
                                })}
                              >
                                <i className="bi bi-eye"></i>
                              </button>
                              <button 
                                className="btn btn-outline-success"
                                title="Edit Patient"
                                onClick={() => navigate(`/patients/edit/${patient.patientId}`, { 
                                  state: { patient } 
                                })}
                              >
                                <i className="bi bi-pencil"></i>
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>

              {/* Doctor information */}
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

export default Patients;
