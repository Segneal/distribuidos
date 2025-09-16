// Users routes
const express = require('express');
const router = express.Router();

// Import middleware
const { autenticarToken } = require('../middleware/autenticacion');
const { autorizarRol } = require('../middleware/autorizacion');
const { 
  validarCrearUsuario, 
  validarActualizarUsuario, 
  validarId,
  validarParametrosListado 
} = require('../middleware/validacion');

// Import constants
const { ROLES } = require('../config/constants');

// Import gRPC client
const UsuarioClient = require('../grpc-clients/usuarioClient');
const usuarioClient = new UsuarioClient();

/**
 * @swagger
 * /api/usuarios:
 *   get:
 *     summary: Listar usuarios (solo Presidente)
 *     tags: [Usuarios]
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       200:
 *         description: Lista de usuarios
 *         content:
 *           application/json:
 *             schema:
 *               type: array
 *               items:
 *                 $ref: '#/components/schemas/Usuario'
 *       401:
 *         description: Token inválido
 *       403:
 *         description: Sin permisos suficientes
 */
router.get('/', 
  autenticarToken, 
  autorizarRol([ROLES.PRESIDENTE]), 
  validarParametrosListado,
  async (req, res) => {
    try {
      const { page = 1, limit = 50, search = '' } = req.query;

      const response = await usuarioClient.listarUsuarios({
        page: parseInt(page),
        limit: parseInt(limit),
        search: search.trim()
      });

      res.json({
        usuarios: response.usuarios.map(usuario => ({
          id: usuario.id,
          nombreUsuario: usuario.nombreUsuario,
          nombre: usuario.nombre,
          apellido: usuario.apellido,
          telefono: usuario.telefono,
          email: usuario.email,
          rol: usuario.rol,
          activo: usuario.activo,
          fechaHoraAlta: usuario.fechaHoraAlta,
          usuarioAlta: usuario.usuarioAlta,
          fechaHoraModificacion: usuario.fechaHoraModificacion,
          usuarioModificacion: usuario.usuarioModificacion
        })),
        total: response.total,
        page: parseInt(page),
        limit: parseInt(limit),
        totalPages: Math.ceil(response.total / parseInt(limit))
      });
    } catch (error) {
      console.error('Error al listar usuarios:', error);

      if (error.code === 14) { // UNAVAILABLE
        return res.status(503).json({
          error: 'Service Unavailable',
          mensaje: 'Servicio de usuarios no disponible',
          codigo: 'USER_SERVICE_UNAVAILABLE'
        });
      }

      res.status(500).json({
        error: 'Internal Server Error',
        mensaje: 'Error interno del servidor',
        codigo: 'INTERNAL_ERROR'
      });
    }
  }
);

/**
 * @swagger
 * /api/usuarios/{id}:
 *   get:
 *     summary: Obtener usuario por ID (solo Presidente)
 *     tags: [Usuarios]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: integer
 *         description: ID del usuario
 *     responses:
 *       200:
 *         description: Usuario encontrado
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/Usuario'
 *       401:
 *         description: Token inválido
 *       403:
 *         description: Sin permisos suficientes
 *       404:
 *         description: Usuario no encontrado
 */
router.get('/:id', 
  autenticarToken, 
  autorizarRol([ROLES.PRESIDENTE]), 
  validarId,
  async (req, res) => {
    try {
      const { id } = req.params;

      const response = await usuarioClient.obtenerUsuario({ 
        id: parseInt(id) 
      });

      res.json({
        usuario: {
          id: response.usuario.id,
          nombreUsuario: response.usuario.nombreUsuario,
          nombre: response.usuario.nombre,
          apellido: response.usuario.apellido,
          telefono: response.usuario.telefono,
          email: response.usuario.email,
          rol: response.usuario.rol,
          activo: response.usuario.activo,
          fechaHoraAlta: response.usuario.fechaHoraAlta,
          usuarioAlta: response.usuario.usuarioAlta,
          fechaHoraModificacion: response.usuario.fechaHoraModificacion,
          usuarioModificacion: response.usuario.usuarioModificacion
        }
      });
    } catch (error) {
      console.error('Error al obtener usuario:', error);

      if (error.code === 5) { // NOT_FOUND
        return res.status(404).json({
          error: 'Not Found',
          mensaje: 'Usuario no encontrado',
          codigo: 'RESOURCE_NOT_FOUND'
        });
      }

      if (error.code === 14) { // UNAVAILABLE
        return res.status(503).json({
          error: 'Service Unavailable',
          mensaje: 'Servicio de usuarios no disponible',
          codigo: 'USER_SERVICE_UNAVAILABLE'
        });
      }

      res.status(500).json({
        error: 'Internal Server Error',
        mensaje: 'Error interno del servidor',
        codigo: 'INTERNAL_ERROR'
      });
    }
  }
);

