import React, { useState, useEffect } from 'react';
import { useNavigate, useParams, useLocation } from 'react-router-dom';
import { PatientCreateDto, PatientUpdateDto, PatientInfoResponseDto } from '../types';
import { useAuth } from '../hooks/useAuth';
import ApiService from '../services/apiService';

// Helper function to get current date in YYYY-MM-DD format
const getCurrentDate = (): string => {
  const today = new Date();
  const year = today.getFullYear();
  const month = String(today.getMonth() + 1).padStart(2, '0');
  const day = String(today.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
};

interface PatientFormProps {
  doctorId: string | number | null;
  username?: string;
}

const PatientForm: React.FC<PatientFormProps> = ({ doctorId, username }) => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const location = useLocation();
  const { isAuthenticated, logout } = useAuth();
  
  // Determinar el modo basado en la ruta
  const isViewing = location.pathname.includes('/view/');
  const isEditing = location.pathname.includes('/edit/');
  
  const pageTitle = isViewing ? 'View Patient' : isEditing ? 'Edit Patient' : 'Create New Patient';
  
  // Estados del formulario
  const [formData, setFormData] = useState<PatientCreateDto>({
    name: '',
    identificationNumber: '',
    dateOfBirth: '',
    phoneNumber: '',
    email: ''
  });
  
  const [patientId, setPatientId] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [success, setSuccess] = useState<string>('');

  // Si estamos editando o viendo, cargar los datos del paciente
  useEffect(() => {
    if ((isEditing || isViewing) && location.state?.patient) {
      const patient = location.state.patient as PatientInfoResponseDto;
      setFormData({
        name: patient.name,
        identificationNumber: patient.identificationNumber,
        dateOfBirth: patient.dateOfBirth.split('T')[0], // Formato YYYY-MM-DD
        phoneNumber: patient.phoneNumber,
        email: patient.email
      });
      setPatientId(patient.patientId);
    }
  }, [isEditing, isViewing, location.state]);

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const handleProfile = () => {
    navigate('/profile');
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (isViewing) return; // No permitir cambios en modo view
    
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const validateForm = (): boolean => {
    if (!formData.name.trim()) {
      setError('Name is required');
      return false;
    }
    if (!formData.identificationNumber.trim()) {
      setError('Identification number is required');
      return false;
    }
    if (!formData.dateOfBirth) {
      setError('Date of birth is required');
      return false;
    }
    
    // Validate that date of birth is not in the future
    const today = new Date();
    const birthDate = new Date(formData.dateOfBirth);
    
    // Reset time to compare only dates
    today.setHours(23, 59, 59, 999); // End of today
    birthDate.setHours(0, 0, 0, 0); // Start of birth date
    
    if (birthDate > today) {
      setError('Date of birth cannot be in the future');
      return false;
    }
    
    if (!formData.phoneNumber.trim()) {
      setError('Phone number is required');
      return false;
    }
    if (!formData.email.trim()) {
      setError('Email is required');
      return false;
    }
    if (!/\S+@\S+\.\S+/.test(formData.email)) {
      setError('Please enter a valid email address');
      return false;
    }
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (isViewing) return; // No permitir submit en modo view
    
    setError('');
    setSuccess('');

    if (!validateForm()) return;

    if (!isAuthenticated) {
      setError('User not authenticated');
      return;
    }

    try {
      setLoading(true);

      if (isEditing && id) {
        const updateData: PatientUpdateDto = {
          ...formData,
          patientId: id
        };
        await ApiService.updatePatient(id, updateData);
        setSuccess('Patient updated successfully!');
      } else {
        await ApiService.createPatient(formData);
        setSuccess('Patient created successfully!');
        // Clear the form after creating
        setFormData({
          name: '',
          identificationNumber: '',
          dateOfBirth: '',
          phoneNumber: '',
          email: ''
        });
      }

      // Redirect to patient list after a brief delay
      setTimeout(() => {
        navigate('/patients');
      }, 1500);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    navigate('/patients');
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
                onClick={() => navigate('/patients')}
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
            <li className="nav-item">
              <button
                className="btn nav-link text-white fw-bold"
                onClick={() => navigate('/instructions')}
                style={{ border: 'none', background: 'transparent' }}
              >
                <i className="bi bi-file-earmark-text me-2"></i>
                Instructions
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
                {username || 'User'}
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
        <div className="row justify-content-center">
          <div className="col-lg-8">
            <div className="bg-white rounded shadow p-4" style={{ color: '#333' }}>
              {/* Header */}
              <div className="d-flex justify-content-between align-items-center mb-4">
                <h2 style={{ color: '#405de6' }}>
                  <i className={`bi ${isEditing ? 'bi-person-gear' : 'bi-person-plus'} me-2`}></i>
                  {pageTitle}
                </h2>
                <button 
                  className="btn btn-outline-secondary"
                  onClick={handleCancel}
                >
                  <i className="bi bi-arrow-left me-2"></i>
                  Back to Patients
                </button>
              </div>

              {/* Mensajes de estado */}
              {error && (
                <div className="alert alert-danger d-flex align-items-center" role="alert">
                  <i className="bi bi-exclamation-triangle me-2"></i>
                  {error}
                </div>
              )}
              
              {success && (
                <div className="alert alert-success d-flex align-items-center" role="alert">
                  <i className="bi bi-check-circle me-2"></i>
                  {success}
                </div>
              )}

              {/* Formulario */}
              <form onSubmit={handleSubmit}>
                <div className="row">
                  {/* Patient ID - Solo mostrar si estamos editando o viendo */}
                  {(isEditing || isViewing) && (
                    <div className="col-md-6 mb-3">
                      <label htmlFor="patientId" className="form-label fw-bold">
                        <i className="bi bi-card-text me-2"></i>
                        Patient ID
                      </label>
                      <input
                        type="text"
                        className="form-control"
                        id="patientId"
                        name="patientId"
                        value={patientId}
                        readOnly
                        style={{ backgroundColor: '#f8f9fa' }}
                      />
                    </div>
                  )}

                  {/* Nombre */}
                  <div className={`${(isEditing || isViewing) ? 'col-md-6' : 'col-md-6'} mb-3`}>
                    <label htmlFor="name" className="form-label fw-bold">
                      <i className="bi bi-person me-2"></i>
                      Full Name {!isViewing && '*'}
                    </label>
                    <input
                      type="text"
                      className="form-control"
                      id="name"
                      name="name"
                      value={formData.name}
                      onChange={handleInputChange}
                      placeholder="Enter patient's full name"
                      required={!isViewing}
                      readOnly={isViewing}
                      autoComplete="off"
                      style={isViewing ? { backgroundColor: '#f8f9fa' } : {}}
                    />
                  </div>

                  {/* Identification number */}
                  <div className="col-md-6 mb-3">
                    <label htmlFor="identificationNumber" className="form-label fw-bold">
                      <i className="bi bi-card-text me-2"></i>
                      Identification Number {!isViewing && '*'}
                    </label>
                    <input
                      type="text"
                      className="form-control"
                      id="identificationNumber"
                      name="identificationNumber"
                      value={formData.identificationNumber}
                      onChange={handleInputChange}
                      placeholder="Enter ID/Passport number"
                      required={!isViewing}
                      readOnly={isViewing}
                      autoComplete="off"
                      style={isViewing ? { backgroundColor: '#f8f9fa' } : {}}
                    />
                  </div>

                  {/* Fecha de nacimiento */}
                  <div className="col-md-6 mb-3">
                    <label htmlFor="dateOfBirth" className="form-label fw-bold">
                      <i className="bi bi-calendar-date me-2"></i>
                      Date of Birth {!isViewing && '*'}
                    </label>
                    <input
                      type="date"
                      className="form-control"
                      id="dateOfBirth"
                      name="dateOfBirth"
                      value={formData.dateOfBirth}
                      onChange={handleInputChange}
                      required={!isViewing}
                      readOnly={isViewing}
                      autoComplete="off"
                      max={getCurrentDate()}
                      style={isViewing ? { backgroundColor: '#f8f9fa' } : {}}
                    />
                  </div>

                  {/* Phone */}
                  <div className="col-md-6 mb-3">
                    <label htmlFor="phoneNumber" className="form-label fw-bold">
                      <i className="bi bi-telephone me-2"></i>
                      Phone Number {!isViewing && '*'}
                    </label>
                    <input
                      type="tel"
                      className="form-control"
                      id="phoneNumber"
                      name="phoneNumber"
                      value={formData.phoneNumber}
                      onChange={handleInputChange}
                      placeholder="Enter phone number"
                      required={!isViewing}
                      readOnly={isViewing}
                      autoComplete="off"
                      style={isViewing ? { backgroundColor: '#f8f9fa' } : {}}
                    />
                  </div>

                  {/* Email */}
                  <div className="col-12 mb-4">
                    <label htmlFor="email" className="form-label fw-bold">
                      <i className="bi bi-envelope me-2"></i>
                      Email Address {!isViewing && '*'}
                    </label>
                    <input
                      type="email"
                      className="form-control"
                      id="email"
                      name="email"
                      value={formData.email}
                      onChange={handleInputChange}
                      placeholder="Enter email address"
                      required={!isViewing}
                      readOnly={isViewing}
                      autoComplete="off"
                      style={isViewing ? { backgroundColor: '#f8f9fa' } : {}}
                    />
                  </div>
                </div>

                {/* Botones */}
                <div className="d-flex justify-content-between gap-3">
                  {/* Add Note button - Only visible in viewing mode */}
                  {isViewing && (
                    <button 
                      type="button" 
                      className="btn btn-outline-primary"
                      onClick={() => {
                        navigate(`/patients/notes/${patientId}`);
                      }}
                    >
                      <i className="bi bi-file-text me-2"></i>
                      Add Note
                    </button>
                  )}
                  
                  <div className="d-flex gap-3">
                    <button 
                      type="button" 
                      className="btn btn-outline-secondary"
                      onClick={handleCancel}
                      disabled={loading}
                    >
                      {isViewing ? 'Back to Patients' : 'Cancel'}
                    </button>
                    {!isViewing && (
                      <button 
                        type="submit" 
                        className="btn"
                        style={{ backgroundColor: '#405de6', color: '#fff' }}
                        disabled={loading}
                      >
                      {loading ? (
                        <>
                          <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                          {isEditing ? 'Updating...' : 'Creating...'}
                        </>
                      ) : (
                        <>
                          <i className={`bi ${isEditing ? 'bi-check-lg' : 'bi-plus-lg'} me-2`}></i>
                          {isEditing ? 'Update Patient' : 'Create Patient'}
                        </>
                      )}
                    </button>
                  )}
                  </div>
                </div>
              </form>

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

export default PatientForm;
