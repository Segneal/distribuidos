// Middleware exports
const { autenticarToken, autenticacionOpcional } = require('./autenticacion');
const { 
  autorizarRol, 
  autorizarPropioRecursoOAdmin, 
  autorizarModificacionPropiaOAdmin,
  autorizarAutoAsignacionVoluntario,
  autorizarCualquiera 
} = require('./autorizacion');
const {
  manejarErroresValidacion,
  validarLogin,
  validarCrearUsuario,
  validarActualizarUsuario,
  validarCrearDonacion,
  validarActualizarDonacion,
  validarCrearEvento,
  validarActualizarEvento,
  validarParticipanteEvento,
  validarId,
  validarParametrosListado
} = require('./validacion');
const {
  handleGrpcError,
  handleGeneralError,
  handleNotFound,
  asyncHandler,
  requestLogger
} = require('./errorHandler');
const corsMiddleware = require('./cors');
const { securityMiddleware, rateLimiters } = require('./security');

module.exports = {
  // Authentication
  autenticarToken,
  autenticacionOpcional,
  
  // Authorization
  autorizarRol,
  autorizarPropioRecursoOAdmin,
  autorizarModificacionPropiaOAdmin,
  autorizarAutoAsignacionVoluntario,
  autorizarCualquiera,
  
  // Validation
  manejarErroresValidacion,
  validarLogin,
  validarCrearUsuario,
  validarActualizarUsuario,
  validarCrearDonacion,
  validarActualizarDonacion,
  validarCrearEvento,
  validarActualizarEvento,
  validarParticipanteEvento,
  validarId,
  validarParametrosListado,
  
  // Error handling
  handleGrpcError,
  handleGeneralError,
  handleNotFound,
  asyncHandler,
  requestLogger,
  
  // Security
  corsMiddleware,
  securityMiddleware,
  rateLimiters
};