/**
 * @swagger
 * /api/usuarios:
 *   post:
 *     summary: Crear usuario (solo Presidente)
 *     tags: [Usuarios]
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - nombreUsuario
 *               - nombre
 *               - apellido
 *               - email
 *               - rol
 *             properties:
 *               nombreUsuario:
 *                 type: string
 *               nombre:
 *                 type: string
 *               apellido:
 *                 type: string
 *               telefono:
 *                 type: string
 *               email:
 *                 type: string
 *                 format: email
 *               rol:
 *                 type: string
 *                 enum: [PRESIDENTE, VOCAL, COORDINADOR, VOLUNTARIO]
 *     responses:
 *       201:
 *         description: Usuario creado exitosamente
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/Usuario'
 *       400:
 *         description: Datos de entrada inválidos
 *       401:
 *         description: Token inválido
 *       403:
 *         description: Sin permisos suficientes
 */
router.post('/', 
  autenticarToken, 
  autorizarRol([ROLES.PRESIDENTE]), 
  validarCrearUsuario,
  async (req, res) => {
    try {
      const { nombreUsuario, nombre, apellido, telefono, email, rol } = req.body;

      const response = await usuarioClient.crearUsuario({
        nombreUsuario,
        nombre,
        apellido,
        telefono: telefono || '',
        email,
        rol,
        usuarioCreador: req.usuario.nombreUsuario
      });

      res.status(201).json({
        mensaje: 'Usuario creado exitosamente',
        usuario: {
          id: response.usuario.id,
          nombreUsuario: response.usuario.nombreUsuario,
          nombre: response.usuario.nombre,
          apellido: response.usuario.apellido,
          telefono: response.usuario.telefono,
          email: response.usuario.email,
          rol: response.usuario.rol,
          activo: response.usuario.activo,
          fechaHoraAlta: response.usuario.fechaHoraAlta,
          usuarioAlta: response.usuario.usuarioAlta
        }
      });
    } catch (error) {
      console.error('Error al crear usuario:', error);

      if (error.code === 6) { // ALREADY_EXISTS
        return res.status(409).json({
          error: 'Conflict',
          mensaje: 'El nombre de usuario o email ya existe',
          codigo: 'DUPLICATE_ENTRY'
        });
      }

      if (error.code === 3) { // INVALID_ARGUMENT
        return res.status(400).json({
          error: 'Bad Request',
          mensaje: 'Datos de entrada inválidos',
          codigo: 'INVALID_INPUT'
        });
      }

      if (error.code === 14) { // UNAVAILABLE
        return res.status(503).json({
          error: 'Service Unavailable',
          mensaje: 'Servicio de usuarios no disponible',
          codigo: 'USER_SERVICE_UNAVAILABLE'
        });
      }

      res.status(500).json({
        error: 'Internal Server Error',
        mensaje: 'Error interno del servidor',
        codigo: 'INTERNAL_ERROR'
      });
    }
  }
);

/**
 * @swagger
 * /api/usuarios/{id}:
 *   put:
 *     summary: Actualizar usuario (solo Presidente)
 *     tags: [Usuarios]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: integer
 *         description: ID del usuario
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               nombre:
 *                 type: string
 *               apellido:
 *                 type: string
 *               telefono:
 *                 type: string
 *               email:
 *                 type: string
 *                 format: email
 *               rol:
 *                 type: string
 *                 enum: [PRESIDENTE, VOCAL, COORDINADOR, VOLUNTARIO]
 *     responses:
 *       200:
 *         description: Usuario actualizado exitosamente
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/Usuario'
 *       400:
 *         description: Datos de entrada inválidos
 *       401:
 *         description: Token inválido
 *       403:
 *         description: Sin permisos suficientes
 *       404:
 *         description: Usuario no encontrado
 */
