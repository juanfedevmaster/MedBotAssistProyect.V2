import React, { useState } from 'react';
import { API_ENDPOINTS } from '../../config/endpoints';
import { useNavigate } from 'react-router-dom';

interface RegisterRequest {
  fullName: string;
  email: string;
  userName: string;
  password: string;
  confirmPassword: string;
  roleId?: number;
}

const Register: React.FC = () => {
  const navigate = useNavigate();
  const [form, setForm] = useState<RegisterRequest>({
    fullName: '',
    email: '',
    userName: '',
    password: '',
    confirmPassword: '',
    roleId: 2,
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
    setError('');
    setSuccess('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (form.password !== form.confirmPassword) {
      setError('Las contraseñas no coinciden.');
      return;
    }

    try {
      const response = await fetch(API_ENDPOINTS.REGISTER, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          fullName: form.fullName,
          email: form.email,
          userName: form.userName,
          password: form.password,
          roleId: form.roleId,
        }),
      });

      if (!response.ok) {
        throw new Error('No se pudo registrar el usuario.');
      }

      setSuccess('Usuario registrado exitosamente.');
      setTimeout(() => {
          navigate('/login');
      }, 2000);
      setForm({
        fullName: '',
        email: '',
        userName: '',
        password: '',
        confirmPassword: '',
        roleId: 2,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error inesperado.');
    }
  };

  return (
    <div className="d-flex justify-content-center align-items-center vh-100" style={{ background: 'linear-gradient(180deg, #ffffff, #405de6)' }}>
      <div className="bg-white p-4 rounded shadow" style={{ width: '100%', maxWidth: '400px' }}>
        <h2 className="text-center mb-4">Registro de Usuario</h2>
        <form onSubmit={handleSubmit}>
          <div className="mb-3">
            <label htmlFor="fullName" className="form-label">Nombre completo</label>
            <input
              type="text"
              className="form-control"
              id="fullName"
              name="fullName"
              value={form.fullName}
              onChange={handleChange}
              required
            />
          </div>
          <div className="mb-3">
            <label htmlFor="email" className="form-label">Correo electrónico</label>
            <input
              type="email"
              className="form-control"
              id="email"
              name="email"
              value={form.email}
              onChange={handleChange}
              required
            />
          </div>
          <div className="mb-3">
            <label htmlFor="userName" className="form-label">Usuario</label>
            <input
              type="text"
              className="form-control"
              id="userName"
              name="userName"
              value={form.userName}
              onChange={handleChange}
              required
            />
          </div>
          <div className="mb-3">
            <label htmlFor="password" className="form-label">Contraseña</label>
            <input
              type="password"
              className="form-control"
              id="password"
              name="password"
              value={form.password}
              onChange={handleChange}
              required
            />
          </div>
          <div className="mb-3">
            <label htmlFor="confirmPassword" className="form-label">Confirmar contraseña</label>
            <input
              type="password"
              className="form-control"
              id="confirmPassword"
              name="confirmPassword"
              value={form.confirmPassword}
              onChange={handleChange}
              required
            />
          </div>
          <button type="submit" className="btn btn-primary w-100">Registrarse</button>
          {error && <div className="alert alert-danger mt-3">{error}</div>}
          {success && <div className="alert alert-success mt-3">{success}</div>}
        </form>
      </div>
    </div>
  );
};

export default Register;