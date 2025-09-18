import { Link, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext.jsx';

const linkClasses = ({ isActive }) =>
  `rounded-md px-3 py-2 text-sm font-medium transition-colors ${
    isActive
      ? 'bg-primary-600 text-white shadow'
      : 'text-slate-600 hover:bg-primary-50 hover:text-primary-700'
  }`;

function Navbar() {
  const { isAuthenticated, user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <header className="border-b border-slate-200 bg-white/95 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
        <Link to="/" className="text-lg font-semibold text-primary-700">
          Empuje Comunitario
        </Link>

        <nav className="flex items-center gap-2">
          <NavLink to="/" className={linkClasses} end>
            Inicio
          </NavLink>
          {isAuthenticated && (
            <NavLink to="/eventos" className={linkClasses}>
              Eventos solidarios
            </NavLink>
          )}
        </nav>

        <div className="flex items-center gap-3">
          {isAuthenticated && user ? (
            <>
              <div className="text-right">
                <p className="text-sm font-medium text-slate-700">
                  {user.nombre} {user.apellido}
                </p>
                <p className="text-xs uppercase tracking-wide text-slate-400">{user.rol}</p>
              </div>
              <button
                type="button"
                onClick={handleLogout}
                className="rounded-md border border-primary-100 bg-white px-3 py-2 text-sm font-medium text-primary-700 shadow-sm transition hover:bg-primary-50"
              >
                Cerrar sesión
              </button>
            </>
          ) : (
            <Link
              to="/login"
              className="rounded-md bg-primary-600 px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-primary-700"
            >
              Ingresar
            </Link>
          )}
        </div>
      </div>
    </header>
  );
}

export default Navbar;
