import { useEffect, useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext.jsx';

function Login() {
  const [identificador, setIdentificador] = useState('');
  const [clave, setClave] = useState('');
  const [formError, setFormError] = useState(null);
  const navigate = useNavigate();
  const location = useLocation();
  const { login, loading, error, setError, isAuthenticated } = useAuth();

  useEffect(() => {
    if (isAuthenticated) {
      const from = location.state?.from?.pathname ? location.state.from : { pathname: '/eventos' };
      navigate(from, { replace: true });
    }
  }, [isAuthenticated, location.state, navigate]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setFormError(null);

    if (!identificador.trim() || !clave.trim()) {
      setFormError('Completá usuario/email y contraseña.');
      return;
    }

    try {
      await login(identificador.trim(), clave.trim());
    } catch (err) {
      console.error('Error de login', err);
    }
  };

  const handleChange = (setter) => (event) => {
    setter(event.target.value);
    if (formError) setFormError(null);
    if (error) setError(null);
  };

  return (
    <div className="mx-auto max-w-md">
      <div className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
        <h1 className="text-2xl font-semibold text-slate-800">Iniciar sesión</h1>
        <p className="mt-2 text-sm text-slate-600">
          Utilizá tu nombre de usuario o email registrado en el sistema. Las credenciales se validan contra el
          servicio de usuarios mediante el API Gateway.
        </p>

        <form onSubmit={handleSubmit} className="mt-6 space-y-4">
          <div>
            <label htmlFor="identificador" className="mb-1 block text-sm font-medium text-slate-700">
              Usuario o email
            </label>
            <input
              id="identificador"
              type="text"
              value={identificador}
              onChange={handleChange(setIdentificador)}
              className="w-full rounded-md border border-slate-200 px-3 py-2 text-sm text-slate-700 shadow-sm focus:border-primary-400 focus:outline-none focus:ring-2 focus:ring-primary-200"
              placeholder="tu.usuario"
              autoComplete="username"
            />
          </div>

          <div>
            <label htmlFor="clave" className="mb-1 block text-sm font-medium text-slate-700">
              Contraseña
            </label>
            <input
              id="clave"
              type="password"
              value={clave}
              onChange={handleChange(setClave)}
              className="w-full rounded-md border border-slate-200 px-3 py-2 text-sm text-slate-700 shadow-sm focus:border-primary-400 focus:outline-none focus:ring-2 focus:ring-primary-200"
              placeholder="••••••••"
              autoComplete="current-password"
            />
          </div>

          {(formError || error) && (
            <div className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
              {formError || error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="flex w-full items-center justify-center rounded-md bg-primary-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-primary-700 disabled:cursor-not-allowed disabled:bg-primary-300"
          >
            {loading ? 'Validando…' : 'Ingresar'}
          </button>
        </form>
      </div>

      <p className="mt-4 text-center text-xs text-slate-500">
        ¿No recordás tu contraseña? Contactá al Presidente para reestablecerla según el flujo definido en el
        sistema.
      </p>

      <div className="mt-8 rounded-2xl border border-slate-200 bg-white p-6 text-sm text-slate-600 shadow-sm">
        <h2 className="text-sm font-semibold text-slate-800">Accesos rápidos</h2>
        <ul className="mt-2 list-inside list-disc space-y-1">
          <li>
            <Link className="text-primary-700 hover:underline" to="/eventos">
              Eventos solidarios (requiere sesión)
            </Link>
          </li>
          <li>
            <a className="text-primary-700 hover:underline" href="/docs/TP_RPC.pdf" target="_blank" rel="noreferrer">
              Enunciado del Trabajo Práctico
            </a>
          </li>
        </ul>
      </div>
    </div>
  );
}

export default Login;
