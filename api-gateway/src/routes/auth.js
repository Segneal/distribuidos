// Authentication routes
const express = require('express');
const router = express.Router();

// Import middleware
const { autenticarToken } = require('../middleware/autenticacion');
const { validarLogin } = require('../middleware/validacion');

// Import gRPC client
const UsuarioClient = require('../grpc-clients/usuarioClient');
const usuarioClient = new UsuarioClient();

/**
 * @swagger
 * /api/auth/login:
 *   post:
 *     summary: Autenticar usuario
 *     tags: [Autenticación]
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - identificador
 *               - clave
 *             properties:
 *               identificador:
 *                 type: string
 *                 description: Nombre de usuario o email
 *               clave:
 *                 type: string
 *                 description: Contraseña del usuario
 *     responses:
 *       200:
 *         description: Login exitoso
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 token:
 *                   type: string
 *                 usuario:
 *                   $ref: '#/components/schemas/Usuario'
 *       401:
 *         description: Credenciales inválidas
 *       400:
 *         description: Datos de entrada inválidos
 */
router.post('/login', validarLogin, async (req, res) => {
  try {
    const { identificador, clave } = req.body;

    // Call user service for authentication
    const response = await usuarioClient.autenticarUsuario({
      identificador,
      clave
    });

    if (response.exitoso) {
      res.json({
        mensaje: 'Login exitoso',
        token: response.token,
        usuario: {
          id: response.usuario.id,
          nombreUsuario: response.usuario.nombreUsuario,
          nombre: response.usuario.nombre,
          apellido: response.usuario.apellido,
          email: response.usuario.email,
          rol: response.usuario.rol,
          activo: response.usuario.activo
        }
      });
    } else {
      res.status(401).json({
        error: 'Unauthorized',
        mensaje: response.mensaje || 'Credenciales inválidas',
        codigo: 'INVALID_CREDENTIALS'
      });
    }
  } catch (error) {
    console.error('Error en login:', error);

    // Handle specific gRPC errors
    if (error.code === 16) { // UNAUTHENTICATED
      return res.status(401).json({
        error: 'Unauthorized',
        mensaje: 'Credenciales inválidas',
        codigo: 'INVALID_CREDENTIALS'
      });
    }

    if (error.code === 5) { // NOT_FOUND
      return res.status(401).json({
        error: 'Unauthorized',
        mensaje: 'Usuario/email inexistente',
        codigo: 'USER_NOT_FOUND'
      });
    }

    if (error.code === 14) { // UNAVAILABLE
      return res.status(503).json({
        error: 'Service Unavailable',
        mensaje: 'Servicio de autenticación no disponible',
        codigo: 'AUTH_SERVICE_UNAVAILABLE'
      });
    }

    res.status(500).json({
      error: 'Internal Server Error',
      mensaje: 'Error interno del servidor',
      codigo: 'INTERNAL_ERROR'
    });
  }
});

/**
 * @swagger
 * /api/auth/logout:
 *   post:
 *     summary: Cerrar sesión
 *     tags: [Autenticación]
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       200:
 *         description: Logout exitoso
 *       401:
 *         description: Token inválido
 */
router.post('/logout', autenticarToken, (req, res) => {
  // Since we're using stateless JWT tokens, logout is handled client-side
  // The client should remove the token from storage
  res.json({
    mensaje: 'Logout exitoso. El token debe ser eliminado del cliente.',
    codigo: 'LOGOUT_SUCCESS'
  });
});

/**
 * @swagger
 * /api/auth/perfil:
 *   get:
 *     summary: Obtener perfil del usuario autenticado
 *     tags: [Autenticación]
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       200:
 *         description: Perfil del usuario
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/Usuario'
 *       401:
 *         description: Token inválido
 */
router.get('/perfil', autenticarToken, (req, res) => {
  // Return user information from the authenticated token
  res.json({
    usuario: {
      id: req.usuario.id,
      nombreUsuario: req.usuario.nombreUsuario,
      nombre: req.usuario.nombre,
      apellido: req.usuario.apellido,
      email: req.usuario.email,
      rol: req.usuario.rol,
      activo: req.usuario.activo
    }
  });
});

module.exports = router;