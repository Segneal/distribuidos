import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { apiRequest } from '../services/apiClient.js';

const AuthContext = createContext(undefined);

function safeParseUser(raw) {
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch (error) {
    console.warn('No se pudo parsear el usuario almacenado', error);
    return null;
  }
}

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem('authToken'));
  const [user, setUser] = useState(() => safeParseUser(localStorage.getItem('authUser')));
  const [loading, setLoading] = useState(false);
  const [initializing, setInitializing] = useState(true);
  const [error, setError] = useState(null);

  const resetAuth = useCallback(() => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('authToken');
    localStorage.removeItem('authUser');
  }, []);

  useEffect(() => {
    if (!token) {
      setInitializing(false);
      setUser(null);
      return;
    }

    if (user) {
      setInitializing(false);
      return;
    }

    const controller = new AbortController();

    const fetchProfile = async () => {
      try {
        const data = await apiRequest('/api/auth/perfil', {
          token,
          signal: controller.signal,
        });
        if (data?.usuario) {
          setUser(data.usuario);
          localStorage.setItem('authUser', JSON.stringify(data.usuario));
        } else {
          resetAuth();
        }
      } catch (err) {
        console.error('Error al recuperar el perfil', err);
        resetAuth();
      } finally {
        setInitializing(false);
      }
    };

    fetchProfile();

    return () => controller.abort();
  }, [token, user, resetAuth]);

  const login = useCallback(
    async (identificador, clave) => {
      setLoading(true);
      setError(null);
      try {
        const data = await apiRequest('/api/auth/login', {
          method: 'POST',
          body: { identificador, clave },
        });
        setToken(data.token);
        setUser(data.usuario);
        localStorage.setItem('authToken', data.token);
        localStorage.setItem('authUser', JSON.stringify(data.usuario));
        setInitializing(false);
        return data;
      } catch (err) {
        const message = err.details?.mensaje || err.message || 'No se pudo iniciar sesión';
        setError(message);
        resetAuth();
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [resetAuth],
  );

  const logout = useCallback(() => {
    resetAuth();
    setError(null);
    setInitializing(false);
  }, [resetAuth]);

  const value = useMemo(
    () => ({
      user,
      token,
      login,
      logout,
      loading,
      error,
      setError,
      isAuthenticated: Boolean(token),
      initializing,
    }),
    [user, token, login, logout, loading, error, initializing],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth debe utilizarse dentro de un AuthProvider');
  }
  return context;
}
