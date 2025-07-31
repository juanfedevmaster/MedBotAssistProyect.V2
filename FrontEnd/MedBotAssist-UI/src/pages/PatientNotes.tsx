import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { PatientInfoWithClinicalDto, ClinicalSummaryCreateDto, MedicalNoteCreateDto } from '../types';
import ApiService from '../services/apiService';
import TokenManager from '../utils/tokenManager';
import { API_ENDPOINTS } from '../config/endpoints';

interface PatientNotesProps {
  doctorId: string | number | null;
  username?: string;
}

const PatientNotes: React.FC<PatientNotesProps> = ({ doctorId, username }) => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  
  // Estados
  const [patient, setPatient] = useState<PatientInfoWithClinicalDto | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [success, setSuccess] = useState<string>('');
  const [notes, setNotes] = useState<string>('');
  const [saving, setSaving] = useState(false);
  const [medicalHistory, setMedicalHistory] = useState<string>('');
  const [aiLoading, setAiLoading] = useState(false);
  const [showAiModal, setShowAiModal] = useState(false);
  const [appointmentId, setAppointmentId] = useState<number>(() => {
    // Intentar obtener appointmentId de la URL o localStorage, sino usar 1 por defecto
    const urlParams = new URLSearchParams(window.location.search);
    const appointmentFromUrl = urlParams.get('appointmentId');
    if (appointmentFromUrl) {
      return parseInt(appointmentFromUrl);
    }
    const storedAppointmentId = localStorage.getItem(`appointmentId_${id}`);
    return storedAppointmentId ? parseInt(storedAppointmentId) : 1;
  });
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const _setAppointmentId = setAppointmentId; // Mantener para uso futuro
  const [showSaveModal, setShowSaveModal] = useState(false);
  
  // Estados para el clinical summary
  const [diagnosis, setDiagnosis] = useState<string>('');
  const [treatment, setTreatment] = useState<string>('');
  const [recommendations, setRecommendations] = useState<string>('');
  const [nextSteps, setNextSteps] = useState<string>('');

  // Guardar appointmentId en localStorage cuando cambie
  useEffect(() => {
    if (id && appointmentId) {
      localStorage.setItem(`appointmentId_${id}`, appointmentId.toString());
    }
  }, [id, appointmentId]);

  // Cargar datos del paciente
  const loadPatientData = useCallback(async () => {
    const isAuthenticated = TokenManager.isAuthenticated();
    
    if (!id || !isAuthenticated) {
      setError('Patient ID not found or user not authenticated');
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      const response = await ApiService.getPatientById(id);
      const patientData = await response.json();
      setPatient(patientData);
      
      // Format clinical history
      let historyText = '';
      if (patientData.clinicalSummaries && patientData.clinicalSummaries.length > 0) {
        patientData.clinicalSummaries.forEach((summary: any) => {
          if (summary.diagnosis !== null && summary.diagnosis !== '') {
            historyText += `DIAGNOSIS: ${summary.diagnosis}\n`;
          }
          if (summary.treatment !== null && summary.treatment !== '') {
            historyText += `TREATMENT: ${summary.treatment}\n`;
          }
          if (summary.recommendations !== null && summary.recommendations !== '') {
            historyText += `RECOMMENDATIONS: ${summary.recommendations}\n`;
          }
          if (summary.nextSteps !== null && summary.nextSteps !== '') {
            historyText += `NEXT STEPS: ${summary.nextSteps}\n`;
          }

          if (summary.medicalNote) {
            const noteDate = new Date(summary.medicalNote.creationDate).toLocaleDateString();
            historyText += `\n- ${noteDate}\n${summary.medicalNote.freeText}\n\n`;
          }

          if (historyText !== '') {
            historyText += '---\n\n';
          }
        });
      }
      setMedicalHistory(historyText);
      
      // Populate clinical summary fields with the last entry
      if (patientData.clinicalSummaries && patientData.clinicalSummaries.length > 0) {
        const lastSummary = patientData.clinicalSummaries[patientData.clinicalSummaries.length - 1];
        setDiagnosis(lastSummary.diagnosis || '');
        setTreatment(lastSummary.treatment || '');
        setRecommendations(lastSummary.recommendations || '');
        setNextSteps(lastSummary.nextSteps || '');
      }
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load patient data');
    } finally {
      setLoading(false);
    }
  }, [id]);

  // Cargar datos del paciente
  useEffect(() => {
    loadPatientData();
  }, [loadPatientData]);

  const handleLogout = () => {
    TokenManager.clearSessionData(); // Usar clearSessionData para mantener conversation_id
    navigate('/');
  };

  const handleProfile = () => {
    navigate('/profile');
  };

  const handleBack = () => {
    if (patient) {
      navigate(`/patients/view/${patient.patientId}`, { 
        state: { patient } 
      });
    } else {
      navigate('/patients');
    }
  };

  const handleSaveNotes = async () => {
    if (!notes.trim()) {
      setError('Please enter some notes before saving');
      return;
    }
    
    if (!diagnosis.trim() || !treatment.trim() || !recommendations.trim() || !nextSteps.trim()) {
      setError('Please fill in all clinical summary fields (diagnosis, treatment, recommendations, next steps)');
      return;
    }

    // Show confirmation modal
    setShowSaveModal(true);
  };

  const handleConfirmSaveNotes = async () => {
    setShowSaveModal(false);
    
    try {
      setSaving(true);
      setError('');
      
      // Prepare medical note
      const medicalNote: MedicalNoteCreateDto = {
        noteId: 0,
        creationDate: new Date().toISOString(),
        freeText: notes,
        appointmentId: appointmentId
      };
      
      // Preparar el clinical summary completo
      const clinicalSummaryData: ClinicalSummaryCreateDto = {
        summaryId: 0,
        diagnosis: diagnosis,
        treatment: treatment,
        recommendations: recommendations,
        nextSteps: nextSteps,
        generatedDate: new Date().toISOString(),
        medicalNote: medicalNote
      };
      
      // Llamar al API para crear el clinical summary
      const response = await ApiService.createClinicalSummary(clinicalSummaryData);
      
      if (response.ok) {
        setSuccess('Clinical summary and medical note saved successfully!');
        // Clear all fields after saving
        setNotes('');
        setDiagnosis('');
        setTreatment('');
        setRecommendations('');
        setNextSteps('');
        
        // Show success message for 2 seconds and then reload patient data
        setTimeout(() => {
          setSuccess('');
          // Recargar los datos del paciente para mostrar la nueva nota en el historial
          loadPatientData();
        }, 2000);
      } else {
        throw new Error('Failed to save clinical summary');
      }
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save clinical summary');
    } finally {
      setSaving(false);
    }
  };

  const handleCancelSaveNotes = () => {
    setShowSaveModal(false);
  };

  const handleNotesChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setNotes(e.target.value);
  };

  const handleShowAiModal = () => {
    if (!notes.trim()) {
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
    if (!notes.trim()) {
      setError('Please enter some text before using AI assistance');
      return;
    }

    try {
      setAiLoading(true);
      setError('');
      
      // Preparar el mensaje para el agente de IA
      const message = `Ayudame a redactar mejor esta nota: ${notes}, solo responde con la nota mejorada, sin saludos, ni mensajes adicionales, solo el mensaje mejorado`;
      // Llamar al agente de IA usando el ApiService
      const response = await ApiService.aiApiFetch(API_ENDPOINTS.AI_CHAT, {
        method: 'POST',
        body: JSON.stringify({ message })
      });

      if (response.ok) {
        const data = await response.json();
        // Actualizar el campo de notas con la respuesta del agente
        if (data.response) {
          setNotes(data.response);
        } else if (data.message) {
          setNotes(data.message);
        } else {
          setNotes(data);
        }
      } else {
        throw new Error('Failed to get AI response');
      }

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error getting AI assistance');
    } finally {
      setAiLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', background: 'linear-gradient(180deg, #ffffff, #405de6)' }}>
        <div className="d-flex justify-content-center align-items-center" style={{ minHeight: '100vh' }}>
          <div className="text-center text-white">
            <div className="spinner-border mb-3" role="status">
              <span className="visually-hidden">Loading...</span>
            </div>
            <p>Loading patient data...</p>
          </div>
        </div>
      </div>
    );
  }

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
      <div className="container-fluid mt-4 px-4">
        {/* Check if patient has clinical summaries (appointments) */}
        {!patient?.clinicalSummaries || patient.clinicalSummaries.length === 0 ? (
          <div className="row justify-content-center">
            <div className="col-md-8">
              <div className="bg-white rounded shadow p-5 text-center" style={{ color: '#333' }}>
                <i className="bi bi-exclamation-triangle-fill text-warning mb-3" style={{ fontSize: '3rem' }}></i>
                <h3 className="mb-3" style={{ color: '#405de6' }}>No Appointments Assigned</h3>
                <p className="lead text-muted mb-4">
                  Cannot add medical notes until the patient has an assigned appointment.
                </p>
                <p className="text-muted mb-4">
                  Please assign an appointment to this patient first, then return to add medical notes.
                </p>
                <button 
                  className="btn btn-primary"
                  onClick={() => navigate('/appointments')}
                  style={{ backgroundColor: '#405de6', borderColor: '#405de6' }}
                >
                  <i className="bi bi-calendar-plus me-2"></i>
                  Go to Appointments
                </button>
              </div>
            </div>
          </div>
        ) : (
        <div className="row">
          {/* Left panel - Patient information */}
          <div className="col-lg-3 col-md-4 mb-4">
            <div className="bg-white rounded shadow p-4 h-100" style={{ color: '#333' }}>
              <h4 className="mb-3" style={{ color: '#405de6' }}>
                <i className="bi bi-person-circle me-2"></i>
                Patient Information
              </h4>
              
              {patient && (
                <div className="patient-info">
                  <div className="mb-3">
                    <label className="form-label fw-bold text-muted small">Patient ID</label>
                    <p className="mb-1">{patient.patientId}</p>
                  </div>
                  
                  <div className="mb-3">
                    <label className="form-label fw-bold text-muted small">Full Name</label>
                    <p className="mb-1">{patient.name}</p>
                  </div>
                  
                  <div className="mb-3">
                    <label className="form-label fw-bold text-muted small">ID Number</label>
                    <p className="mb-1">{patient.identificationNumber}</p>
                  </div>
                  
                  <div className="mb-3">
                    <label className="form-label fw-bold text-muted small">Date of Birth</label>
                    <p className="mb-1">{new Date(patient.dateOfBirth).toLocaleDateString()}</p>
                  </div>
                  
                  <div className="mb-3">
                    <label className="form-label fw-bold text-muted small">Phone</label>
                    <p className="mb-1">{patient.phoneNumber}</p>
                  </div>
                  
                  <div className="mb-3">
                    <label className="form-label fw-bold text-muted small">Email</label>
                    <p className="mb-1">{patient.email}</p>
                  </div>
                </div>
              )}
              
              <div className="mt-4">
                <button 
                  className="btn btn-outline-secondary w-100"
                  onClick={handleBack}
                >
                  <i className="bi bi-arrow-left me-2"></i>
                  Back to Patient
                </button>
              </div>
            </div>
          </div>

          {/* Right panel - Clinical history and notes */}
          <div className="col-lg-9 col-md-8">
            <div className="bg-white rounded shadow p-4" style={{ color: '#333' }}>
              {/* Header */}
              <div className="d-flex justify-content-between align-items-center mb-4">
                <h3 style={{ color: '#405de6' }}>
                  <i className="bi bi-file-medical me-2"></i>
                  Patient Notes & Medical History
                </h3>
                {patient && (
                  <span className="badge bg-light text-dark fs-6">
                    Patient: {patient.name}
                  </span>
                )}
              </div>

              {/* Mensajes de estado */}
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

              {/* Clinical history */}
              <div className="mb-4">
                <label className="form-label fw-bold">
                  <i className="bi bi-file-earmark-medical me-2"></i>
                  Medical History
                </label>
                <textarea
                  className="form-control"
                  rows={12}
                  placeholder="Medical history will be displayed here..."
                  value={medicalHistory}
                  readOnly
                  style={{ 
                    backgroundColor: '#f8f9fa',
                    minHeight: '300px',
                    resize: 'none'
                  }}
                />
                <small className="text-muted">
                  <i className="bi bi-info-circle me-1"></i>
                  Medical history is read-only and managed by the system
                </small>
              </div>

              {/* Notas */}
              <div className="mb-4">
                <label className="form-label fw-bold">
                  <i className="bi bi-pencil-square me-2"></i>
                  Add Notes
                </label>
                <div className="position-relative">
                  <textarea
                    className="form-control"
                    rows={6}
                    placeholder={aiLoading ? "AI is improving your notes..." : "Enter your notes about this patient..."}
                    value={notes}
                    onChange={handleNotesChange}
                    disabled={aiLoading}
                    style={{ 
                      minHeight: '150px',
                      resize: 'vertical',
                      paddingBottom: '45px', // Space for the button
                      backgroundColor: aiLoading ? '#f8f9fa' : 'white',
                      cursor: aiLoading ? 'not-allowed' : 'text'
                    }}
                  />
                  {/* AI floating button */}
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
                      backgroundColor: aiLoading ? '#6c757d' : '#405de6',
                      border: 'none',
                      boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                    }}
                    onClick={handleShowAiModal}
                    disabled={aiLoading || !notes.trim()}
                    title={aiLoading ? "AI is working..." : "Improve medical note"}
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
                <small className="text-muted">
                  <i className="bi bi-info-circle me-1"></i>
                  Add your observations, treatment notes, or any relevant information
                </small>
              </div>

              {/* Campos del Clinical Summary */}
              <div className="row mb-4">
                <div className="col-12">
                  <h5 className="mb-3" style={{ color: '#405de6' }}>
                    <i className="bi bi-clipboard-data me-2"></i>
                    Clinical Summary
                    {patient?.clinicalSummaries && patient.clinicalSummaries.length > 0 && (
                      <small className="ms-2 text-muted fs-6">
                        <i className="bi bi-info-circle me-1"></i>
                        Pre-filled with last consultation data
                      </small>
                    )}
                  </h5>
                </div>
                
                <div className="col-md-6 mb-3">
                  <label htmlFor="diagnosis" className="form-label">
                    <i className="bi bi-search me-2"></i>
                    Diagnosis *
                  </label>
                  <textarea
                    className="form-control"
                    id="diagnosis"
                    rows={3}
                    value={diagnosis}
                    onChange={(e) => setDiagnosis(e.target.value)}
                    placeholder="Enter the diagnosis..."
                  />
                </div>
                
                <div className="col-md-6 mb-3">
                  <label htmlFor="treatment" className="form-label">
                    <i className="bi bi-prescription2 me-2"></i>
                    Treatment *
                  </label>
                  <textarea
                    className="form-control"
                    id="treatment"
                    rows={3}
                    value={treatment}
                    onChange={(e) => setTreatment(e.target.value)}
                    placeholder="Enter the treatment plan..."
                  />
                </div>
                
                <div className="col-md-6 mb-3">
                  <label htmlFor="recommendations" className="form-label">
                    <i className="bi bi-lightbulb me-2"></i>
                    Recommendations *
                  </label>
                  <textarea
                    className="form-control"
                    id="recommendations"
                    rows={3}
                    value={recommendations}
                    onChange={(e) => setRecommendations(e.target.value)}
                    placeholder="Enter recommendations..."
                  />
                </div>
                
                <div className="col-md-6 mb-3">
                  <label htmlFor="nextSteps" className="form-label">
                    <i className="bi bi-arrow-right-circle me-2"></i>
                    Next Steps *
                  </label>
                  <textarea
                    className="form-control"
                    id="nextSteps"
                    rows={3}
                    value={nextSteps}
                    onChange={(e) => setNextSteps(e.target.value)}
                    placeholder="Enter next steps..."
                  />
                </div>
              </div>

              {/* Campo para appointmentId */}
              <div className="mb-3">
                <label htmlFor="appointmentId" className="form-label">
                  <i className="bi bi-calendar-check me-2"></i>
                  Appointment ID
                </label>
                <input
                  type="number"
                  className="form-control"
                  id="appointmentId"
                  value={appointmentId}
                  readOnly
                  min="1"
                  style={{ 
                    maxWidth: '200px',
                    backgroundColor: '#f8f9fa',
                    cursor: 'not-allowed'
                  }}
                  placeholder="Enter appointment ID"
                />
                <small className="text-muted">
                  <i className="bi bi-info-circle me-1"></i>
                  ID of the appointment for this medical note (read-only)
                </small>
              </div>

              {/* Button to save notes */}
              <div className="d-flex justify-content-end">
                <button 
                  className="btn"
                  style={{ backgroundColor: '#405de6', color: '#fff' }}
                  onClick={handleSaveNotes}
                  disabled={saving || !notes.trim() || !diagnosis.trim() || !treatment.trim() || !recommendations.trim() || !nextSteps.trim()}
                >
                  {saving ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                      Saving...
                    </>
                  ) : (
                    <>
                      <i className="bi bi-save me-2"></i>
                      Save Clinical Summary
                    </>
                  )}
                </button>
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
        )}
      </div>

      {/* Confirmation modal to improve note with AI */}
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
                    {notes}
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

      {/* Confirmation modal to save medical note */}
      {showSaveModal && (
        <div className="modal show d-block" tabIndex={-1} style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog modal-dialog-centered">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">
                  <i className="bi bi-save me-2"></i>
                  Save Clinical Summary
                </h5>
                <button 
                  type="button" 
                  className="btn-close" 
                  onClick={handleCancelSaveNotes}
                  aria-label="Close"
                ></button>
              </div>
              <div className="modal-body">
                <p className="mb-3">
                  <i className="bi bi-question-circle text-warning me-2"></i>
                  Are you sure you want to save this clinical summary and medical note?
                </p>
                
                {/* Clinical Summary Information */}
                <div className="bg-light p-3 rounded mb-3">
                  <h6 className="mb-3">
                    <i className="bi bi-clipboard-data me-2"></i>
                    Clinical Summary
                  </h6>
                  <div className="row">
                    <div className="col-6">
                      <small className="text-muted d-block">Diagnosis:</small>
                      <p className="mb-2 small">{diagnosis}</p>
                    </div>
                    <div className="col-6">
                      <small className="text-muted d-block">Treatment:</small>
                      <p className="mb-2 small">{treatment}</p>
                    </div>
                    <div className="col-6">
                      <small className="text-muted d-block">Recommendations:</small>
                      <p className="mb-2 small">{recommendations}</p>
                    </div>
                    <div className="col-6">
                      <small className="text-muted d-block">Next Steps:</small>
                      <p className="mb-2 small">{nextSteps}</p>
                    </div>
                  </div>
                </div>
                
                {/* Medical Note Information */}
                <div className="bg-light p-3 rounded">
                  <h6 className="mb-2">
                    <i className="bi bi-file-medical me-2"></i>
                    Medical Note
                  </h6>
                  <small className="text-muted d-block mb-2">Note content:</small>
                  <p className="mb-0 small" style={{ maxHeight: '100px', overflowY: 'auto' }}>
                    {notes}
                  </p>
                </div>
                
                <div className="mt-3">
                  <small className="text-muted">
                    <i className="bi bi-info-circle me-1"></i>
                    Patient ID: {patient?.patientId} | Appointment ID: {appointmentId}
                  </small>
                </div>
              </div>
              <div className="modal-footer">
                <button 
                  type="button" 
                  className="btn btn-secondary" 
                  onClick={handleCancelSaveNotes}
                >
                  <i className="bi bi-x-lg me-2"></i>
                  Cancel
                </button>
                <button 
                  type="button" 
                  className="btn btn-success" 
                  onClick={handleConfirmSaveNotes}
                  disabled={saving}
                >
                  {saving ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                      Saving...
                    </>
                  ) : (
                    <>
                      <i className="bi bi-check-lg me-2"></i>
                      Yes, Save Clinical Summary
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

export default PatientNotes;
