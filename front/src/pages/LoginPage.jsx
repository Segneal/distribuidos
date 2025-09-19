import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function LoginPage(){
  const [form, setForm] = useState({ usuario: '', clave: '' });
  const [error, setError] = useState(null);
  const { login } = useAuth();
  const nav = useNavigate();

  const submit = async (e) => {
    e.preventDefault();
    setError(null);
    try {
      const user = await login(form.usuario, form.clave);
      nav('/');
    } catch (err) {
      setError(err.response?.data?.message || err.message || 'Error en login');
    }
  };

  return (
    <div className="container">
      <h2>Iniciar sesión</h2>
      <form onSubmit={submit}>
        <div className="form-row">
          <input className="input" placeholder="Usuario o Email" value={form.usuario}
                 onChange={e=>setForm({...form, usuario: e.target.value})} />
        </div>
        <div className="form-row">
          <input className="input" placeholder="Contraseña" type="password" value={form.clave}
                 onChange={e=>setForm({...form, clave: e.target.value})} />
        </div>
        {error && <div style={{color:'red'}}>{error}</div>}
        <button type="submit">Ingresar</button>
      </form>
    </div>
  );
}
