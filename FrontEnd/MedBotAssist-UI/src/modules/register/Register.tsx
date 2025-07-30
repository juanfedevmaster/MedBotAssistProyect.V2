import React, { useState, useEffect } from 'react';
import { API_ENDPOINTS } from '../../config/endpoints';
import { useNavigate } from 'react-router-dom';

interface RegisterRequest {
  fullName: string;
  email: string;
  userName: string;
  password: string;
  confirmPassword: string;
  roleId: number;
  specialtyId: number;
  medicalLicenseNumber: string;
}

interface Specialty {
  specialtyId: number;
  specialtyName: string;
}

const Register: React.FC = () => {
  const navigate = useNavigate();
  const [form, setForm] = useState<RegisterRequest>({
    fullName: '',
    email: '',
    userName: '',
    password: '',
    confirmPassword: '',
    roleId: 1, // Always will be 1 as specified by the user
    specialtyId: 0,
    medicalLicenseNumber: '',
  });
  const [specialties, setSpecialties] = useState<Specialty[]>([]);
  const [loadingSpecialties, setLoadingSpecialties] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // Cargar especialidades al montar el componente
  useEffect(() => {
    const loadSpecialties = async () => {
      try {
        setLoadingSpecialties(true);
        const response = await fetch(API_ENDPOINTS.REGISTER_SPECIALTIES);
        
        if (response.ok) {
          const data = await response.json();
          // Asumir que la respuesta contiene las especialidades
          // If it's a direct array, use it; if it's in a property, extract it
          const specialtiesData = Array.isArray(data) ? data : data.specialties || [];
          setSpecialties(specialtiesData);
        } else {
          console.error('Error loading specialties:', response.statusText);
          setSpecialties([]);
        }
      } catch (error) {
        console.error('Error fetching specialties:', error);
        setSpecialties([]);
      } finally {
        setLoadingSpecialties(false);
      }
    };

    loadSpecialties();
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setForm({ 
      ...form, 
      [name]: name === 'specialtyId' ? parseInt(value) : value 
    });
    setError('');
    setSuccess('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    // Validations
    if (form.password !== form.confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    if (!form.specialtyId || form.specialtyId === 0) {
      setError('Please select a medical specialty.');
      return;
    }

    if (!form.medicalLicenseNumber.trim()) {
      setError('Please enter the medical license number.');
      return;
    }

    try {
      setIsLoading(true);
      const response = await fetch(API_ENDPOINTS.REGISTER, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          fullName: form.fullName,
          email: form.email,
          userName: form.userName,
          password: form.password,
          roleId: form.roleId, // Always will be 1
          specialtyId: form.specialtyId,
          medicalLicenseNumber: form.medicalLicenseNumber,
        }),
      });

      if (!response.ok) {
        const errorData = await response.text();
        throw new Error(`Could not register user: ${errorData}`);
      }

      setSuccess('Doctor registered successfully! Redirecting to login...');
      setTimeout(() => {
        navigate('/');
      }, 2000);
      
      // Reset form
      setForm({
        fullName: '',
        email: '',
        userName: '',
        password: '',
        confirmPassword: '',
        roleId: 1,
        specialtyId: 0,
        medicalLicenseNumber: '',
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unexpected error during registration.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div 
      className="min-vh-100 d-flex align-items-center py-4" 
      style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}
    >
      <div className="container">
        <div className="row justify-content-center">
          <div className="col-12 col-md-10 col-lg-8 col-xl-7">
            <div className="card shadow-lg border-0" style={{ borderRadius: '15px' }}>
              <div className="card-header text-center py-4" style={{ 
                background: 'linear-gradient(135deg, #405de6 0%, #5a67d8 100%)', 
                color: 'white',
                borderRadius: '15px 15px 0 0'
              }}>
                <div className="mb-2">
                  <i className="bi bi-person-plus-fill" style={{ fontSize: '2.5rem' }}></i>
                </div>
                <h2 className="mb-0 fw-bold">Doctor Registration</h2>
              </div>
              
              <div className="card-body p-4">
                {error && (
                  <div className="alert alert-danger d-flex align-items-center mb-4" role="alert">
                    <i className="bi bi-exclamation-triangle me-2"></i>
                    {error}
                  </div>
                )}
                
                {success && (
                  <div className="alert alert-success d-flex align-items-center mb-4" role="alert">
                    <i className="bi bi-check-circle me-2"></i>
                    {success}
                  </div>
                )}

                <form onSubmit={handleSubmit}>
                  {/* Personal Information */}
                  <div className="mb-3">
                    <h6 className="text-muted mb-2">
                      <i className="bi bi-person me-2"></i>
                      Personal Information
                    </h6>
                    
                    <div className="row">
                      <div className="col-md-6 mb-3">
                        <label htmlFor="fullName" className="form-label fw-semibold">
                          <i className="bi bi-person me-1"></i>
                          Full Name <span className="text-danger">*</span>
                        </label>
                        <input
                          type="text"
                          className="form-control form-control-lg"
                          id="fullName"
                          name="fullName"
                          value={form.fullName}
                          onChange={handleChange}
                          placeholder="Enter your full name"
                          required
                          autoComplete="off"
                          style={{ borderRadius: '10px' }}
                        />
                      </div>

                      <div className="col-md-6 mb-3">
                        <label htmlFor="email" className="form-label fw-semibold">
                          <i className="bi bi-envelope me-1"></i>
                          Email Address <span className="text-danger">*</span>
                        </label>
                        <input
                          type="email"
                          className="form-control form-control-lg"
                          id="email"
                          name="email"
                          value={form.email}
                          onChange={handleChange}
                          placeholder="doctor@example.com"
                          required
                          autoComplete="off"
                          style={{ borderRadius: '10px' }}
                        />
                      </div>
                    </div>
                  </div>

                  {/* Professional Information */}
                  <div className="mb-3">
                    <h6 className="text-muted mb-2">
                      <i className="bi bi-hospital me-2"></i>
                      Professional Information
                    </h6>
                    
                    <div className="row">
                      <div className="col-md-6 mb-3">
                        <label htmlFor="specialtyId" className="form-label fw-semibold">
                          <i className="bi bi-clipboard-pulse me-1"></i>
                          Medical Specialty <span className="text-danger">*</span>
                        </label>
                        {loadingSpecialties ? (
                          <div className="d-flex align-items-center">
                            <div className="spinner-border spinner-border-sm me-2" role="status">
                              <span className="visually-hidden">Loading...</span>
                            </div>
                            <span className="text-muted">Loading specialties...</span>
                          </div>
                        ) : (
                          <select
                            className="form-select form-select-lg"
                            id="specialtyId"
                            name="specialtyId"
                            value={form.specialtyId}
                            onChange={handleChange}
                            required
                            style={{ borderRadius: '10px' }}
                          >
                            <option value={0}>Select a specialty</option>
                            {specialties.map((specialty) => (
                              <option key={specialty.specialtyId} value={specialty.specialtyId}>
                                {specialty.specialtyName}
                              </option>
                            ))}
                          </select>
                        )}
                      </div>

                      <div className="col-md-6 mb-3">
                        <label htmlFor="medicalLicenseNumber" className="form-label fw-semibold">
                          <i className="bi bi-card-text me-1"></i>
                          Medical License Number <span className="text-danger">*</span>
                        </label>
                        <input
                          type="text"
                          className="form-control form-control-lg"
                          id="medicalLicenseNumber"
                          name="medicalLicenseNumber"
                          value={form.medicalLicenseNumber}
                          onChange={handleChange}
                          placeholder="Enter license number"
                          required
                          autoComplete="off"
                          style={{ borderRadius: '10px' }}
                        />
                      </div>
                    </div>
                  </div>

                  {/* Access Credentials */}
                  <div className="mb-3">
                    <h6 className="text-muted mb-2">
                      <i className="bi bi-key me-2"></i>
                      Access Credentials
                    </h6>
                    
                    <div className="mb-3">
                      <label htmlFor="userName" className="form-label fw-semibold">
                        <i className="bi bi-at me-1"></i>
                        Username <span className="text-danger">*</span>
                      </label>
                      <input
                        type="text"
                        className="form-control form-control-lg"
                        id="userName"
                        name="userName"
                        value={form.userName}
                        onChange={handleChange}
                        placeholder="Choose a username"
                        required
                        autoComplete="off"
                        style={{ borderRadius: '10px' }}
                      />
                    </div>

                    <div className="row">
                      <div className="col-md-6 mb-3">
                        <label htmlFor="password" className="form-label fw-semibold">
                          <i className="bi bi-lock me-1"></i>
                          Password <span className="text-danger">*</span>
                        </label>
                        <input
                          type="password"
                          className="form-control form-control-lg"
                          id="password"
                          name="password"
                          value={form.password}
                          onChange={handleChange}
                          placeholder="Secure password"
                          required
                          autoComplete="off"
                          style={{ borderRadius: '10px' }}
                        />
                      </div>
                      
                      <div className="col-md-6 mb-3">
                        <label htmlFor="confirmPassword" className="form-label fw-semibold">
                          <i className="bi bi-lock-fill me-1"></i>
                          Confirm Password <span className="text-danger">*</span>
                        </label>
                        <input
                          type="password"
                          className="form-control form-control-lg"
                          id="confirmPassword"
                          name="confirmPassword"
                          value={form.confirmPassword}
                          onChange={handleChange}
                          placeholder="Repeat password"
                          required
                          autoComplete="off"
                          style={{ borderRadius: '10px' }}
                        />
                      </div>
                    </div>
                  </div>

                  <div className="d-grid gap-2 mb-3">
                    <button 
                      type="submit" 
                      className="btn btn-lg fw-bold"
                      disabled={isLoading}
                      style={{
                        background: 'linear-gradient(135deg, #405de6 0%, #5a67d8 100%)',
                        color: 'white',
                        border: 'none',
                        borderRadius: '10px',
                        padding: '15px'
                      }}
                    >
                      {isLoading ? (
                        <>
                          <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                          Registering Doctor...
                        </>
                      ) : (
                        <>
                          <i className="bi bi-person-plus me-2"></i>
                          Register Doctor
                        </>
                      )}
                    </button>
                  </div>

                  <div className="text-center">
                    <p className="mb-0 text-muted">
                      Already have an account?{' '}
                      <span
                        className="fw-semibold"
                        onClick={() => navigate('/')}
                        style={{ 
                          color: '#405de6', 
                          textDecoration: 'none',
                          cursor: 'pointer'
                        }}
                      >
                        Sign In
                      </span>
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

export default Register;