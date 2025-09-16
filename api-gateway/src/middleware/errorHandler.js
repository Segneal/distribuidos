// Centralized error handling middleware
const { HTTP_STATUS, GRPC_STATUS, ERROR_CODES } = require('../config/constants');

/**
 * Maps gRPC status codes to HTTP status codes
 */
const mapGrpcToHttpStatus = (grpcCode) => {
  const statusMap = {
    [GRPC_STATUS.OK]: HTTP_STATUS.OK,
    [GRPC_STATUS.INVALID_ARGUMENT]: HTTP_STATUS.BAD_REQUEST,
    [GRPC_STATUS.NOT_FOUND]: HTTP_STATUS.NOT_FOUND,
    [GRPC_STATUS.ALREADY_EXISTS]: HTTP_STATUS.CONFLICT,
    [GRPC_STATUS.PERMISSION_DENIED]: HTTP_STATUS.FORBIDDEN,
    [GRPC_STATUS.UNAUTHENTICATED]: HTTP_STATUS.UNAUTHORIZED,
    [GRPC_STATUS.RESOURCE_EXHAUSTED]: HTTP_STATUS.SERVICE_UNAVAILABLE,
    [GRPC_STATUS.FAILED_PRECONDITION]: HTTP_STATUS.UNPROCESSABLE_ENTITY,
    [GRPC_STATUS.UNAVAILABLE]: HTTP_STATUS.SERVICE_UNAVAILABLE,
    [GRPC_STATUS.INTERNAL]: HTTP_STATUS.INTERNAL_SERVER_ERROR,
    [GRPC_STATUS.UNIMPLEMENTED]: HTTP_STATUS.NOT_FOUND,
    [GRPC_STATUS.DEADLINE_EXCEEDED]: HTTP_STATUS.SERVICE_UNAVAILABLE
  };
  
  return statusMap[grpcCode] || HTTP_STATUS.INTERNAL_SERVER_ERROR;
};

/**
 * Maps gRPC errors to user-friendly messages
 */
const mapGrpcErrorMessage = (grpcCode, originalMessage) => {
  const messageMap = {
    [GRPC_STATUS.INVALID_ARGUMENT]: 'Datos de entrada inválidos',
    [GRPC_STATUS.NOT_FOUND]: 'Recurso no encontrado',
    [GRPC_STATUS.ALREADY_EXISTS]: 'El recurso ya existe',
    [GRPC_STATUS.PERMISSION_DENIED]: 'Permisos insuficientes',
    [GRPC_STATUS.UNAUTHENTICATED]: 'Autenticación requerida',
    [GRPC_STATUS.RESOURCE_EXHAUSTED]: 'Servicio temporalmente no disponible',
    [GRPC_STATUS.FAILED_PRECONDITION]: 'Operación no permitida en el estado actual',
    [GRPC_STATUS.UNAVAILABLE]: 'Servicio no disponible',
    [GRPC_STATUS.INTERNAL]: 'Error interno del servicio',
    [GRPC_STATUS.UNIMPLEMENTED]: 'Funcionalidad no implementada',
    [GRPC_STATUS.DEADLINE_EXCEEDED]: 'Tiempo de espera agotado'
  };
  
  return messageMap[grpcCode] || originalMessage || 'Error desconocido';
};

/**
 * Handles gRPC errors and converts them to HTTP responses
 */
const handleGrpcError = (error, req, res, next) => {
  if (error.code !== undefined) {
    // This is a gRPC error
    const httpStatus = mapGrpcToHttpStatus(error.code);
    const userMessage = mapGrpcErrorMessage(error.code, error.details);
    
    console.error(`gRPC Error [${error.code}] on ${req.method} ${req.path}:`, {
      message: error.message,
      details: error.details,
      metadata: error.metadata?.getMap?.() || {},
      userId: req.usuario?.id,
      userRole: req.usuario?.rol
    });
    
    return res.status(httpStatus).json({
      error: getErrorName(httpStatus),
      mensaje: userMessage,
      codigo: getErrorCode(error.code),
      timestamp: new Date().toISOString(),
      path: req.path,
      method: req.method
    });
  }
  
  // Not a gRPC error, pass to next error handler
  next(error);
};

/**
 * General error handling middleware
 */
