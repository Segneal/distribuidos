// Authentication middleware for JWT token validation
const jwt = require('jsonwebtoken');
const UsuarioClient = require('../grpc-clients/usuarioClient');

const usuarioClient = new UsuarioClient();

/**
 * Middleware to authenticate JWT tokens
 * Validates token and adds user information to request object
 */
const autenticarToken = async (req, res, next) => {
  try {
    // Get token from Authorization header
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1]; // Bearer TOKEN

    if (!token) {
      return res.status(401).json({
        error: 'Unauthorized',
        mensaje: 'Token de acceso requerido',
        codigo: 'TOKEN_MISSING'
      });
    }

    // Validate token with user service
    try {
      const validationResponse = await usuarioClient.validarToken({ token });
      
      if (!validationResponse.valido) {
        return res.status(401).json({
          error: 'Unauthorized',
          mensaje: validationResponse.mensaje || 'Token inválido',
          codigo: 'TOKEN_INVALID'
        });
      }

      // Add user information to request
      req.usuario = {
        id: validationResponse.usuario.id,
        nombreUsuario: validationResponse.usuario.nombreUsuario,
        nombre: validationResponse.usuario.nombre,
        apellido: validationResponse.usuario.apellido,
        email: validationResponse.usuario.email,
        rol: validationResponse.usuario.rol,
        activo: validationResponse.usuario.activo
      };

      // Check if user is active
      if (!req.usuario.activo) {
        return res.status(401).json({
          error: 'Unauthorized',
          mensaje: 'Usuario inactivo',
          codigo: 'USER_INACTIVE'
        });
      }

      next();
    } catch (grpcError) {
      console.error('Error validating token with user service:', grpcError);
      
      // Handle specific gRPC errors
      if (grpcError.code === 16) { // UNAUTHENTICATED
        return res.status(401).json({
          error: 'Unauthorized',
          mensaje: 'Token inválido o expirado',
          codigo: 'TOKEN_INVALID'
        });
      }
      
      if (grpcError.code === 5) { // NOT_FOUND
        return res.status(401).json({
          error: 'Unauthorized',
          mensaje: 'Usuario no encontrado',
          codigo: 'USER_NOT_FOUND'
        });
      }

      // Service unavailable
      return res.status(503).json({
        error: 'Service Unavailable',
        mensaje: 'Servicio de autenticación no disponible',
        codigo: 'AUTH_SERVICE_UNAVAILABLE'
      });
    }
  } catch (error) {
    console.error('Authentication middleware error:', error);
    return res.status(500).json({
      error: 'Internal Server Error',
      mensaje: 'Error interno en la autenticación',
      codigo: 'AUTH_INTERNAL_ERROR'
    });
  }
};

/**
 * Optional authentication middleware
 * Adds user information if token is present and valid, but doesn't require it
 */
const autenticacionOpcional = async (req, res, next) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    // No token provided, continue without user info
    req.usuario = null;
    return next();
  }

  try {
    const validationResponse = await usuarioClient.validarToken({ token });
    
    if (validationResponse.valido && validationResponse.usuario.activo) {
      req.usuario = {
        id: validationResponse.usuario.id,
        nombreUsuario: validationResponse.usuario.nombreUsuario,
        nombre: validationResponse.usuario.nombre,
        apellido: validationResponse.usuario.apellido,
        email: validationResponse.usuario.email,
        rol: validationResponse.usuario.rol,
        activo: validationResponse.usuario.activo
      };
    } else {
      req.usuario = null;
    }
  } catch (error) {
    // If token validation fails, continue without user info
    req.usuario = null;
  }

  next();
};

module.exports = {
  autenticarToken,
  autenticacionOpcional
};