import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext.jsx';

function Home() {
  const { isAuthenticated, user } = useAuth();

  return (
    <div className="space-y-10">
      <section className="rounded-2xl bg-white px-8 py-10 shadow-sm">
        <h1 className="text-3xl font-bold text-slate-800 sm:text-4xl">
          Plataforma de gestión para la ONG "Empuje Comunitario"
        </h1>
        <p className="mt-4 max-w-3xl text-lg text-slate-600">
          Administrá usuarios, inventario de donaciones y eventos solidarios desde un único lugar. Este
          frontend se integra con el API Gateway gRPC que ya construimos y respeta los permisos
          configurados según tu rol dentro de la organización.
        </p>
        <div className="mt-6 flex flex-wrap items-center gap-3">
          <Link
            to={isAuthenticated ? '/eventos' : '/login'}
            className="rounded-md bg-primary-600 px-5 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-primary-700"
          >
            {isAuthenticated ? 'Ir a eventos' : 'Iniciar sesión'}
          </Link>
          <a
            href="/docs/TP_RPC.pdf"
            target="_blank"
            rel="noreferrer"
            className="rounded-md border border-primary-200 px-5 py-3 text-sm font-semibold text-primary-700 transition hover:border-primary-300 hover:bg-primary-50"
          >
            Ver enunciado
          </a>
        </div>
      </section>

      <section className="grid gap-6 lg:grid-cols-3">
        {[
          {
            title: 'Gestión de roles',
            description:
              'Los permisos se aplican automáticamente según el rol provisto por el servicio de usuarios: Presidente, Vocal, Coordinador o Voluntario.',
          },
          {
            title: 'Eventos solidarios',
            description:
              'Consultá el calendario, anotate en actividades y administrá participantes conforme a las reglas de negocio definidas en el backend.',
          },
          {
            title: 'Arquitectura gRPC',
            description:
              'La aplicación web se comunica con el API Gateway del proyecto, que a su vez orquesta los microservicios gRPC existentes.',
          },
        ].map((item) => (
          <article key={item.title} className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="text-lg font-semibold text-slate-800">{item.title}</h2>
            <p className="mt-2 text-sm text-slate-600">{item.description}</p>
          </article>
        ))}
      </section>

      {isAuthenticated && user && (
        <section className="rounded-2xl border border-primary-100 bg-primary-50 p-6">
          <h2 className="text-lg font-semibold text-primary-800">Tu sesión</h2>
          <ul className="mt-3 space-y-1 text-sm text-primary-700">
            <li>
              <span className="font-medium">Nombre:</span> {user.nombre} {user.apellido}
            </li>
            <li>
              <span className="font-medium">Usuario:</span> {user.nombreUsuario}
            </li>
            <li>
              <span className="font-medium">Rol:</span> {user.rol}
            </li>
          </ul>
        </section>
      )}
    </div>
  );
}

export default Home;
