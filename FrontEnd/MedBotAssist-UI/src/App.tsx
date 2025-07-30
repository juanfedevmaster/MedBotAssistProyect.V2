import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './modules/login/Login';
import Home from './pages/Home';
import Profile from './pages/Profile';
import Patients from './pages/Patients';
import PatientForm from './pages/PatientForm';
import PatientNotes from './pages/PatientNotes';
import Appointments from './pages/Appointments';
import Register from './modules/register/Register';
import FloatingChat from './components/FloatingChat';
import TokenManager from './utils/tokenManager';

const App = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [doctorId, setDoctorId] = useState<string | number | null>(null);
  const [username, setUsername] = useState<string>('');

  // Check authentication when loading the application
  useEffect(() => {
    const token = TokenManager.getToken();
    const storedDoctorId = TokenManager.getDoctorId();
    const storedUsername = TokenManager.getUsername();
    
    if (token && storedDoctorId) {
      setIsAuthenticated(true);
      setDoctorId(storedDoctorId);
      if (storedUsername) {
        setUsername(storedUsername);
      }
    }
  }, []);

  const handleLogin = (success: boolean, doctorId?: string | number, username?: string) => {
    setIsAuthenticated(success);
    if (success && doctorId) {
      setDoctorId(doctorId);
    }
    if (success && username) {
      setUsername(username);
    }
  };

  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login onLogin={handleLogin} />} />
        <Route path="/register" element={<Register />} />
        <Route
          path="/home"
          element={isAuthenticated ? <Home doctorId={doctorId} username={username} /> : <Navigate to="/login" replace />}
        />
        <Route
          path="/profile"
          element={isAuthenticated ? <Profile doctorId={doctorId} username={username} /> : <Navigate to="/login" replace />}
        />
        <Route
          path="/patients"
          element={isAuthenticated ? <Patients doctorId={doctorId} username={username} /> : <Navigate to="/login" replace />}
        />
        <Route
          path="/patients/new"
          element={isAuthenticated ? <PatientForm doctorId={doctorId} username={username} /> : <Navigate to="/login" replace />}
        />
        <Route
          path="/patients/view/:id"
          element={isAuthenticated ? <PatientForm doctorId={doctorId} username={username} /> : <Navigate to="/login" replace />}
        />
        <Route
          path="/patients/edit/:id"
          element={isAuthenticated ? <PatientForm doctorId={doctorId} username={username} /> : <Navigate to="/login" replace />}
        />
        <Route
          path="/patients/notes/:id"
          element={isAuthenticated ? <PatientNotes doctorId={doctorId} username={username} /> : <Navigate to="/login" replace />}
        />
        <Route
          path="/appointments"
          element={isAuthenticated ? <Appointments doctorId={doctorId} username={username} /> : <Navigate to="/login" replace />}
        />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
      
      {/* Floating chat - Only appears when user is authenticated */}
      {isAuthenticated && <FloatingChat />}
    </Router>
  );
};

export default App;