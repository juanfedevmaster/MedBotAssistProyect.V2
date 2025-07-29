import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Appointment } from '../types';
import ApiService from '../services/apiService';
import TokenManager from '../utils/tokenManager';

interface AppointmentsProps {
  doctorId: string | number | null;
  username?: string;
}

const Appointments: React.FC<AppointmentsProps> = ({ doctorId, username }) => {
  const navigate = useNavigate();
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [viewMode, setViewMode] = useState<'list' | 'calendar'>('list');
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedAppointment, setSelectedAppointment] = useState<Appointment | null>(null);
  const [isNotesModalOpen, setIsNotesModalOpen] = useState(false);
  
  // Estados para IA
  const [isEditMode, setIsEditMode] = useState(false);
  const [editNotes, setEditNotes] = useState('');
  const [showAiModal, setShowAiModal] = useState(false);
  const [aiLoading, setAiLoading] = useState(false);
  const [saving, setSaving] = useState(false);

  // Estados para crear nueva cita
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [selectedDateForNewAppointment, setSelectedDateForNewAppointment] = useState('');
  const [patients, setPatients] = useState<any[]>([]);
  const [loadingPatients, setLoadingPatients] = useState(false);
  const [newAppointment, setNewAppointment] = useState({
    patientId: '',
    patientName: '',
    appointmentTime: '',
    status: 'pending',
    notes: ''
  });
  const [creatingAppointment, setCreatingAppointment] = useState(false);

  // Estados para confirmar cita
  const [isConfirmModalOpen, setIsConfirmModalOpen] = useState(false);
  const [appointmentToConfirm, setAppointmentToConfirm] = useState<Appointment | null>(null);
  const [confirming, setConfirming] = useState(false);

  // Estados para editar cita
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [appointmentToEdit, setAppointmentToEdit] = useState<Appointment | null>(null);
  const [editAppointmentData, setEditAppointmentData] = useState({
    appointmentDate: '',
    appointmentTime: '',
    status: 'Pending',
    notes: ''
  });
  const [updatingAppointment, setUpdatingAppointment] = useState(false);

  // Cargar citas del doctor
  useEffect(() => {
    const loadAppointments = async () => {
      if (!doctorId) {
        setError('Doctor ID not found');
        setLoading(false);
        return;
      }

      const isAuthenticated = TokenManager.isAuthenticated();
      if (!isAuthenticated) {
        setError('User not authenticated');
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError('');
        const response = await ApiService.getAppointmentsByDoctor(doctorId);
        const appointmentsData = await response.json();
        setAppointments(appointmentsData);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load appointments');
      } finally {
        setLoading(false);
      }
    };

    loadAppointments();
  }, [doctorId]);

  // Función para manejar la visualización de notas
  const handleViewNotes = (appointment: Appointment) => {
    setSelectedAppointment(appointment);
    setEditNotes(appointment.notes || '');
    setIsEditMode(false); // Asegurar que inicie en modo lectura
    setIsNotesModalOpen(true);
  };

  // Función para cerrar el modal y resetear estados
  const handleCloseModal = () => {
    setIsNotesModalOpen(false);
    setIsEditMode(false);
    setSelectedAppointment(null);
    setEditNotes('');
    setError('');
    setShowAiModal(false);
    setSaving(false);
  };

  // Funciones para el modo de edición
  const handleEditMode = () => {
    setIsEditMode(true);
  };

  const handleCancelEdit = () => {
    setIsEditMode(false);
    if (selectedAppointment) {
      setEditNotes(selectedAppointment.notes || '');
    }
  };

  const handleSaveNotes = async () => {
    if (!selectedAppointment) return;
    
    try {
      setSaving(true);
      setError('');
      
      // Preparar los datos para el endpoint PUT
      const appointmentUpdateData = {
        appointmentId: selectedAppointment.appointmentId,
        patientId: selectedAppointment.patientId,
        patientName: selectedAppointment.patientName || '',
        doctorId: selectedAppointment.doctorId,
        appointmentDate: selectedAppointment.appointmentDate,
        appointmentTime: selectedAppointment.appointmentTime,
        status: selectedAppointment.status,
        notes: editNotes || ''
      };
      
      console.log('Sending appointment update:', appointmentUpdateData);
      
      try {
        // Intentar llamar al endpoint PUT para actualizar la cita
        const response = await ApiService.updateAppointment(
          selectedAppointment.appointmentId,
          appointmentUpdateData
        );
        
        if (response.ok) {
          // Actualizar la lista local solo si la API fue exitosa
          setAppointments(prev => prev.map(apt => 
            apt.appointmentId === selectedAppointment.appointmentId 
              ? { ...apt, notes: editNotes }
              : apt
          ));
          
          setSelectedAppointment({ ...selectedAppointment, notes: editNotes });
          setIsEditMode(false);
          
          console.log('Appointment notes updated successfully via API');
        } else {
          const errorText = await response.text();
          console.error('API Error Response:', errorText);
          throw new Error(`API returned ${response.status}: ${errorText}`);
        }
      } catch (apiError) {
        console.warn('API update failed, updating locally only:', apiError);
        
        // Si la API falla, actualizar solo localmente
        setAppointments(prev => prev.map(apt => 
          apt.appointmentId === selectedAppointment.appointmentId 
            ? { ...apt, notes: editNotes }
            : apt
        ));
        
        setSelectedAppointment({ ...selectedAppointment, notes: editNotes });
        setIsEditMode(false);
        
        // Mostrar mensaje informativo en lugar de error
        setError('Notes updated locally. API endpoint may not be available.');
        
        // Limpiar el mensaje después de 3 segundos
        setTimeout(() => setError(''), 3000);
      }
    } catch (error) {
      console.error('Error updating notes:', error);
      setError(`Error updating notes: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setSaving(false);
    }
  };

  // Funciones para IA
  const handleShowAiModal = () => {
    if (!editNotes.trim()) {
      setError('Please enter some text before using AI assistance');
      return;
    }
    setShowAiModal(true);
  };

  const handleConfirmAiImprovement = () => {
    setShowAiModal(false);
    handleAiImproveNotes();
  };

  const handleCancelAiImprovement = () => {
    setShowAiModal(false);
  };

  const handleAiImproveNotes = async () => {
    if (!editNotes.trim()) return;
    
    setAiLoading(true);
    try {
      // Preparar el mensaje para el agente de IA exactamente como en PatientNotes
      const message = `Ayudame a redactar mejor esta nota: ${editNotes}, solo responde con la nota mejorada, sin saludos, ni mensajes adicionales, solo el mensaje mejorado`;
      
      const response = await ApiService.aiApiFetch(`http://localhost:8000/api/v1/agent/chat`, {
        method: 'POST',
        body: JSON.stringify({ message })
      });
      
      const data = await response.json();
      // Actualizar el campo de notas con la respuesta del agente igual que PatientNotes
      if (data.response) {
        setEditNotes(data.response);
      } else if (data.message) {
        setEditNotes(data.message);
      } else {
        setEditNotes(data);
      }
    } catch (error) {
      console.error('Error improving notes with AI:', error);
      setError('Error improving notes with AI');
    } finally {
      setAiLoading(false);
    }
  };

  // Funciones para crear nuevas citas
  const loadPatients = async () => {
    try {
      setLoadingPatients(true);
      const response = await ApiService.getAllPatients();
      const patientsData = await response.json();
      setPatients(patientsData);
    } catch (error) {
      console.error('Error loading patients:', error);
      setError('Error loading patients');
    } finally {
      setLoadingPatients(false);
    }
  };

  const handleCreateAppointmentClick = (selectedDate?: string) => {
    const dateToUse = selectedDate || new Date().toISOString().split('T')[0];
    setSelectedDateForNewAppointment(dateToUse);
    setIsCreateModalOpen(true);
    loadPatients();
  };

  const handleCloseCreateModal = () => {
    setIsCreateModalOpen(false);
    setNewAppointment({
      patientId: '',
      patientName: '',
      appointmentTime: '',
      status: 'pending',
      notes: ''
    });
    setSelectedDateForNewAppointment('');
    setError('');
  };

  const handlePatientSelect = (patientId: string) => {
    const selectedPatient = patients.find(p => p.patientId.toString() === patientId);
    if (selectedPatient) {
      setNewAppointment(prev => ({
        ...prev,
        patientId: patientId,
        patientName: selectedPatient.name
      }));
    }
  };

  const handleCreateAppointment = async () => {
    if (!newAppointment.patientId || !newAppointment.appointmentTime) {
      setError('Please select a patient and appointment time');
      return;
    }

    try {
      setCreatingAppointment(true);
      setError('');

      const appointmentData = {
        appointmentId: 0,
        patientId: parseInt(newAppointment.patientId),
        patientName: newAppointment.patientName,
        doctorId: doctorId,
        appointmentDate: selectedDateForNewAppointment,
        appointmentTime: newAppointment.appointmentTime,
        status: newAppointment.status,
        notes: newAppointment.notes || ''
      };

      console.log('Creating appointment:', appointmentData);

      const response = await ApiService.createAppointment(appointmentData);
      
      if (response.ok) {
        const createdAppointment = await response.json();
        
        // Agregar la nueva cita a la lista local
        setAppointments(prev => [...prev, createdAppointment]);
        
        handleCloseCreateModal();
        console.log('Appointment created successfully');
      } else {
        const errorText = await response.text();
        console.error('API Error Response:', errorText);
        throw new Error(`Failed to create appointment: ${response.status} - ${errorText}`);
      }
    } catch (error) {
      console.error('Error creating appointment:', error);
      setError(`Error creating appointment: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setCreatingAppointment(false);
    }
  };

  // Funciones para confirmar cita médica
  const isAppointmentConfirmable = (appointment: Appointment): boolean => {
    const appointmentDateTime = new Date(`${appointment.appointmentDate}T${appointment.appointmentTime}`);
    const now = new Date();
    return appointmentDateTime >= now && appointment.status.toLowerCase() !== 'confirmed';
  };

  const handleConfirmAppointmentClick = (appointment: Appointment) => {
    setAppointmentToConfirm(appointment);
    setIsConfirmModalOpen(true);
  };

  const handleCloseConfirmModal = () => {
    setIsConfirmModalOpen(false);
    setAppointmentToConfirm(null);
    setError('');
  };

  const handleConfirmAppointment = async () => {
    if (!appointmentToConfirm) return;

    try {
      setConfirming(true);
      setError('');

      // Preparar los datos para el endpoint PUT con status "Confirmed"
      const appointmentUpdateData = {
        appointmentId: appointmentToConfirm.appointmentId,
        patientId: appointmentToConfirm.patientId,
        patientName: appointmentToConfirm.patientName || '',
        doctorId: appointmentToConfirm.doctorId,
        appointmentDate: appointmentToConfirm.appointmentDate,
        appointmentTime: appointmentToConfirm.appointmentTime,
        status: 'Confirmed',
        notes: appointmentToConfirm.notes || ''
      };

      console.log('Confirming appointment:', appointmentUpdateData);

      try {
        // Llamar al endpoint PUT para actualizar la cita
        const response = await ApiService.updateAppointment(
          appointmentToConfirm.appointmentId,
          appointmentUpdateData
        );

        if (response.ok) {
          // Actualizar la lista local solo si la API fue exitosa
          setAppointments(prev => prev.map(apt => 
            apt.appointmentId === appointmentToConfirm.appointmentId 
              ? { ...apt, status: 'Confirmed' }
              : apt
          ));

          handleCloseConfirmModal();
          console.log('Appointment confirmed successfully via API');
        } else {
          const errorText = await response.text();
          console.error('API Error Response:', errorText);
          throw new Error(`API returned ${response.status}: ${errorText}`);
        }
      } catch (apiError) {
        console.warn('API confirmation failed, updating locally only:', apiError);
        
        // Si la API falla, actualizar solo localmente
        setAppointments(prev => prev.map(apt => 
          apt.appointmentId === appointmentToConfirm.appointmentId 
            ? { ...apt, status: 'Confirmed' }
            : apt
        ));

        handleCloseConfirmModal();
        
        // Mostrar mensaje informativo en lugar de error
        setError('Appointment confirmed locally. API endpoint may not be available.');
        
        // Limpiar el mensaje después de 3 segundos
        setTimeout(() => setError(''), 3000);
      }
    } catch (error) {
      console.error('Error confirming appointment:', error);
      setError(`Error confirming appointment: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setConfirming(false);
    }
  };

  // Funciones para editar cita médica
  const handleEditAppointmentClick = (appointment: Appointment) => {
    setAppointmentToEdit(appointment);
    setEditAppointmentData({
      appointmentDate: appointment.appointmentDate,
      appointmentTime: appointment.appointmentTime,
      status: 'Pending', // Siempre será Pending como especifica el usuario
      notes: appointment.notes || ''
    });
    setIsEditModalOpen(true);
  };

  const handleCloseEditModal = () => {
    setIsEditModalOpen(false);
    setAppointmentToEdit(null);
    setEditAppointmentData({
      appointmentDate: '',
      appointmentTime: '',
      status: 'Pending',
      notes: ''
    });
    setError('');
  };

  const handleUpdateAppointment = async () => {
    if (!appointmentToEdit || !editAppointmentData.appointmentDate || !editAppointmentData.appointmentTime) {
      setError('Please fill in all required fields');
      return;
    }

    try {
      setUpdatingAppointment(true);
      setError('');

      // Preparar los datos para el endpoint PUT
      const appointmentUpdateData = {
        appointmentId: appointmentToEdit.appointmentId,
        patientId: appointmentToEdit.patientId,
        patientName: appointmentToEdit.patientName || '',
        doctorId: appointmentToEdit.doctorId,
        appointmentDate: editAppointmentData.appointmentDate,
        appointmentTime: editAppointmentData.appointmentTime,
        status: 'Pending', // Siempre Pending como especifica el usuario
        notes: editAppointmentData.notes || ''
      };

      console.log('Updating appointment:', appointmentUpdateData);

      try {
        // Llamar al endpoint PUT para actualizar la cita
        const response = await ApiService.updateAppointment(
          appointmentToEdit.appointmentId,
          appointmentUpdateData
        );

        if (response.ok) {
          // Actualizar la lista local solo si la API fue exitosa
          setAppointments(prev => prev.map(apt => 
            apt.appointmentId === appointmentToEdit.appointmentId 
              ? { 
                  ...apt, 
                  appointmentDate: editAppointmentData.appointmentDate,
                  appointmentTime: editAppointmentData.appointmentTime,
                  status: 'Pending',
                  notes: editAppointmentData.notes
                }
              : apt
          ));

          handleCloseEditModal();
          console.log('Appointment updated successfully via API');
        } else {
          const errorText = await response.text();
          console.error('API Error Response:', errorText);
          throw new Error(`API returned ${response.status}: ${errorText}`);
        }
      } catch (apiError) {
        console.warn('API update failed, updating locally only:', apiError);
        
        // Si la API falla, actualizar solo localmente
        setAppointments(prev => prev.map(apt => 
          apt.appointmentId === appointmentToEdit.appointmentId 
            ? { 
                ...apt, 
                appointmentDate: editAppointmentData.appointmentDate,
                appointmentTime: editAppointmentData.appointmentTime,
                status: 'Pending',
                notes: editAppointmentData.notes
              }
            : apt
        ));

        handleCloseEditModal();
        
        // Mostrar mensaje informativo en lugar de error
        setError('Appointment updated locally. API endpoint may not be available.');
        
        // Limpiar el mensaje después de 3 segundos
        setTimeout(() => setError(''), 3000);
      }
    } catch (error) {
      console.error('Error updating appointment:', error);
      setError(`Error updating appointment: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setUpdatingAppointment(false);
    }
  };

  // Filtrado de citas
  const filteredAppointments = appointments.filter(appointment => {
    const matchesSearch = appointment.patientName?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         appointment.patientId.toString().includes(searchTerm) ||
                         appointment.appointmentId.toString().includes(searchTerm) ||
                         appointment.notes.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = statusFilter === '' || appointment.status.toLowerCase() === statusFilter.toLowerCase();
    
    return matchesSearch && matchesStatus;
  });

  // Funciones del calendario
  const generateCalendarDays = () => {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    const firstDay = new Date(year, month, 1);
    const startCalendar = new Date(firstDay);
    startCalendar.setDate(startCalendar.getDate() - firstDay.getDay());
    
    const days = [];
    const current = new Date(startCalendar);
    
    for (let i = 0; i < 42; i++) { // 6 semanas × 7 días
      days.push({
        day: current.getDate(),
        date: current.getDate().toString(),
        fullDate: new Date(current), // Almacenar la fecha completa
        appointments: [],
        isToday: false,
        isSelected: false,
        isCurrentMonth: current.getMonth() === currentDate.getMonth()
      });
      current.setDate(current.getDate() + 1);
    }
    
    return days;
  };

  const getMonthName = (monthIndex: number) => {
    const months = [
      'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
      'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ];
    return months[monthIndex];
  };

  const navigateMonth = (direction: 'prev' | 'next') => {
    setCurrentDate(prev => {
      const newDate = new Date(prev);
      if (direction === 'prev') {
        newDate.setMonth(newDate.getMonth() - 1);
      } else {
        newDate.setMonth(newDate.getMonth() + 1);
      }
      return newDate;
    });
  };

  // Mostrar estado de carga
  if (loading) {
    return (
      <div style={{ minHeight: '100vh', background: 'linear-gradient(180deg, #ffffff, #405de6)' }}>
        <div className="d-flex justify-content-center align-items-center" style={{ minHeight: '100vh' }}>
          <div className="text-center text-white">
            <div className="spinner-border mb-3" role="status">
              <span className="visually-hidden">Loading...</span>
            </div>
            <h5>Loading appointments...</h5>
          </div>
        </div>
      </div>
    );
  }

  // Mostrar error
  if (error) {
    return (
      <div style={{ minHeight: '100vh', background: 'linear-gradient(180deg, #ffffff, #405de6)' }}>
        <div className="d-flex justify-content-center align-items-center" style={{ minHeight: '100vh' }}>
          <div className="text-center text-white">
            <div className="alert alert-danger" role="alert">
              <i className="bi bi-exclamation-triangle me-2"></i>
              {error}
            </div>
            <button 
              className="btn btn-outline-light" 
              onClick={() => window.location.reload()}
            >
              <i className="bi bi-arrow-clockwise me-2"></i>
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Estadísticas de citas
  const totalAppointments = appointments.length;
  const pendingAppointments = appointments.filter(apt => apt.status.toLowerCase() === 'pending').length;
  const confirmedAppointments = appointments.filter(apt => apt.status.toLowerCase() === 'confirmed').length;
  const completedAppointments = appointments.filter(apt => apt.status.toLowerCase() === 'completed').length;

  return (
    <div style={{ minHeight: '100vh', background: 'linear-gradient(180deg, #ffffff, #405de6)' }}>
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
                    onClick={() => navigate('/profile')}
                  >
                    <i className="bi bi-person me-2"></i>
                    Profile
                  </button>
                </li>
                <li><hr className="dropdown-divider" /></li>
                <li>
                  <button 
                    className="dropdown-item d-flex align-items-center text-danger" 
                    onClick={() => {
                      if (window.confirm('¿Estás seguro de que deseas cerrar sesión?')) {
                        navigate('/login');
                      }
                    }}
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

      <div className="container py-4">
        <div className="row justify-content-center">
          <div className="col-12">
            {/* Header */}
            <div className="d-flex justify-content-between align-items-center mb-4">
              <div>
                <h2 className="mb-1" style={{ color: '#405de6' }}>
                  <i className="bi bi-calendar-check me-2"></i>
                  Medical Appointments
                </h2>
                <p className="mb-0" style={{ color: '#405de6', opacity: 0.8 }}>Manage and view your scheduled appointments</p>
              </div>
              <button 
                className="btn"
                onClick={() => handleCreateAppointmentClick()}
                style={{
                  backgroundColor: '#405de6',
                  color: 'white',
                  border: '1px solid #405de6',
                  fontWeight: 'bold'
                }}
              >
                <i className="bi bi-calendar-plus me-2"></i>
                New Appointment
              </button>
            </div>

            {/* Estadísticas */}
            <div className="row mb-4">
              <div className="col-md-3 mb-3">
                <div className="card border-0 shadow-sm h-100">
                  <div className="card-body text-center">
                    <i className="bi bi-calendar3 text-primary mb-2" style={{ fontSize: '2rem' }}></i>
                    <h3 className="mb-1">{totalAppointments}</h3>
                    <small className="text-muted">Total Appointments</small>
                  </div>
                </div>
              </div>
              <div className="col-md-3 mb-3">
                <div className="card border-0 shadow-sm h-100">
                  <div className="card-body text-center">
                    <i className="bi bi-clock-history text-warning mb-2" style={{ fontSize: '2rem' }}></i>
                    <h3 className="mb-1">{pendingAppointments}</h3>
                    <small className="text-muted">Pending</small>
                  </div>
                </div>
              </div>
              <div className="col-md-3 mb-3">
                <div className="card border-0 shadow-sm h-100">
                  <div className="card-body text-center">
                    <i className="bi bi-check-circle text-success mb-2" style={{ fontSize: '2rem' }}></i>
                    <h3 className="mb-1">{confirmedAppointments}</h3>
                    <small className="text-muted">Confirmed</small>
                  </div>
                </div>
              </div>
              <div className="col-md-3 mb-3">
                <div className="card border-0 shadow-sm h-100">
                  <div className="card-body text-center">
                    <i className="bi bi-check2-all text-info mb-2" style={{ fontSize: '2rem' }}></i>
                    <h3 className="mb-1">{completedAppointments}</h3>
                    <small className="text-muted">Completed</small>
                  </div>
                </div>
              </div>
            </div>

            {/* Card principal */}
            <div className="card border-0 shadow-lg">
              <div className="card-header bg-white border-0 py-3">
                <div className="row align-items-center">
                  <div className="col-md-6">
                    <h5 className="mb-0">
                      <i className="bi bi-list-check me-2 text-primary"></i>
                      Appointments List
                    </h5>
                  </div>
                  <div className="col-md-6">
                    <div className="d-flex justify-content-end gap-2">
                      <button 
                        className={`btn ${viewMode === 'list' ? 'btn-primary' : 'btn-outline-primary'}`}
                        onClick={() => setViewMode('list')}
                      >
                        <i className="bi bi-list-ul me-1"></i>
                        List
                      </button>
                      <button 
                        className={`btn ${viewMode === 'calendar' ? 'btn-primary' : 'btn-outline-primary'}`}
                        onClick={() => setViewMode('calendar')}
                      >
                        <i className="bi bi-calendar3 me-1"></i>
                        Calendar
                      </button>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="card-body">
                {/* Filtros */}
                <div className="row mb-4">
                  <div className="col-md-8">
                    <div className="input-group">
                      <span className="input-group-text">
                        <i className="bi bi-search"></i>
                      </span>
                      <input
                        type="text"
                        className="form-control"
                        placeholder="Search by patient name, ID, appointment ID, or notes..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                      />
                    </div>
                  </div>
                  <div className="col-md-4">
                    <select
                      className="form-select"
                      value={statusFilter}
                      onChange={(e) => setStatusFilter(e.target.value)}
                    >
                      <option value="">All Status</option>
                      <option value="pending">Pending</option>
                      <option value="confirmed">Confirmed</option>
                      <option value="completed">Completed</option>
                      <option value="cancelled">Cancelled</option>
                    </select>
                  </div>
                </div>

                {/* Vista condicional: Lista o Calendario */}
                {viewMode === 'list' ? (
                  /* Tabla de citas */
                  <div className="table-responsive">
                    <table className="table table-hover">
                      <thead style={{ backgroundColor: '#405de6', color: 'white' }}>
                        <tr>
                          <th>Time</th>
                          <th>Patient</th>
                          <th>Patient ID</th>
                          <th>Appointment ID</th>
                          <th>Status</th>
                          <th>Notes</th>
                          <th>Attend Patient</th>
                          <th>Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {filteredAppointments.length === 0 ? (
                          <tr>
                            <td colSpan={8} className="text-center py-4">
                              <div className="text-muted">
                                <i className="bi bi-calendar-x" style={{ fontSize: '3rem' }}></i>
                                <p className="mt-2 mb-0">No appointments found</p>
                                <small>Try adjusting your search criteria</small>
                              </div>
                            </td>
                          </tr>
                        ) : (
                          filteredAppointments.map((appointment) => (
                            <tr key={appointment.appointmentId}>
                              <td>
                                <strong>{appointment.appointmentTime}</strong>
                                <br />
                                <small className="text-muted">{appointment.appointmentDate}</small>
                              </td>
                              <td>
                                <div className="d-flex align-items-center">
                                  <i className="bi bi-person-circle me-2 text-primary" style={{ fontSize: '1.2rem' }}></i>
                                  <div>
                                    <strong>{appointment.patientName || 'Unknown Patient'}</strong>
                                  </div>
                                </div>
                              </td>
                              <td>
                                <span className="badge bg-primary">#{appointment.patientId}</span>
                              </td>
                              <td>
                                <span className="badge bg-secondary">#{appointment.appointmentId}</span>
                              </td>
                              <td>
                                <span className={`badge ${
                                  appointment.status.toLowerCase() === 'confirmed' ? 'bg-success' :
                                  appointment.status.toLowerCase() === 'pending' ? 'bg-warning' :
                                  appointment.status.toLowerCase() === 'completed' ? 'bg-info' :
                                  'bg-danger'
                                }`}>
                                  {appointment.status}
                                </span>
                              </td>
                              <td>
                                <span className="text-muted">
                                  {appointment.notes.length > 50 
                                    ? `${appointment.notes.substring(0, 50)}...` 
                                    : appointment.notes || 'No notes'}
                                </span>
                              </td>
                              <td>
                                {(() => {
                                  const appointmentDate = new Date(appointment.appointmentDate);
                                  const today = new Date();
                                  today.setHours(0, 0, 0, 0); // Resetear horas para comparar solo fecha
                                  appointmentDate.setHours(0, 0, 0, 0); // Resetear horas para comparar solo fecha
                                  
                                  // Solo mostrar botón de atender si la cita está confirmada y es hoy o en el futuro
                                  if (appointment.status.toLowerCase() === 'confirmed' && appointmentDate >= today) {
                                    return (
                                      <button 
                                        className="btn btn-sm btn-primary"
                                        onClick={() => navigate(`/patients/notes/${appointment.patientId}?appointmentId=${appointment.appointmentId}`)}
                                        title="Attend Patient"
                                      >
                                        <i className="bi bi-person-check me-1"></i>
                                        Attend
                                      </button>
                                    );
                                  }
                                  return (
                                    <span className="text-muted small">
                                      {appointment.status.toLowerCase() !== 'confirmed' ? 'Not confirmed' : 'Past appointment'}
                                    </span>
                                  );
                                })()}
                              </td>
                              <td>
                                <div className="btn-group btn-group-sm">
                                  <button 
                                    className="btn btn-outline-primary"
                                    onClick={() => handleViewNotes(appointment)}
                                    title="View/Add Notes"
                                  >
                                    <i className="bi bi-file-medical"></i>
                                  </button>
                                  {/* Botón de confirmar cita - solo para citas futuras y no confirmadas */}
                                  {isAppointmentConfirmable(appointment) && (
                                    <button 
                                      className="btn btn-outline-success"
                                      onClick={() => handleConfirmAppointmentClick(appointment)}
                                      title="Confirm Appointment"
                                    >
                                      <i className="bi bi-check-circle"></i>
                                    </button>
                                  )}
                                  {(() => {
                                    const appointmentDate = new Date(appointment.appointmentDate);
                                    const today = new Date();
                                    today.setHours(0, 0, 0, 0); // Resetear horas para comparar solo fecha
                                    appointmentDate.setHours(0, 0, 0, 0); // Resetear horas para comparar solo fecha
                                    
                                    // Solo mostrar botón de editar si la cita es hoy o en el futuro
                                    if (appointmentDate >= today) {
                                      return (
                                        <button 
                                          className="btn btn-outline-secondary"
                                          title="Edit Appointment"
                                          onClick={() => handleEditAppointmentClick(appointment)}
                                        >
                                          <i className="bi bi-pencil"></i>
                                        </button>
                                      );
                                    }
                                    return null;
                                  })()}
                                </div>
                              </td>
                            </tr>
                          ))
                        )}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  /* Vista de Calendario */
                  <div>
                    {/* Navegación del calendario */}
                    <div className="d-flex justify-content-between align-items-center mb-4">
                      <button 
                        className="btn btn-outline-primary"
                        onClick={() => navigateMonth('prev')}
                      >
                        <i className="bi bi-chevron-left"></i> Previous
                      </button>
                      <h3 className="mb-0">
                        {getMonthName(currentDate.getMonth())} {currentDate.getFullYear()}
                      </h3>
                      <button 
                        className="btn btn-outline-primary"
                        onClick={() => navigateMonth('next')}
                      >
                        Next <i className="bi bi-chevron-right"></i>
                      </button>
                    </div>

                    {/* Grid del calendario */}
                    <div className="calendar-grid" style={{ 
                      display: 'grid', 
                      gridTemplateColumns: 'repeat(7, 1fr)', 
                      gap: '1px',
                      backgroundColor: '#dee2e6',
                      border: '1px solid #dee2e6',
                      borderRadius: '0.375rem',
                      overflow: 'hidden'
                    }}>
                      {/* Encabezados de días */}
                      {['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'].map(day => (
                        <div key={day} className="text-center fw-bold p-2" style={{ 
                          backgroundColor: '#405de6', 
                          color: 'white' 
                        }}>
                          {day}
                        </div>
                      ))}
                      
                      {/* Días del calendario */}
                      {generateCalendarDays().map((day) => {
                        const dayAppointments = appointments.filter(appointment => {
                          const appointmentDate = new Date(appointment.appointmentDate);
                          const dayDate = day.fullDate;
                          
                          // Comparar solo año, mes y día (ignorar hora)
                          return appointmentDate.getDate() === dayDate.getDate() &&
                                 appointmentDate.getMonth() === dayDate.getMonth() &&
                                 appointmentDate.getFullYear() === dayDate.getFullYear();
                        });

                        return (
                          <div 
                            key={`${day.day}-${day.isCurrentMonth}`}
                            className="calendar-day p-2"
                            style={{ 
                              backgroundColor: 'white',
                              minHeight: '80px',
                              opacity: day.isCurrentMonth ? 1 : 0.3,
                              cursor: day.isCurrentMonth && day.fullDate >= new Date() ? 'pointer' : 'default',
                              position: 'relative',
                              border: day.isCurrentMonth && day.fullDate >= new Date() ? '2px solid transparent' : '1px solid #e9ecef'
                            }}
                            onClick={() => {
                              // Solo permitir selección de fechas actuales o futuras
                              if (day.isCurrentMonth && day.fullDate >= new Date()) {
                                const selectedDate = day.fullDate.toISOString().split('T')[0];
                                handleCreateAppointmentClick(selectedDate);
                              }
                            }}
                            onMouseEnter={(e) => {
                              if (day.isCurrentMonth && day.fullDate >= new Date()) {
                                e.currentTarget.style.border = '2px solid #405de6';
                                e.currentTarget.style.backgroundColor = '#f8f9ff';
                              }
                            }}
                            onMouseLeave={(e) => {
                              if (day.isCurrentMonth && day.fullDate >= new Date()) {
                                e.currentTarget.style.border = '2px solid transparent';
                                e.currentTarget.style.backgroundColor = 'white';
                              }
                            }}
                          >
                            <div className="fw-bold mb-1">{day.day}</div>
                            {dayAppointments.length > 0 && (
                              <div>
                                <small className="badge bg-primary mb-1">
                                  {dayAppointments.length} cita{dayAppointments.length > 1 ? 's' : ''}
                                </small>
                                {dayAppointments.slice(0, 2).map((appointment) => (
                                  <div 
                                    key={appointment.appointmentId}
                                    className="small text-truncate"
                                    style={{ fontSize: '0.7rem' }}
                                    title={`${appointment.appointmentTime} - ${appointment.patientName || 'Patient'}`}
                                  >
                                    <i className="bi bi-clock me-1"></i>
                                    {appointment.appointmentTime}
                                    <br />
                                    <i className="bi bi-person me-1"></i>
                                    {appointment.patientName || 'Patient'}
                                  </div>
                                ))}
                                {dayAppointments.length > 2 && (
                                  <small className="text-muted">
                                    +{dayAppointments.length - 2} más
                                  </small>
                                )}
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}

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

      {/* Modal de notas */}
      {isNotesModalOpen && selectedAppointment && (
        <div className="modal show d-block" tabIndex={-1} style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog modal-lg">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">
                  <i className="bi bi-file-medical me-2"></i>
                  Appointment Notes
                </h5>
                <button 
                  type="button" 
                  className="btn-close"
                  onClick={handleCloseModal}
                ></button>
              </div>
              <div className="modal-body">
                <div className="mb-3">
                  <strong>Patient:</strong> {selectedAppointment.patientName || 'Unknown Patient'}
                </div>
                <div className="mb-3">
                  <strong>Date:</strong> {selectedAppointment.appointmentDate} at {selectedAppointment.appointmentTime}
                </div>
                <div className="mb-3">
                  <strong>Status:</strong> 
                  <span className={`badge ms-2 ${
                    selectedAppointment.status.toLowerCase() === 'confirmed' ? 'bg-success' :
                    selectedAppointment.status.toLowerCase() === 'pending' ? 'bg-warning' :
                    selectedAppointment.status.toLowerCase() === 'completed' ? 'bg-info' :
                    'bg-danger'
                  }`}>
                    {selectedAppointment.status}
                  </span>
                </div>
                <div className="mb-3">
                  <label className="form-label"><strong>Notes:</strong></label>
                  {isEditMode ? (
                    <div className="position-relative">
                      <textarea 
                        className="form-control" 
                        rows={5} 
                        value={editNotes}
                        onChange={(e) => setEditNotes(e.target.value)}
                        placeholder="Enter notes for this appointment"
                        disabled={aiLoading || saving}
                        style={{
                          backgroundColor: (aiLoading || saving) ? '#f8f9fa' : 'white',
                          cursor: (aiLoading || saving) ? 'not-allowed' : 'text'
                        }}
                      />
                      {/* Botón flotante de IA */}
                      <button
                        type="button"
                        className="btn btn-primary btn-sm position-absolute"
                        style={{
                          bottom: '8px',
                          right: '8px',
                          width: '32px',
                          height: '32px',
                          borderRadius: '50%',
                          padding: '0',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          backgroundColor: (aiLoading || saving) ? '#6c757d' : '#405de6',
                          border: 'none',
                          boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                        }}
                        onClick={handleShowAiModal}
                        disabled={aiLoading || saving || !editNotes.trim()}
                        title={aiLoading ? "AI is working..." : saving ? "Saving..." : "Improve medical note"}
                      >
                        {aiLoading ? (
                          <span className="spinner-border spinner-border-sm" role="status" style={{ width: '14px', height: '14px' }}>
                            <span className="visually-hidden">Loading...</span>
                          </span>
                        ) : (
                          <i className="bi bi-robot" style={{ fontSize: '14px' }}></i>
                        )}
                      </button>
                    </div>
                  ) : (
                    <textarea 
                      className="form-control" 
                      rows={5} 
                      value={selectedAppointment.notes || ''}
                      readOnly
                      placeholder="No notes available for this appointment"
                    />
                  )}
                </div>
              </div>
              <div className="modal-footer">
                <button 
                  type="button" 
                  className="btn btn-secondary"
                  onClick={handleCloseModal}
                >
                  Close
                </button>
                {isEditMode ? (
                  <>
                    <button 
                      type="button" 
                      className="btn btn-outline-secondary"
                      onClick={handleCancelEdit}
                      disabled={saving}
                    >
                      Cancel
                    </button>
                    <button 
                      type="button" 
                      className="btn btn-primary"
                      onClick={handleSaveNotes}
                      disabled={saving}
                    >
                      {saving ? (
                        <>
                          <span className="spinner-border spinner-border-sm me-2" role="status">
                            <span className="visually-hidden">Saving...</span>
                          </span>
                          Saving...
                        </>
                      ) : (
                        <>
                          <i className="bi bi-check-lg me-2"></i>
                          Save Changes
                        </>
                      )}
                    </button>
                  </>
                ) : (
                  <button 
                    type="button" 
                    className="btn btn-primary"
                    onClick={handleEditMode}
                  >
                    <i className="bi bi-pencil me-2"></i>
                    Edit Notes
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Modal de confirmación para mejorar nota con IA */}
      {showAiModal && (
        <div className="modal show d-block" tabIndex={-1} style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog modal-dialog-centered">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">
                  <i className="bi bi-robot me-2"></i>
                  AI Medical Note Improvement
                </h5>
                <button 
                  type="button" 
                  className="btn-close" 
                  onClick={handleCancelAiImprovement}
                  aria-label="Close"
                ></button>
              </div>
              <div className="modal-body">
                <p className="mb-3">Do you want me to improve this medical note?</p>
                <div className="bg-light p-3 rounded">
                  <small className="text-muted d-block mb-2">Current note:</small>
                  <p className="mb-0" style={{ maxHeight: '150px', overflowY: 'auto' }}>
                    {editNotes}
                  </p>
                </div>
              </div>
              <div className="modal-footer">
                <button 
                  type="button" 
                  className="btn btn-secondary" 
                  onClick={handleCancelAiImprovement}
                >
                  Cancel
                </button>
                <button 
                  type="button" 
                  className="btn btn-primary" 
                  onClick={handleConfirmAiImprovement}
                  style={{ backgroundColor: '#405de6', borderColor: '#405de6' }}
                >
                  <i className="bi bi-magic me-2"></i>
                  Yes, Improve Note
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Modal para confirmar cita médica */}
      {isConfirmModalOpen && appointmentToConfirm && (
        <div className="modal show d-block" tabIndex={-1} style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog modal-dialog-centered">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">
                  <i className="bi bi-check-circle me-2"></i>
                  Confirm Medical Appointment
                </h5>
                <button 
                  type="button" 
                  className="btn-close"
                  onClick={handleCloseConfirmModal}
                ></button>
              </div>
              <div className="modal-body">
                {error && (
                  <div className="alert alert-danger d-flex align-items-center mb-3" role="alert">
                    <i className="bi bi-exclamation-triangle me-2"></i>
                    {error}
                  </div>
                )}

                <div className="text-center mb-4">
                  <i className="bi bi-calendar-check" style={{ fontSize: '3rem', color: '#28a745' }}></i>
                </div>

                <p className="text-center mb-4">
                  Are you sure you want to confirm this medical appointment?
                </p>

                <div className="bg-light p-3 rounded mb-3">
                  <div className="row">
                    <div className="col-sm-4">
                      <strong>Patient:</strong>
                    </div>
                    <div className="col-sm-8">
                      {appointmentToConfirm.patientName || 'Unknown Patient'}
                    </div>
                  </div>
                  <div className="row">
                    <div className="col-sm-4">
                      <strong>Date:</strong>
                    </div>
                    <div className="col-sm-8">
                      {appointmentToConfirm.appointmentDate}
                    </div>
                  </div>
                  <div className="row">
                    <div className="col-sm-4">
                      <strong>Time:</strong>
                    </div>
                    <div className="col-sm-8">
                      {appointmentToConfirm.appointmentTime}
                    </div>
                  </div>
                  <div className="row">
                    <div className="col-sm-4">
                      <strong>Current Status:</strong>
                    </div>
                    <div className="col-sm-8">
                      <span className={`badge ${
                        appointmentToConfirm.status.toLowerCase() === 'confirmed' ? 'bg-success' :
                        appointmentToConfirm.status.toLowerCase() === 'pending' ? 'bg-warning' :
                        appointmentToConfirm.status.toLowerCase() === 'completed' ? 'bg-info' :
                        'bg-danger'
                      }`}>
                        {appointmentToConfirm.status}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="alert alert-info">
                  <i className="bi bi-info-circle me-2"></i>
                  After confirmation, the appointment status will be changed to <strong>"Confirmed"</strong>.
                </div>
              </div>
              <div className="modal-footer">
                <button 
                  type="button" 
                  className="btn btn-secondary"
                  onClick={handleCloseConfirmModal}
                  disabled={confirming}
                >
                  Cancel
                </button>
                <button 
                  type="button" 
                  className="btn btn-success"
                  onClick={handleConfirmAppointment}
                  disabled={confirming}
                >
                  {confirming ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                      Confirming...
                    </>
                  ) : (
                    <>
                      <i className="bi bi-check-circle me-2"></i>
                      Confirm Appointment
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Modal para editar cita médica */}
      {isEditModalOpen && appointmentToEdit && (
        <div className="modal show d-block" tabIndex={-1} style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog modal-lg">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">
                  <i className="bi bi-calendar-event me-2"></i>
                  Edit Medical Appointment
                </h5>
                <button 
                  type="button" 
                  className="btn-close"
                  onClick={handleCloseEditModal}
                ></button>
              </div>
              <div className="modal-body">
                {error && (
                  <div className="alert alert-danger d-flex align-items-center mb-3" role="alert">
                    <i className="bi bi-exclamation-triangle me-2"></i>
                    {error}
                  </div>
                )}

                <div className="row">
                  <div className="col-md-6 mb-3">
                    <label className="form-label">
                      <i className="bi bi-calendar me-1"></i>
                      Appointment Date <span className="text-danger">*</span>
                    </label>
                    <input 
                      type="date" 
                      className="form-control"
                      value={editAppointmentData.appointmentDate}
                      onChange={(e) => setEditAppointmentData(prev => ({ ...prev, appointmentDate: e.target.value }))}
                      min={new Date().toISOString().split('T')[0]}
                      required
                    />
                  </div>
                  <div className="col-md-6 mb-3">
                    <label className="form-label">
                      <i className="bi bi-clock me-1"></i>
                      Appointment Time <span className="text-danger">*</span>
                    </label>
                    <input 
                      type="time" 
                      className="form-control"
                      value={editAppointmentData.appointmentTime}
                      onChange={(e) => setEditAppointmentData(prev => ({ ...prev, appointmentTime: e.target.value }))}
                      required
                    />
                  </div>
                </div>

                <div className="mb-3">
                  <label className="form-label">
                    <i className="bi bi-person me-1"></i>
                    Patient (Read Only)
                  </label>
                  <input 
                    type="text" 
                    className="form-control" 
                    value={appointmentToEdit.patientName || 'Unknown Patient'}
                    readOnly
                    style={{ backgroundColor: '#f8f9fa', cursor: 'not-allowed' }}
                  />
                  <small className="text-muted">Patient information cannot be modified</small>
                </div>

                <div className="row">
                  <div className="col-md-6 mb-3">
                    <label className="form-label">
                      <i className="bi bi-info-circle me-1"></i>
                      Status (Will be set to Pending)
                    </label>
                    <input 
                      type="text" 
                      className="form-control" 
                      value="Pending"
                      readOnly
                      style={{ backgroundColor: '#fff3cd', cursor: 'not-allowed' }}
                    />
                    <small className="text-muted">Status will automatically be set to Pending after editing</small>
                  </div>
                  <div className="col-md-6 mb-3">
                    <label className="form-label">
                      <i className="bi bi-hash me-1"></i>
                      Appointment ID
                    </label>
                    <input 
                      type="text" 
                      className="form-control" 
                      value={appointmentToEdit.appointmentId}
                      readOnly
                      style={{ backgroundColor: '#f8f9fa', cursor: 'not-allowed' }}
                    />
                  </div>
                </div>

                <div className="mb-3">
                  <label className="form-label">
                    <i className="bi bi-file-text me-1"></i>
                    Notes
                  </label>
                  <textarea 
                    className="form-control" 
                    rows={3} 
                    value={editAppointmentData.notes}
                    onChange={(e) => setEditAppointmentData(prev => ({ ...prev, notes: e.target.value }))}
                    placeholder="Add or modify notes for this appointment..."
                  />
                </div>

                <div className="alert alert-info">
                  <i className="bi bi-info-circle me-2"></i>
                  <strong>Note:</strong> After editing, the appointment status will be changed to "Pending" and may require confirmation again.
                </div>
              </div>
              <div className="modal-footer">
                <button 
                  type="button" 
                  className="btn btn-secondary"
                  onClick={handleCloseEditModal}
                  disabled={updatingAppointment}
                >
                  Cancel
                </button>
                <button 
                  type="button" 
                  className="btn btn-primary"
                  onClick={handleUpdateAppointment}
                  disabled={updatingAppointment || !editAppointmentData.appointmentDate || !editAppointmentData.appointmentTime}
                >
                  {updatingAppointment ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                      Updating...
                    </>
                  ) : (
                    <>
                      <i className="bi bi-check-lg me-2"></i>
                      Update Appointment
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Modal para crear nueva cita */}
      {isCreateModalOpen && (
        <div className="modal show d-block" tabIndex={-1} style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog modal-lg">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">
                  <i className="bi bi-calendar-plus me-2"></i>
                  Create New Appointment
                </h5>
                <button 
                  type="button" 
                  className="btn-close"
                  onClick={handleCloseCreateModal}
                ></button>
              </div>
              <div className="modal-body">
                {error && (
                  <div className="alert alert-danger d-flex align-items-center mb-3" role="alert">
                    <i className="bi bi-exclamation-triangle me-2"></i>
                    {error}
                  </div>
                )}

                <div className="row">
                  <div className="col-md-6 mb-3">
                    <label className="form-label"><strong>Selected Date:</strong></label>
                    <input 
                      type="date" 
                      className="form-control"
                      value={selectedDateForNewAppointment}
                      onChange={(e) => setSelectedDateForNewAppointment(e.target.value)}
                      min={new Date().toISOString().split('T')[0]}
                    />
                  </div>
                  <div className="col-md-6 mb-3">
                    <label className="form-label"><strong>Appointment Time:</strong></label>
                    <input 
                      type="time" 
                      className="form-control"
                      value={newAppointment.appointmentTime}
                      onChange={(e) => setNewAppointment(prev => ({ ...prev, appointmentTime: e.target.value }))}
                      required
                    />
                  </div>
                </div>

                <div className="mb-3">
                  <label className="form-label"><strong>Patient:</strong></label>
                  {loadingPatients ? (
                    <div className="d-flex align-items-center">
                      <div className="spinner-border spinner-border-sm me-2" role="status">
                        <span className="visually-hidden">Loading...</span>
                      </div>
                      Loading patients...
                    </div>
                  ) : (
                    <select 
                      className="form-select"
                      value={newAppointment.patientId}
                      onChange={(e) => handlePatientSelect(e.target.value)}
                      required
                    >
                      <option value="">Select a patient</option>
                      {patients.map((patient) => (
                        <option key={patient.patientId} value={patient.patientId}>
                          {patient.name} - ID: {patient.patientId}
                        </option>
                      ))}
                    </select>
                  )}
                </div>

                <div className="row">
                  <div className="col-md-6 mb-3">
                    <label className="form-label"><strong>Status:</strong></label>
                    <select 
                      className="form-select"
                      value={newAppointment.status}
                      onChange={(e) => setNewAppointment(prev => ({ ...prev, status: e.target.value }))}
                    >
                      <option value="pending">Pending</option>
                      <option value="confirmed">Confirmed</option>
                    </select>
                  </div>
                  <div className="col-md-6 mb-3">
                    <label className="form-label"><strong>Doctor ID:</strong></label>
                    <input 
                      type="text" 
                      className="form-control"
                      value={doctorId || ''}
                      readOnly
                      style={{ backgroundColor: '#f8f9fa' }}
                    />
                  </div>
                </div>

                <div className="mb-3">
                  <label className="form-label"><strong>Notes (Optional):</strong></label>
                  <textarea 
                    className="form-control" 
                    rows={3} 
                    value={newAppointment.notes}
                    onChange={(e) => setNewAppointment(prev => ({ ...prev, notes: e.target.value }))}
                    placeholder="Add any additional notes for this appointment..."
                  />
                </div>
              </div>
              <div className="modal-footer">
                <button 
                  type="button" 
                  className="btn btn-secondary"
                  onClick={handleCloseCreateModal}
                  disabled={creatingAppointment}
                >
                  Cancel
                </button>
                <button 
                  type="button" 
                  className="btn btn-primary"
                  onClick={handleCreateAppointment}
                  disabled={creatingAppointment || !newAppointment.patientId || !newAppointment.appointmentTime}
                >
                  {creatingAppointment ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2" role="status">
                        <span className="visually-hidden">Creating...</span>
                      </span>
                      Creating...
                    </>
                  ) : (
                    <>
                      <i className="bi bi-check-lg me-2"></i>
                      Create Appointment
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Appointments;