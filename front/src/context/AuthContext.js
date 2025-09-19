import React, { createContext, useContext, useState, useEffect } from 'react';
import { login as apiLogin } from '../api/auth';

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try {
      const raw = localStorage.getItem('tp_user');
      return raw ? JSON.parse(raw) : null;
    } catch { return null; }
  });

  useEffect(() => {
    if (user) localStorage.setItem('tp_user', JSON.stringify(user));
    else localStorage.removeItem('tp_user');
  }, [user]);

  const login = async (usuario, clave) => {
    const data = await apiLogin(usuario, clave);
    // api should return { token, user: {nombre, apellido, email, rol, id} }
    setUser(data.user);
    localStorage.setItem('tp_token', data.token);
    return data.user;
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('tp_token');
  };

  return (
    <AuthContext.Provider value={{ user, setUser, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
