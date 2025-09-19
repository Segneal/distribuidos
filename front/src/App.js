import React from 'react';
import { BrowserRouter, Routes, Route, Navigate, Link } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import LoginPage from './pages/LoginPage';
import UsuariosPage from './pages/UsuariosPage';
import InventarioPage from './pages/InventarioPage';
import EventosPage from './pages/EventosPage';

function PrivateRoute({ children, roles }) {
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" replace />;
  if (roles && !roles.includes(user.rol)) return <Navigate to="/" replace />;
  return children;
}

function Home() {
  const { user, logout } = useAuth();
  return (
    <div className="container">
      <div className="header">
        <div>
          <strong>Empuje Comunitario</strong>
          <div className="nav">
            <Link to="/usuarios">Usuarios</Link>
            <Link to="/inventario">Inventario</Link>
            <Link to="/eventos">Eventos</Link>
          </div>
        </div>
        <div>
          {user ? (
            <>
              <span>{user.nombre} ({user.rol})</span>
              <button onClick={logout} style={{marginLeft:12}}>Cerrar sesión</button>
            </>
          ) : <Link to="/login">Iniciar sesión</Link>}
        </div>
      </div>
      <p>Bienvenido al panel. Usá el menú para navegar.</p>
    </div>
  );
}

export default function App(){
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/usuarios" element={
            <PrivateRoute roles={['PRESIDENTE']}>
              <UsuariosPage />
            </PrivateRoute>
          }/>
          <Route path="/inventario" element={
            <PrivateRoute roles={['PRESIDENTE','VOCAL']}>
              <InventarioPage />
            </PrivateRoute>
          }/>
          <Route path="/eventos" element={
            <PrivateRoute roles={['PRESIDENTE','COORDINADOR','VOLUNTARIO']}>
              <EventosPage />
            </PrivateRoute>
          }/>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