const handleGeneralError = (error, req, res, next) => {
  // Log the error
  console.error(`General Error on ${req.method} ${req.path}:`, {
    name: error.name,
    message: error.message,
    stack: error.stack,
    userId: req.usuario?.id,
    userRole: req.usuario?.rol,
    body: req.body,
    params: req.params,
    query: req.query
  });
  
  // Handle specific error types
  if (error.name === 'ValidationError') {
    return res.status(HTTP_STATUS.BAD_REQUEST).json({
      error: 'Validation Error',
      mensaje: 'Datos de entrada inválidos',
      codigo: ERROR_CODES.VALIDATION_ERROR,
      detalles: error.message,
      timestamp: new Date().toISOString(),
      path: req.path,
      method: req.method
    });
  }
  
  if (error.name === 'UnauthorizedError' || error.name === 'JsonWebTokenError') {
    return res.status(HTTP_STATUS.UNAUTHORIZED).json({
      error: 'Unauthorized',
      mensaje: 'Token de acceso inválido o expirado',
      codigo: ERROR_CODES.TOKEN_INVALID,
      timestamp: new Date().toISOString(),
      path: req.path,
      method: req.method
    });
  }
  
  if (error.name === 'TokenExpiredError') {
    return res.status(HTTP_STATUS.UNAUTHORIZED).json({
      error: 'Unauthorized',
      mensaje: 'Token de acceso expirado',
      codigo: ERROR_CODES.TOKEN_EXPIRED,
      timestamp: new Date().toISOString(),
      path: req.path,
      method: req.method
    });
  }
  
  if (error.code === 'LIMIT_FILE_SIZE') {
    return res.status(HTTP_STATUS.BAD_REQUEST).json({
      error: 'File Too Large',
      mensaje: 'El archivo es demasiado grande',
      codigo: ERROR_CODES.INVALID_INPUT,
      timestamp: new Date().toISOString(),
      path: req.path,
      method: req.method
    });
  }
  
  if (error.code === 'ECONNREFUSED' || error.code === 'ENOTFOUND') {
    return res.status(HTTP_STATUS.SERVICE_UNAVAILABLE).json({
      error: 'Service Unavailable',
      mensaje: 'Servicio temporalmente no disponible',
      codigo: ERROR_CODES.SERVICE_UNAVAILABLE,
      timestamp: new Date().toISOString(),
      path: req.path,
      method: req.method
    });
  }
  
  // Default error response
  const isDevelopment = process.env.NODE_ENV === 'development';
  
  res.status(HTTP_STATUS.INTERNAL_SERVER_ERROR).json({
    error: 'Internal Server Error',
    mensaje: 'Ha ocurrido un error interno del servidor',
    codigo: ERROR_CODES.INTERNAL_ERROR,
    timestamp: new Date().toISOString(),
    path: req.path,
    method: req.method,
    ...(isDevelopment && {
      stack: error.stack,
      details: error.message
    })
  });
};

/**
 * 404 Not Found handler
 */
const handleNotFound = (req, res) => {
  res.status(HTTP_STATUS.NOT_FOUND).json({
    error: 'Not Found',
    mensaje: 'Ruta no encontrada',
    codigo: ERROR_CODES.RESOURCE_NOT_FOUND,
    timestamp: new Date().toISOString(),
    path: req.path,
    method: req.method,
    availableEndpoints: {
      auth: '/api/auth',
      usuarios: '/api/usuarios',
      inventario: '/api/inventario',
      eventos: '/api/eventos',
      red: '/api/red',
      docs: '/api-docs',
      health: '/health'
    }
  });
};

/**
 * Async error wrapper for route handlers
 */
const asyncHandler = (fn) => {
  return (req, res, next) => {
    Promise.resolve(fn(req, res, next)).catch(next);
  };
};

/**
 * Helper function to get error name from HTTP status
 */
const getErrorName = (httpStatus) => {
  const errorNames = {
    [HTTP_STATUS.BAD_REQUEST]: 'Bad Request',
    [HTTP_STATUS.UNAUTHORIZED]: 'Unauthorized',
    [HTTP_STATUS.FORBIDDEN]: 'Forbidden',
    [HTTP_STATUS.NOT_FOUND]: 'Not Found',
    [HTTP_STATUS.CONFLICT]: 'Conflict',
    [HTTP_STATUS.UNPROCESSABLE_ENTITY]: 'Unprocessable Entity',
    [HTTP_STATUS.INTERNAL_SERVER_ERROR]: 'Internal Server Error',
    [HTTP_STATUS.SERVICE_UNAVAILABLE]: 'Service Unavailable'
  };
  
  return errorNames[httpStatus] || 'Unknown Error';
};

/**
 * Helper function to get error code from gRPC status
 */
const getErrorCode = (grpcCode) => {
  const errorCodes = {
    [GRPC_STATUS.INVALID_ARGUMENT]: ERROR_CODES.INVALID_INPUT,
    [GRPC_STATUS.NOT_FOUND]: ERROR_CODES.RESOURCE_NOT_FOUND,
    [GRPC_STATUS.ALREADY_EXISTS]: ERROR_CODES.DUPLICATE_ENTRY,
    [GRPC_STATUS.PERMISSION_DENIED]: ERROR_CODES.INSUFFICIENT_PERMISSIONS,
    [GRPC_STATUS.UNAUTHENTICATED]: ERROR_CODES.AUTHENTICATION_REQUIRED,
    [GRPC_STATUS.UNAVAILABLE]: ERROR_CODES.SERVICE_UNAVAILABLE,
    [GRPC_STATUS.INTERNAL]: ERROR_CODES.INTERNAL_ERROR
  };
  
  return errorCodes[grpcCode] || ERROR_CODES.INTERNAL_ERROR;
};

/**
 * Request logging middleware
 */
const requestLogger = (req, res, next) => {
  const start = Date.now();
  
  // Log request
  console.log(`${new Date().toISOString()} - ${req.method} ${req.path}`, {
    ip: req.ip,
    userAgent: req.get('User-Agent'),
    userId: req.usuario?.id,
    userRole: req.usuario?.rol,
    body: req.method !== 'GET' ? req.body : undefined,
    query: Object.keys(req.query).length > 0 ? req.query : undefined
  });
  
  // Log response
  const originalSend = res.send;
  res.send = function(data) {
    const duration = Date.now() - start;
    console.log(`${new Date().toISOString()} - ${req.method} ${req.path} - ${res.statusCode} - ${duration}ms`);
    originalSend.call(this, data);
  };
  
  next();
};

module.exports = {
  handleGrpcError,
  handleGeneralError,
  handleNotFound,
  asyncHandler,
  requestLogger,
  mapGrpcToHttpStatus,
  mapGrpcErrorMessage
};