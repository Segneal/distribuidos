# API Gateway Middleware

This directory contains all middleware implementations for the API Gateway, providing authentication, authorization, validation, and error handling capabilities.

## Middleware Components

### Authentication (`autenticacion.js`)

Handles JWT token validation and user authentication.

**Functions:**
- `autenticarToken`: Validates JWT tokens and adds user info to request
- `autenticacionOpcional`: Optional authentication for public endpoints

**Usage:**
```javascript
const { autenticarToken } = require('./middleware');

// Require authentication
app.get('/protected', autenticarToken, (req, res) => {
  // req.usuario contains authenticated user info
  res.json({ user: req.usuario });
});
```

### Authorization (`autorizacion.js`)

Implements role-based access control (RBAC).

**Functions:**
- `autorizarRol(roles)`: Checks if user has required role(s)
- `autorizarPropioRecursoOAdmin(param)`: Allows access to own resources or admin
- `autorizarModificacionPropiaOAdmin(param)`: Allows modification of own resources or admin
- `autorizarAutoAsignacionVoluntario()`: Special logic for volunteer self-assignment
- `autorizarCualquiera(middlewares)`: OR logic for multiple authorization conditions

**Usage:**
```javascript
const { autorizarRol } = require('./middleware');
const { ROLES } = require('../config/constants');

// Only Presidente can access
app.get('/admin', autenticarToken, autorizarRol([ROLES.PRESIDENTE]), handler);

// Presidente or Vocal can access
app.get('/inventory', autenticarToken, autorizarRol([ROLES.PRESIDENTE, ROLES.VOCAL]), handler);
```

### Validation (`validacion.js`)

Input validation using express-validator.

**Functions:**
- `validarLogin`: Validates login credentials
- `validarCrearUsuario`: Validates user creation data
- `validarActualizarUsuario`: Validates user update data
- `validarCrearDonacion`: Validates donation creation
- `validarActualizarDonacion`: Validates donation updates
- `validarCrearEvento`: Validates event creation
- `validarActualizarEvento`: Validates event updates
- `validarParticipanteEvento`: Validates event participant operations
- `validarId`: Validates ID parameters
- `validarParametrosListado`: Validates query parameters for listing

**Usage:**
```javascript
const { validarCrearUsuario } = require('./middleware');

app.post('/usuarios', validarCrearUsuario, (req, res) => {
  // Input is validated, proceed with creation
});
```

### Error Handling (`errorHandler.js`)

Centralized error handling for gRPC and general errors.

**Functions:**
- `handleGrpcError`: Converts gRPC errors to HTTP responses
- `handleGeneralError`: Handles general application errors
- `handleNotFound`: 404 error handler
- `asyncHandler`: Wrapper for async route handlers
- `requestLogger`: Logs all requests and responses

**Usage:**
```javascript
const { handleGrpcError, handleGeneralError, asyncHandler } = require('./middleware');

// Wrap async handlers
app.get('/async-route', asyncHandler(async (req, res) => {
  const result = await someAsyncOperation();
  res.json(result);
}));

// Add error handlers at the end
app.use(handleGrpcError);
app.use(handleGeneralError);
```

### Security (`security.js`)

Security middleware using Helmet and rate limiting.

**Components:**
- `securityMiddleware`: Helmet configuration for security headers
- `rateLimiters`: Different rate limits for different endpoint types

### CORS (`cors.js`)

Cross-Origin Resource Sharing configuration.

## Constants (`../config/constants.js`)

Defines application constants including:
- `ROLES`: User roles (PRESIDENTE, VOCAL, COORDINADOR, VOLUNTARIO)
- `CATEGORIAS_DONACION`: Donation categories
- `HTTP_STATUS`: HTTP status codes
- `GRPC_STATUS`: gRPC status codes
- `ERROR_CODES`: Application error codes
- `VALIDATION_RULES`: Input validation rules

## Middleware Chain Example

```javascript
const {
  securityMiddleware,
  rateLimiters,
  corsMiddleware,
  requestLogger,
  autenticarToken,
  autorizarRol,
  validarCrearUsuario,
  handleGrpcError,
  handleGeneralError,
  handleNotFound
} = require('./middleware');

const app = express();

// Security and CORS
app.use(securityMiddleware);
app.use(rateLimiters.general);
app.use(corsMiddleware);

// Body parsing and logging
app.use(express.json());
app.use(requestLogger);

// Protected route example
app.post('/api/usuarios',
  rateLimiters.api,                    // Rate limiting
  autenticarToken,                     // Authentication required
  autorizarRol([ROLES.PRESIDENTE]),    // Only Presidente can create users
  validarCrearUsuario,                 // Validate input
  async (req, res) => {
    // Route handler
  }
);

// Error handling (must be last)
app.use(handleGrpcError);
app.use(handleGeneralError);
app.use('*', handleNotFound);
```

## Error Response Format

All errors follow a consistent format:

```json
{
  "error": "Error Type",
  "mensaje": "User-friendly message in Spanish",
  "codigo": "ERROR_CODE",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "path": "/api/endpoint",
  "method": "POST",
  "detalles": "Additional details (optional)"
}
```

## Testing

Middleware components are tested in `../tests/middleware.test.js` with comprehensive test coverage including:
- Authentication scenarios (valid/invalid tokens, inactive users)
- Authorization scenarios (role-based access control)
- Validation scenarios (valid/invalid input)
- Error handling scenarios (gRPC errors, general errors)

Run tests with:
```bash
npm test src/tests/middleware.test.js
```