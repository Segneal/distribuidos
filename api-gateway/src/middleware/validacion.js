// Input validation middleware using express-validator
const { body, param, query, validationResult } = require('express-validator');
const { ROLES, CATEGORIAS_DONACION, VALIDATION_RULES, ERROR_CODES } = require('../config/constants');

/**
 * Middleware to handle validation errors
 */
const manejarErroresValidacion = (req, res, next) => {
  const errors = validationResult(req);
  
  if (!errors.isEmpty()) {
    const errorDetails = errors.array().map(error => ({
      campo: error.path || error.param,
      valor: error.value,
      mensaje: error.msg,
      ubicacion: error.location
    }));

    return res.status(400).json({
      error: 'Validation Error',
      mensaje: 'Datos de entrada inválidos',
      codigo: ERROR_CODES.VALIDATION_ERROR,
      detalles: errorDetails
    });
  }
  
  next();
};

/**
 * Validation rules for user authentication
 */
const validarLogin = [
  body('identificador')
    .notEmpty()
    .withMessage('El identificador (usuario o email) es requerido')
    .isLength({ min: 3, max: 255 })
    .withMessage('El identificador debe tener entre 3 y 255 caracteres'),
  
  body('clave')
    .notEmpty()
    .withMessage('La contraseña es requerida')
    .isLength({ min: 1 })
    .withMessage('La contraseña no puede estar vacía'),
  
  manejarErroresValidacion
];

/**
 * Validation rules for creating users
 */
const validarCrearUsuario = [
  body('nombreUsuario')
    .notEmpty()
    .withMessage('El nombre de usuario es requerido')
    .isLength({ 
      min: VALIDATION_RULES.NOMBRE_USUARIO.MIN_LENGTH, 
      max: VALIDATION_RULES.NOMBRE_USUARIO.MAX_LENGTH 
    })
    .withMessage(`El nombre de usuario debe tener entre ${VALIDATION_RULES.NOMBRE_USUARIO.MIN_LENGTH} y ${VALIDATION_RULES.NOMBRE_USUARIO.MAX_LENGTH} caracteres`)
    .matches(VALIDATION_RULES.NOMBRE_USUARIO.PATTERN)
    .withMessage('El nombre de usuario solo puede contener letras, números y guiones bajos'),
  
  body('nombre')
    .notEmpty()
    .withMessage('El nombre es requerido')
    .isLength({ 
      min: VALIDATION_RULES.NOMBRE.MIN_LENGTH, 
      max: VALIDATION_RULES.NOMBRE.MAX_LENGTH 
    })
    .withMessage(`El nombre debe tener entre ${VALIDATION_RULES.NOMBRE.MIN_LENGTH} y ${VALIDATION_RULES.NOMBRE.MAX_LENGTH} caracteres`)
    .matches(VALIDATION_RULES.NOMBRE.PATTERN)
    .withMessage('El nombre solo puede contener letras y espacios'),
  
  body('apellido')
    .notEmpty()
    .withMessage('El apellido es requerido')
    .isLength({ 
      min: VALIDATION_RULES.NOMBRE.MIN_LENGTH, 
      max: VALIDATION_RULES.NOMBRE.MAX_LENGTH 
    })
    .withMessage(`El apellido debe tener entre ${VALIDATION_RULES.NOMBRE.MIN_LENGTH} y ${VALIDATION_RULES.NOMBRE.MAX_LENGTH} caracteres`)
    .matches(VALIDATION_RULES.NOMBRE.PATTERN)
    .withMessage('El apellido solo puede contener letras y espacios'),
  
  body('email')
    .isEmail()
    .withMessage('Debe proporcionar un email válido')
    .normalizeEmail(),
  
  body('telefono')
    .optional()
    .isLength({ 
      min: VALIDATION_RULES.TELEFONO.MIN_LENGTH, 
      max: VALIDATION_RULES.TELEFONO.MAX_LENGTH 
    })
    .withMessage(`El teléfono debe tener entre ${VALIDATION_RULES.TELEFONO.MIN_LENGTH} y ${VALIDATION_RULES.TELEFONO.MAX_LENGTH} caracteres`)
    .matches(VALIDATION_RULES.TELEFONO.PATTERN)
    .withMessage('El teléfono contiene caracteres inválidos'),
  
  body('rol')
    .isIn(Object.values(ROLES))
    .withMessage(`El rol debe ser uno de: ${Object.values(ROLES).join(', ')}`),
  
  manejarErroresValidacion
];

/**
 * Validation rules for updating users
 */