router.put('/:id', 
  autenticarToken, 
  autorizarRol([ROLES.PRESIDENTE]), 
  validarActualizarUsuario,
  async (req, res) => {
    try {
      const { id } = req.params;
      const { nombre, apellido, telefono, email, rol } = req.body;

      // First check if user exists
      try {
        await usuarioClient.obtenerUsuario({ id: parseInt(id) });
      } catch (error) {
        if (error.code === 5) { // NOT_FOUND
          return res.status(404).json({
            error: 'Not Found',
            mensaje: 'Usuario no encontrado',
            codigo: 'RESOURCE_NOT_FOUND'
          });
        }
        throw error;
      }

      const response = await usuarioClient.actualizarUsuario({
        id: parseInt(id),
        nombre,
        apellido,
        telefono,
        email,
        rol,
        usuarioModificacion: req.usuario.nombreUsuario
      });

      res.json({
        mensaje: 'Usuario actualizado exitosamente',
        usuario: {
          id: response.usuario.id,
          nombreUsuario: response.usuario.nombreUsuario,
          nombre: response.usuario.nombre,
          apellido: response.usuario.apellido,
          telefono: response.usuario.telefono,
          email: response.usuario.email,
          rol: response.usuario.rol,
          activo: response.usuario.activo,
          fechaHoraAlta: response.usuario.fechaHoraAlta,
          usuarioAlta: response.usuario.usuarioAlta,
          fechaHoraModificacion: response.usuario.fechaHoraModificacion,
          usuarioModificacion: response.usuario.usuarioModificacion
        }
      });
    } catch (error) {
      console.error('Error al actualizar usuario:', error);

      if (error.code === 5) { // NOT_FOUND
        return res.status(404).json({
          error: 'Not Found',
          mensaje: 'Usuario no encontrado',
          codigo: 'RESOURCE_NOT_FOUND'
        });
      }

      if (error.code === 6) { // ALREADY_EXISTS
        return res.status(409).json({
          error: 'Conflict',
          mensaje: 'El email ya está en uso por otro usuario',
          codigo: 'DUPLICATE_ENTRY'
        });
      }

      if (error.code === 3) { // INVALID_ARGUMENT
        return res.status(400).json({
          error: 'Bad Request',
          mensaje: 'Datos de entrada inválidos',
          codigo: 'INVALID_INPUT'
        });
      }

      if (error.code === 14) { // UNAVAILABLE
        return res.status(503).json({
          error: 'Service Unavailable',
          mensaje: 'Servicio de usuarios no disponible',
          codigo: 'USER_SERVICE_UNAVAILABLE'
        });
      }

      res.status(500).json({
        error: 'Internal Server Error',
        mensaje: 'Error interno del servidor',
        codigo: 'INTERNAL_ERROR'
      });
    }
  }
);

/**
 * @swagger
 * /api/usuarios/{id}:
 *   delete:
 *     summary: Eliminar usuario (solo Presidente)
 *     tags: [Usuarios]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: integer
 *         description: ID del usuario
 *     responses:
 *       200:
 *         description: Usuario eliminado exitosamente
 *       401:
 *         description: Token inválido
 *       403:
 *         description: Sin permisos suficientes
 *       404:
 *         description: Usuario no encontrado
 */
router.delete('/:id', 
  autenticarToken, 
  autorizarRol([ROLES.PRESIDENTE]), 
  validarId,
  async (req, res) => {
    try {
      const { id } = req.params;

      // First check if user exists
      try {
        await usuarioClient.obtenerUsuario({ id: parseInt(id) });
      } catch (error) {
        if (error.code === 5) { // NOT_FOUND
          return res.status(404).json({
            error: 'Not Found',
            mensaje: 'Usuario no encontrado',
            codigo: 'RESOURCE_NOT_FOUND'
          });
        }
        throw error;
      }

      const response = await usuarioClient.eliminarUsuario({
        id: parseInt(id),
        usuarioModificacion: req.usuario.nombreUsuario
      });

      res.json({
        mensaje: 'Usuario eliminado exitosamente (baja lógica)',
        codigo: 'USER_DELETED'
      });
    } catch (error) {
      console.error('Error al eliminar usuario:', error);

      if (error.code === 5) { // NOT_FOUND
        return res.status(404).json({
          error: 'Not Found',
          mensaje: 'Usuario no encontrado',
          codigo: 'RESOURCE_NOT_FOUND'
        });
      }

      if (error.code === 9) { // FAILED_PRECONDITION
        return res.status(422).json({
          error: 'Unprocessable Entity',
          mensaje: 'No se puede eliminar el usuario debido a restricciones del sistema',
          codigo: 'OPERATION_NOT_ALLOWED'
        });
      }

      if (error.code === 14) { // UNAVAILABLE
        return res.status(503).json({
          error: 'Service Unavailable',
          mensaje: 'Servicio de usuarios no disponible',
          codigo: 'USER_SERVICE_UNAVAILABLE'
        });
      }

      res.status(500).json({
        error: 'Internal Server Error',
        mensaje: 'Error interno del servidor',
        codigo: 'INTERNAL_ERROR'
      });
    }
  }
);

module.exports = router;