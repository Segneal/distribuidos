# Frontend ONG Empuje Comunitario

Aplicacion web creada con Vite + React + TailwindCSS para interactuar con el API Gateway existente del trabajo practico de Sistemas Distribuidos. Implementa las paginas iniciales (Home, Login y Eventos solidarios) respetando el esquema de autenticacion y los permisos definidos en el backend.

## Requisitos locales

- Node.js 18+ (se recomienda utilizar la misma version usada por el gateway)
- Dependencias instaladas con `npm install`

## Puesta en marcha (modo local)

```bash
cd frontend
npm install
VITE_API_BASE_URL=http://localhost:3000 npm run dev
```

> Nota: `VITE_API_BASE_URL` apunta al gateway que corre en `http://localhost:3000`. Si el gateway vive en otro host/puerto, ajusta ese valor.

## Contenedor Docker

La SPA se puede construir y servir dentro de Docker usando el `docker-compose.yml` del proyecto:

```bash
docker compose build frontend
docker compose up -d frontend
```

- La app queda expuesta en `http://localhost:5173`.
- Las peticiones siguen yendo al gateway publicado en `http://localhost:3000`; asegurate de levantar el servicio `api-gateway` (y sus dependencias) antes o junto con el frontend.
- El gateway necesita permitir el origen del frontend mediante la variable `FRONTEND_URL` (ya declarada por defecto como `http://localhost:5173`).

Para regenerar el build de produccion manualmente:

```bash
npm run build
npm run preview
```

El artefacto final queda en `frontend/dist/`.

## Funcionalidades iniciales

- **Home**: resumen de la solucion y accesos rapidos.
- **Login**: formulario que envia credenciales al endpoint `/api/auth/login`, persistiendo token y datos del usuario.
- **Eventos solidarios**: listado de eventos que permite agregarse o quitarse mediante los endpoints del gateway (`POST /api/eventos/:id/participantes` y `DELETE /api/eventos/:id/participantes/:usuarioId`).
- Navbar adaptativo segun sesion activa (rol y nombre visibles, opcion de logout).

El estado de autenticacion se almacena en `localStorage` y se revalida consultando `/api/auth/perfil`. Todas las peticiones incluyen automaticamente el token JWT.

## Proximos pasos sugeridos

1. Implementar las vistas restantes (Inventario y Usuarios) reutilizando el contexto de autenticacion.
2. Anadir manejo de errores mas granular (toasts, estados vacios especificos).
3. Integrar tests de componentes (por ejemplo con Vitest + Testing Library) una vez estabilizada la UI.
