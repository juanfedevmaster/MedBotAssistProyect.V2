import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { Appointment, DoctorInfo } from '../types';
import ApiService from '../services/apiService';
import { API_ENDPOINTS } from '../config/endpoints';

interface HomeProps {
  doctorId: string | number | null;
  username?: string;
}

const Home: React.FC<HomeProps> = ({ doctorId, username }) => {
  const navigate = useNavigate();
  const { logout } = useAuth();
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [doctorInfo, setDoctorInfo] = useState<DoctorInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [currentWeekStart, setCurrentWeekStart] = useState(() => {
    const today = new Date();
    const dayOfWeek = today.getDay();
    const startOfWeek = new Date(today);
    startOfWeek.setDate(today.getDate() - dayOfWeek);
    return startOfWeek;
  });

  // Cargar citas médicas y información del doctor
  useEffect(() => {
    const fetchData = async () => {
      if (!doctorId) return;
      
      try {
        setLoading(true);
        
        // Cargar citas médicas
        const appointmentsResponse = await ApiService.authenticatedFetch(API_ENDPOINTS.APPOINTMENTS_GET_BY_DOCTOR(doctorId));
        const appointmentsData = await appointmentsResponse.json();
        setAppointments(appointmentsData || []);
        
        // Simular información del doctor (puedes reemplazar por API real si existe)
        setDoctorInfo({
          medicalLicenseNumber: "CARD12345",
          specialtyName: "Cardiología",
          userName: username || "jperez"
        });
        
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [doctorId, username]);

  // Generar días de la semana actual
  const generateWeekDays = () => {
    const days = [];
    for (let i = 0; i < 7; i++) {
      const day = new Date(currentWeekStart);
      day.setDate(currentWeekStart.getDate() + i);
      days.push(day);
    }
    return days;
  };

  // Obtener citas para un día específico
  const getAppointmentsForDay = (date: Date) => {
    const dateStr = date.toISOString().split('T')[0];
    return appointments.filter(apt => {
      const aptDate = new Date(apt.appointmentDate).toISOString().split('T')[0];
      return aptDate === dateStr;
    });
  };

  // Navegar semana anterior/siguiente
  const navigateWeek = (direction: 'prev' | 'next') => {
    const newWeekStart = new Date(currentWeekStart);
    if (direction === 'prev') {
      newWeekStart.setDate(newWeekStart.getDate() - 7);
    } else {
      newWeekStart.setDate(newWeekStart.getDate() + 7);
    }
    setCurrentWeekStart(newWeekStart);
  };

  const handleAttendAppointment = (appointmentId: number) => {
    // TODO: Implementar navegación a página de atender
    console.log('Atender cita:', appointmentId);
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const handleProfile = () => {
    navigate('/profile');
  };

  const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  const dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

  const formatWeekRange = () => {
    const weekEnd = new Date(currentWeekStart);
    weekEnd.setDate(currentWeekStart.getDate() + 6);
    
    const startMonth = monthNames[currentWeekStart.getMonth()];
    const endMonth = monthNames[weekEnd.getMonth()];
    const startDay = currentWeekStart.getDate();
    const endDay = weekEnd.getDate();
    const year = currentWeekStart.getFullYear();
    
    if (currentWeekStart.getMonth() === weekEnd.getMonth()) {
      return `${startMonth} ${startDay} - ${endDay}, ${year}`;
    } else {
      return `${startMonth} ${startDay} - ${endMonth} ${endDay}, ${year}`;
    }
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
                className="btn nav-link fw-bold"
                style={{ 
                  border: 'none', 
                  background: 'rgba(255,255,255,0.2)', 
                  color: '#fff',
                  borderRadius: '5px'
                }}
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

      {/* Contenido principal */}
      <div className="container-fluid p-4">
        <div className="row">
          {/* Calendario semanal - Columna izquierda y centro */}
          <div className="col-md-8">
            <div className="card shadow-lg border-0" style={{ background: 'rgba(255,255,255,0.95)' }}>
              <div className="card-header text-center" style={{ backgroundColor: '#405de6', color: 'white' }}>
                <div className="d-flex justify-content-between align-items-center">
                  <button 
                    className="btn btn-outline-light btn-sm"
                    onClick={() => navigateWeek('prev')}
                  >
                    <i className="bi bi-chevron-left"></i>
                  </button>
                  <h4 className="mb-0 fw-bold">
                    {formatWeekRange()}
                  </h4>
                  <button 
                    className="btn btn-outline-light btn-sm"
                    onClick={() => navigateWeek('next')}
                  >
                    <i className="bi bi-chevron-right"></i>
                  </button>
                </div>
              </div>
              <div className="card-body p-0">
                {loading ? (
                  <div className="text-center p-5">
                    <div className="spinner-border text-primary" role="status">
                      <span className="visually-hidden">Loading...</span>
                    </div>
                    <p className="mt-3 text-muted">Loading appointments...</p>
                  </div>
                ) : (
                  <>
                    {/* Headers de días de la semana */}
                    <div className="row g-0 border-bottom">
                      {generateWeekDays().map((day, index) => (
                        <div key={index} className="col text-center py-3 border-end">
                          <div className="fw-bold" style={{ color: '#405de6' }}>
                            {dayNames[day.getDay()]}
                          </div>
                          <div className="text-muted small">
                            {day.getDate()}/{day.getMonth() + 1}
                          </div>
                        </div>
                      ))}
                    </div>
                    
                    {/* Citas de cada día */}
                    <div className="row g-0" style={{ minHeight: '400px' }}>
                      {generateWeekDays().map((day, dayIndex) => {
                        const dayAppointments = getAppointmentsForDay(day);
                        const isToday = day.toDateString() === new Date().toDateString();
                        
                        return (
                          <div 
                            key={dayIndex} 
                            className={`col border-end p-2 ${isToday ? 'bg-primary bg-opacity-5' : ''}`}
                            style={{ fontSize: '0.9rem' }}
                          >
                            {dayAppointments.length === 0 ? (
                              <div className="text-center text-muted mt-4">
                                <i className="bi bi-calendar-x"></i>
                                <div className="small">No appointments</div>
                              </div>
                            ) : (
                              dayAppointments.map((apt, index) => (
                                <div 
                                  key={index}
                                  className="card mb-2 border-0 shadow-sm"
                                  style={{ fontSize: '0.85rem' }}
                                >
                                  <div className="card-body p-2">
                                    <div className="d-flex justify-content-between align-items-start mb-1">
                                      <span className="badge bg-primary">{apt.appointmentTime}</span>
                                      <span className={`badge ${apt.status === 'Confirmed' ? 'bg-success' : 'bg-warning'}`}>
                                        {apt.status}
                                      </span>
                                    </div>
                                    <div className="fw-bold text-dark mb-1" style={{ fontSize: '0.8rem' }}>
                                      {apt.patientName}
                                    </div>
                                    {apt.notes && (
                                      <div className="text-muted small mb-2">
                                        <i className="bi bi-note-text me-1"></i>
                                        {apt.notes}
                                      </div>
                                    )}
                                    <button
                                      className="btn btn-sm btn-outline-primary w-100"
                                      onClick={() => handleAttendAppointment(apt.appointmentId)}
                                      style={{ fontSize: '0.75rem' }}
                                    >
                                      <i className="bi bi-person-check me-1"></i>
                                      Attend
                                    </button>
                                  </div>
                                </div>
                              ))
                            )}
                          </div>
                        );
                      })}
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>

          {/* Tarjeta de información del doctor - Columna derecha */}
          <div className="col-md-4">
            <div className="card shadow-lg border-0" style={{ background: 'rgba(255,255,255,0.95)' }}>
              <div className="card-header text-center" style={{ backgroundColor: '#405de6', color: 'white' }}>
                <h5 className="mb-0 fw-bold">
                  <i className="bi bi-person-badge me-2"></i>
                  Doctor Information
                </h5>
              </div>
              <div className="card-body">
                {doctorInfo ? (
                  <div className="text-center">
                    <div className="mb-4">
                      <i className="bi bi-person-circle display-4" style={{ color: '#405de6' }}></i>
                    </div>
                    
                    <div className="mb-3">
                      <label className="form-label fw-bold text-muted small">USERNAME</label>
                      <div className="p-2 bg-light rounded">
                        <i className="bi bi-person me-2 text-primary"></i>
                        <span className="fw-bold">{doctorInfo.userName}</span>
                      </div>
                    </div>
                    
                    <div className="mb-3">
                      <label className="form-label fw-bold text-muted small">SPECIALTY</label>
                      <div className="p-2 bg-light rounded">
                        <i className="bi bi-heart-pulse me-2 text-danger"></i>
                        <span className="fw-bold">{doctorInfo.specialtyName}</span>
                      </div>
                    </div>
                    
                    <div className="mb-3">
                      <label className="form-label fw-bold text-muted small">MEDICAL LICENSE</label>
                      <div className="p-2 bg-light rounded">
                        <i className="bi bi-award me-2 text-warning"></i>
                        <span className="fw-bold">{doctorInfo.medicalLicenseNumber}</span>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-center">
                    <div className="spinner-border text-primary" role="status">
                      <span className="visually-hidden">Loading...</span>
                    </div>
                    <p className="mt-3 text-muted">Loading doctor information...</p>
                  </div>
                )}
              </div>
            </div>

            {/* Estadísticas rápidas */}
            <div className="card shadow-lg border-0 mt-4" style={{ background: 'rgba(255,255,255,0.95)' }}>
              <div className="card-header text-center" style={{ backgroundColor: '#405de6', color: 'white' }}>
                <h6 className="mb-0 fw-bold">
                  <i className="bi bi-graph-up me-2"></i>
                  Weekly Stats
                </h6>
              </div>
              <div className="card-body">
                <div className="row text-center">
                  <div className="col-12 mb-3">
                    <div className="p-3 bg-primary bg-opacity-10 rounded">
                      <i className="bi bi-calendar-week fs-4 text-primary"></i>
                      <div className="fw-bold fs-5 text-primary">
                        {generateWeekDays().reduce((total, day) => 
                          total + getAppointmentsForDay(day).length, 0
                        )}
                      </div>
                      <small className="text-muted">This Week</small>
                    </div>
                  </div>
                  <div className="col-12 mb-3">
                    <div className="p-3 bg-success bg-opacity-10 rounded">
                      <i className="bi bi-calendar-day fs-4 text-success"></i>
                      <div className="fw-bold fs-5 text-success">
                        {appointments.filter(apt => new Date(apt.appointmentDate).toDateString() === new Date().toDateString()).length}
                      </div>
                      <small className="text-muted">Today</small>
                    </div>
                  </div>
                  <div className="col-12">
                    <div className="p-3 bg-warning bg-opacity-10 rounded">
                      <i className="bi bi-check-circle fs-4 text-warning"></i>
                      <div className="fw-bold fs-5 text-warning">
                        {generateWeekDays().reduce((total, day) => 
                          total + getAppointmentsForDay(day).filter(apt => apt.status === 'Confirmed').length, 0
                        )}
                      </div>
                      <small className="text-muted">Confirmed</small>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