const validarActualizarUsuario = [
  param('id')
    .isInt({ min: 1 })
    .withMessage('El ID del usuario debe ser un número entero positivo'),
  
  body('nombre')
    .optional()
    .isLength({ 
      min: VALIDATION_RULES.NOMBRE.MIN_LENGTH, 
      max: VALIDATION_RULES.NOMBRE.MAX_LENGTH 
    })
    .withMessage(`El nombre debe tener entre ${VALIDATION_RULES.NOMBRE.MIN_LENGTH} y ${VALIDATION_RULES.NOMBRE.MAX_LENGTH} caracteres`)
    .matches(VALIDATION_RULES.NOMBRE.PATTERN)
    .withMessage('El nombre solo puede contener letras y espacios'),
  
  body('apellido')
    .optional()
    .isLength({ 
      min: VALIDATION_RULES.NOMBRE.MIN_LENGTH, 
      max: VALIDATION_RULES.NOMBRE.MAX_LENGTH 
    })
    .withMessage(`El apellido debe tener entre ${VALIDATION_RULES.NOMBRE.MIN_LENGTH} y ${VALIDATION_RULES.NOMBRE.MAX_LENGTH} caracteres`)
    .matches(VALIDATION_RULES.NOMBRE.PATTERN)
    .withMessage('El apellido solo puede contener letras y espacios'),
  
  body('email')
    .optional()
    .isEmail()
    .withMessage('Debe proporcionar un email válido')
    .normalizeEmail(),
  
  body('telefono')
    .optional()
    .isLength({ 
      min: VALIDATION_RULES.TELEFONO.MIN_LENGTH, 
      max: VALIDATION_RULES.TELEFONO.MAX_LENGTH 
    })
    .withMessage(`El teléfono debe tener entre ${VALIDATION_RULES.TELEFONO.MIN_LENGTH} y ${VALIDATION_RULES.TELEFONO.MAX_LENGTH} caracteres`)
    .matches(VALIDATION_RULES.TELEFONO.PATTERN)
    .withMessage('El teléfono contiene caracteres inválidos'),
  
  body('rol')
    .optional()
    .isIn(Object.values(ROLES))
    .withMessage(`El rol debe ser uno de: ${Object.values(ROLES).join(', ')}`),
  
  manejarErroresValidacion
];

/**
 * Validation rules for creating donations
 */
const validarCrearDonacion = [
  body('categoria')
    .isIn(Object.values(CATEGORIAS_DONACION))
    .withMessage(`La categoría debe ser una de: ${Object.values(CATEGORIAS_DONACION).join(', ')}`),
  
  body('descripcion')
    .notEmpty()
    .withMessage('La descripción es requerida')
    .isLength({ 
      min: VALIDATION_RULES.DESCRIPCION.MIN_LENGTH, 
      max: VALIDATION_RULES.DESCRIPCION.MAX_LENGTH 
    })
    .withMessage(`La descripción debe tener entre ${VALIDATION_RULES.DESCRIPCION.MIN_LENGTH} y ${VALIDATION_RULES.DESCRIPCION.MAX_LENGTH} caracteres`),
  
  body('cantidad')
    .isInt({ 
      min: VALIDATION_RULES.CANTIDAD.MIN, 
      max: VALIDATION_RULES.CANTIDAD.MAX 
    })
    .withMessage(`La cantidad debe ser un número entero entre ${VALIDATION_RULES.CANTIDAD.MIN} y ${VALIDATION_RULES.CANTIDAD.MAX}`),
  
  manejarErroresValidacion
];

/**
 * Validation rules for updating donations
 */
const validarActualizarDonacion = [
  param('id')
    .isInt({ min: 1 })
    .withMessage('El ID de la donación debe ser un número entero positivo'),
  
  body('descripcion')
    .optional()
    .isLength({ 
      min: VALIDATION_RULES.DESCRIPCION.MIN_LENGTH, 
      max: VALIDATION_RULES.DESCRIPCION.MAX_LENGTH 
    })
    .withMessage(`La descripción debe tener entre ${VALIDATION_RULES.DESCRIPCION.MIN_LENGTH} y ${VALIDATION_RULES.DESCRIPCION.MAX_LENGTH} caracteres`),
  
  body('cantidad')
    .optional()
    .isInt({ 
      min: VALIDATION_RULES.CANTIDAD.MIN, 
      max: VALIDATION_RULES.CANTIDAD.MAX 
    })
    .withMessage(`La cantidad debe ser un número entero entre ${VALIDATION_RULES.CANTIDAD.MIN} y ${VALIDATION_RULES.CANTIDAD.MAX}`),
  
  manejarErroresValidacion
];

