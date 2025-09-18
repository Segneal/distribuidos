import { Link } from 'react-router-dom';

function NotFound() {
  return (
    <div className="mx-auto max-w-lg rounded-2xl border border-slate-200 bg-white p-10 text-center shadow-sm">
      <h1 className="text-3xl font-bold text-slate-800">404</h1>
      <p className="mt-2 text-sm text-slate-600">
        No pudimos encontrar la página solicitada. Volvé al inicio o navegá a una sección disponible.
      </p>
      <div className="mt-6 flex justify-center gap-3">
        <Link
          to="/"
          className="rounded-md bg-primary-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-primary-700"
        >
          Inicio
        </Link>
        <Link
          to="/eventos"
          className="rounded-md border border-primary-200 px-4 py-2 text-sm font-semibold text-primary-700 transition hover:bg-primary-50"
        >
          Eventos
        </Link>
      </div>
    </div>
  );
}

export default NotFound;
