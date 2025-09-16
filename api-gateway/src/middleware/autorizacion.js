// Authorization middleware for role-based access control
const { ROLES } = require('../config/constants');

/**
 * Middleware to authorize users based on their roles
 * @param {string|string[]} rolesPermitidos - Single role or array of roles allowed
 * @returns {Function} Express middleware function
 */
const autorizarRol = (rolesPermitidos) => {
  return (req, res, next) => {
    // Ensure user is authenticated first
    if (!req.usuario) {
      return res.status(401).json({
        error: 'Unauthorized',
        mensaje: 'Autenticación requerida',
        codigo: 'AUTHENTICATION_REQUIRED'
      });
    }

    // Convert single role to array for consistent handling
    const rolesArray = Array.isArray(rolesPermitidos) ? rolesPermitidos : [rolesPermitidos];
    
    // Check if user's role is in the allowed roles
    if (!rolesArray.includes(req.usuario.rol)) {
      return res.status(403).json({
        error: 'Forbidden',
        mensaje: `Acceso denegado. Roles requeridos: ${rolesArray.join(', ')}`,
        codigo: 'INSUFFICIENT_PERMISSIONS',
        rolUsuario: req.usuario.rol,
        rolesRequeridos: rolesArray
      });
    }

    next();
  };
};

/**
 * Middleware to check if user can access their own resource or has admin privileges
 * @param {string} userIdParam - Parameter name containing the user ID (default: 'id')
 * @returns {Function} Express middleware function
 */
const autorizarPropioRecursoOAdmin = (userIdParam = 'id') => {
  return (req, res, next) => {
    if (!req.usuario) {
      return res.status(401).json({
        error: 'Unauthorized',
        mensaje: 'Autenticación requerida',
        codigo: 'AUTHENTICATION_REQUIRED'
      });
    }

    const resourceUserId = parseInt(req.params[userIdParam]);
    const currentUserId = req.usuario.id;
    const userRole = req.usuario.rol;

    // Allow if user is accessing their own resource
    if (resourceUserId === currentUserId) {
      return next();
    }

    // Allow if user has admin privileges (Presidente)
    if (userRole === ROLES.PRESIDENTE) {
      return next();
    }

    return res.status(403).json({
      error: 'Forbidden',
      mensaje: 'Solo puedes acceder a tus propios recursos o necesitas permisos de administrador',
      codigo: 'RESOURCE_ACCESS_DENIED'
    });
  };
};

/**
 * Middleware to check if user can modify their own resource or has admin privileges
 * For operations like updating profile, changing password, etc.
 */
const autorizarModificacionPropiaOAdmin = (userIdParam = 'id') => {
  return (req, res, next) => {
    if (!req.usuario) {
      return res.status(401).json({
        error: 'Unauthorized',
        mensaje: 'Autenticación requerida',
        codigo: 'AUTHENTICATION_REQUIRED'
      });
    }

    const resourceUserId = parseInt(req.params[userIdParam]);
    const currentUserId = req.usuario.id;
    const userRole = req.usuario.rol;

    // Allow if user is modifying their own resource
    if (resourceUserId === currentUserId) {
      return next();
    }

    // Allow if user has admin privileges (Presidente)
    if (userRole === ROLES.PRESIDENTE) {
      return next();
    }

    return res.status(403).json({
      error: 'Forbidden',
      mensaje: 'Solo puedes modificar tus propios recursos o necesitas permisos de administrador',
      codigo: 'RESOURCE_MODIFICATION_DENIED'
    });
  };
};

/**
 * Middleware for Voluntario self-assignment to events
 * Voluntarios can only add/remove themselves from events
 */
const autorizarAutoAsignacionVoluntario = () => {
  return (req, res, next) => {
    if (!req.usuario) {
      return res.status(401).json({
        error: 'Unauthorized',
        mensaje: 'Autenticación requerida',
        codigo: 'AUTHENTICATION_REQUIRED'
      });
    }

    const userRole = req.usuario.rol;
    const currentUserId = req.usuario.id;

    // If user is Voluntario, they can only manage their own participation
    if (userRole === ROLES.VOLUNTARIO) {
      // Check if they're trying to add/remove themselves
      const usuarioId = req.body.usuarioId || req.params.usuarioId;
      
      if (usuarioId && parseInt(usuarioId) !== currentUserId) {
        return res.status(403).json({
          error: 'Forbidden',
          mensaje: 'Los voluntarios solo pueden gestionar su propia participación en eventos',
          codigo: 'SELF_ASSIGNMENT_ONLY'
        });
      }
    }

    // For other roles (Presidente, Coordinador), allow full access
    next();
  };
};

/**
 * Middleware to check multiple authorization conditions with OR logic
 * @param {Function[]} authMiddlewares - Array of authorization middleware functions
 * @returns {Function} Express middleware function
 */
const autorizarCualquiera = (authMiddlewares) => {
  return async (req, res, next) => {
    let lastError = null;
    
    for (const authMiddleware of authMiddlewares) {
      try {
        // Create a mock response to capture authorization results
        const mockRes = {
          status: () => mockRes,
          json: (data) => {
            lastError = data;
            return mockRes;
          }
        };
        
        let authorized = false;
        const mockNext = () => {
          authorized = true;
        };
        
        await authMiddleware(req, mockRes, mockNext);
        
        if (authorized) {
          return next(); // Authorization successful
        }
      } catch (error) {
        lastError = {
          error: 'Authorization Error',
          mensaje: error.message,
          codigo: 'AUTHORIZATION_ERROR'
        };
      }
    }
    
    // If we get here, all authorization attempts failed
    return res.status(403).json(lastError || {
      error: 'Forbidden',
      mensaje: 'No tienes permisos para realizar esta operación',
      codigo: 'ACCESS_DENIED'
    });
  };
};

module.exports = {
  autorizarRol,
  autorizarPropioRecursoOAdmin,
  autorizarModificacionPropiaOAdmin,
  autorizarAutoAsignacionVoluntario,
  autorizarCualquiera
};