/**
 * Validation rules for creating events
 */
const validarCrearEvento = [
  body('nombre')
    .notEmpty()
    .withMessage('El nombre del evento es requerido')
    .isLength({ 
      min: VALIDATION_RULES.NOMBRE_EVENTO.MIN_LENGTH, 
      max: VALIDATION_RULES.NOMBRE_EVENTO.MAX_LENGTH 
    })
    .withMessage(`El nombre debe tener entre ${VALIDATION_RULES.NOMBRE_EVENTO.MIN_LENGTH} y ${VALIDATION_RULES.NOMBRE_EVENTO.MAX_LENGTH} caracteres`),
  
  body('descripcion')
    .notEmpty()
    .withMessage('La descripción del evento es requerida')
    .isLength({ 
      min: VALIDATION_RULES.DESCRIPCION_EVENTO.MIN_LENGTH, 
      max: VALIDATION_RULES.DESCRIPCION_EVENTO.MAX_LENGTH 
    })
    .withMessage(`La descripción debe tener entre ${VALIDATION_RULES.DESCRIPCION_EVENTO.MIN_LENGTH} y ${VALIDATION_RULES.DESCRIPCION_EVENTO.MAX_LENGTH} caracteres`),
  
  body('fechaHora')
    .isISO8601()
    .withMessage('La fecha debe estar en formato ISO 8601 (YYYY-MM-DDTHH:mm:ss.sssZ)')
    .custom((value) => {
      const eventDate = new Date(value);
      const now = new Date();
      if (eventDate <= now) {
        throw new Error('La fecha del evento debe ser futura');
      }
      return true;
    }),
  
  manejarErroresValidacion
];

/**
 * Validation rules for updating events
 */
const validarActualizarEvento = [
  param('id')
    .isInt({ min: 1 })
    .withMessage('El ID del evento debe ser un número entero positivo'),
  
  body('nombre')
    .optional()
    .isLength({ 
      min: VALIDATION_RULES.NOMBRE_EVENTO.MIN_LENGTH, 
      max: VALIDATION_RULES.NOMBRE_EVENTO.MAX_LENGTH 
    })
    .withMessage(`El nombre debe tener entre ${VALIDATION_RULES.NOMBRE_EVENTO.MIN_LENGTH} y ${VALIDATION_RULES.NOMBRE_EVENTO.MAX_LENGTH} caracteres`),
  
  body('descripcion')
    .optional()
    .isLength({ 
      min: VALIDATION_RULES.DESCRIPCION_EVENTO.MIN_LENGTH, 
      max: VALIDATION_RULES.DESCRIPCION_EVENTO.MAX_LENGTH 
    })
    .withMessage(`La descripción debe tener entre ${VALIDATION_RULES.DESCRIPCION_EVENTO.MIN_LENGTH} y ${VALIDATION_RULES.DESCRIPCION_EVENTO.MAX_LENGTH} caracteres`),
  
  body('fechaHora')
    .optional()
    .isISO8601()
    .withMessage('La fecha debe estar en formato ISO 8601 (YYYY-MM-DDTHH:mm:ss.sssZ)'),
  
  manejarErroresValidacion
];

/**
 * Validation rules for managing event participants
 */
const validarParticipanteEvento = [
  param('id')
    .isInt({ min: 1 })
    .withMessage('El ID del evento debe ser un número entero positivo'),
  
  body('usuarioId')
    .isInt({ min: 1 })
    .withMessage('El ID del usuario debe ser un número entero positivo'),
  
  manejarErroresValidacion
];

/**
 * Common parameter validations
 */
const validarId = [
  param('id')
    .isInt({ min: 1 })
    .withMessage('El ID debe ser un número entero positivo'),
  
  manejarErroresValidacion
];

/**
 * Query parameter validations for listing
 */
const validarParametrosListado = [
  query('page')
    .optional()
    .isInt({ min: 1 })
    .withMessage('La página debe ser un número entero positivo'),
  
  query('limit')
    .optional()
    .isInt({ min: 1, max: 100 })
    .withMessage('El límite debe ser un número entero entre 1 y 100'),
  
  query('search')
    .optional()
    .isLength({ min: 1, max: 255 })
    .withMessage('El término de búsqueda debe tener entre 1 y 255 caracteres'),
  
  manejarErroresValidacion
];

module.exports = {
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
};