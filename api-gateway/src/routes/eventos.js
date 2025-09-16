// Events routes
const express = require('express');
const router = express.Router();

// Import middleware
const { autenticarToken } = require('../middleware/autenticacion');
const { autorizarRol, autorizarAutoAsignacionVoluntario } = require('../middleware/autorizacion');
const { 
  validarCrearEvento, 
  validarActualizarEvento, 
  validarParticipanteEvento,
  validarId,
  validarParametrosListado 
} = require('../middleware/validacion');

// Import constants
const { ROLES } = require('../config/constants');

// Import gRPC client
const EventoClient = require('../grpc-clients/eventoClient');
const eventoClient = new EventoClient();

/**
 * @swagger
 * /api/eventos:
 *   get:
 *     summary: Listar eventos
 *     tags: [Eventos]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: query
 *         name: page
 *         schema:
 *           type: integer
 *           minimum: 1
 *         description: Número de página
 *       - in: query
 *         name: limit
 *         schema:
 *           type: integer
 *           minimum: 1
 *           maximum: 100
 *         description: Elementos por página
 *       - in: query
 *         name: search
 *         schema:
 *           type: string
 *         description: Término de búsqueda
 *     responses:
 *       200:
 *         description: Lista de eventos
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 eventos:
 *                   type: array
 *                   items:
 *                     $ref: '#/components/schemas/Evento'
 *                 total:
 *                   type: integer
 *                 page:
 *                   type: integer
 *                 limit:
 *                   type: integer
 *                 totalPages:
 *                   type: integer
 *       401:
 *         description: Token inválido
 */
router.get('/', 
  autenticarToken,
  validarParametrosListado,
  async (req, res) => {
    try {
      const { page = 1, limit = 50, search = '' } = req.query;

      const response = await eventoClient.listarEventos({
        page: parseInt(page),
        limit: parseInt(limit),
        search: search.trim()
      });

      res.json({
        eventos: response.eventos.map(evento => ({
          id: evento.id,
          nombre: evento.nombre,
          descripcion: evento.descripcion,
          fechaHora: evento.fechaHora,
          participantesIds: evento.participantesIds || [],
          donacionesRepartidas: evento.donacionesRepartidas || []
        })),
        total: response.total,
        page: parseInt(page),
        limit: parseInt(limit),
        totalPages: Math.ceil(response.total / parseInt(limit))
      });
    } catch (error) {
      console.error('Error al listar eventos:', error);

      if (error.code === 14) { // UNAVAILABLE
        return res.status(503).json({
          error: 'Service Unavailable',
          mensaje: 'Servicio de eventos no disponible',
          codigo: 'EVENT_SERVICE_UNAVAILABLE'
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
 * /api/eventos/{id}:
 *   get:
 *     summary: Obtener evento por ID
 *     tags: [Eventos]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: integer
 *         description: ID del evento
 *     responses:
 *       200:
 *         description: Evento encontrado
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/Evento'
 *       401:
 *         description: Token inválido
 *       404:
 *         description: Evento no encontrado
 */
router.get('/:id', 
  autenticarToken,
  validarId,
  async (req, res) => {
    try {
      const { id } = req.params;

      const response = await eventoClient.obtenerEvento({ 
        id: parseInt(id) 
      });

      res.json({
        evento: {
          id: response.evento.id,
          nombre: response.evento.nombre,
          descripcion: response.evento.descripcion,
          fechaHora: response.evento.fechaHora,
          participantesIds: response.evento.participantesIds || [],
          donacionesRepartidas: response.evento.donacionesRepartidas || []
        }
      });
    } catch (error) {
      console.error('Error al obtener evento:', error);

      if (error.code === 5) { // NOT_FOUND
        return res.status(404).json({
          error: 'Not Found',
          mensaje: 'Evento no encontrado',
          codigo: 'RESOURCE_NOT_FOUND'
        });
      }

      if (error.code === 14) { // UNAVAILABLE
        return res.status(503).json({
          error: 'Service Unavailable',
          mensaje: 'Servicio de eventos no disponible',
          codigo: 'EVENT_SERVICE_UNAVAILABLE'
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
 * /api/eventos:
 *   post:
 *     summary: Crear evento (Presidente, Coordinador)
 *     tags: [Eventos]
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - nombre
 *               - descripcion
 *               - fechaHora
 *             properties:
 *               nombre:
 *                 type: string
 *                 minLength: 5
 *                 maxLength: 255
 *               descripcion:
 *                 type: string
 *                 minLength: 10
 *                 maxLength: 1000
 *               fechaHora:
 *                 type: string
 *                 format: date-time
 *                 description: Fecha y hora del evento (debe ser futura)
 *     responses:
 *       201:
 *         description: Evento creado exitosamente
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/Evento'
 *       400:
 *         description: Datos de entrada inválidos
 *       401:
 *         description: Token inválido
 *       403:
 *         description: Sin permisos suficientes
 */
router.post('/', 
  autenticarToken, 
  autorizarRol([ROLES.PRESIDENTE, ROLES.COORDINADOR]), 
  validarCrearEvento,
  async (req, res) => {
    try {
      const { nombre, descripcion, fechaHora } = req.body;

      const response = await eventoClient.crearEvento({
        nombre,
        descripcion,
        fechaHora,
        usuarioCreador: req.usuario.nombreUsuario
      });

      res.status(201).json({
        mensaje: 'Evento creado exitosamente',
        evento: {
          id: response.evento.id,
          nombre: response.evento.nombre,
          descripcion: response.evento.descripcion,
          fechaHora: response.evento.fechaHora,
          participantesIds: response.evento.participantesIds || [],
          donacionesRepartidas: response.evento.donacionesRepartidas || []
        }
      });
    } catch (error) {
      console.error('Error al crear evento:', error);

      if (error.code === 3) { // INVALID_ARGUMENT
        return res.status(400).json({
          error: 'Bad Request',
          mensaje: error.details || 'Datos de entrada inválidos',
          codigo: 'INVALID_INPUT'
        });
      }

      if (error.code === 9) { // FAILED_PRECONDITION
        return res.status(400).json({
          error: 'Bad Request',
          mensaje: 'La fecha del evento debe ser futura',
          codigo: 'INVALID_DATE'
        });
      }

      if (error.code === 14) { // UNAVAILABLE
        return res.status(503).json({
          error: 'Service Unavailable',
          mensaje: 'Servicio de eventos no disponible',
          codigo: 'EVENT_SERVICE_UNAVAILABLE'
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
 * /api/eventos/{id}:
 *   put:
 *     summary: Actualizar evento (Presidente, Coordinador)
 *     tags: [Eventos]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: integer
 *         description: ID del evento
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               nombre:
 *                 type: string
 *                 minLength: 5
 *                 maxLength: 255
 *               descripcion:
 *                 type: string
 *                 minLength: 10
 *                 maxLength: 1000
 *               fechaHora:
 *                 type: string
 *                 format: date-time
 *                 description: Fecha y hora del evento
 *     responses:
 *       200:
 *         description: Evento actualizado exitosamente
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/Evento'
 *       400:
 *         description: Datos de entrada inválidos
 *       401:
 *         description: Token inválido
 *       403:
 *         description: Sin permisos suficientes
 *       404:
 *         description: Evento no encontrado
 */
router.put('/:id', 
  autenticarToken, 
  autorizarRol([ROLES.PRESIDENTE, ROLES.COORDINADOR]), 
  validarActualizarEvento,
  async (req, res) => {
    try {
      const { id } = req.params;
      const { nombre, descripcion, fechaHora } = req.body;

      // First check if event exists
      try {
        await eventoClient.obtenerEvento({ id: parseInt(id) });
      } catch (error) {
        if (error.code === 5) { // NOT_FOUND
          return res.status(404).json({
            error: 'Not Found',
            mensaje: 'Evento no encontrado',
            codigo: 'RESOURCE_NOT_FOUND'
          });
        }
        throw error;
      }

      const response = await eventoClient.actualizarEvento({
        id: parseInt(id),
        nombre,
        descripcion,
        fechaHora,
        usuarioModificacion: req.usuario.nombreUsuario
      });

      res.json({
        mensaje: 'Evento actualizado exitosamente',
        evento: {
          id: response.evento.id,
          nombre: response.evento.nombre,
          descripcion: response.evento.descripcion,
          fechaHora: response.evento.fechaHora,
          participantesIds: response.evento.participantesIds || [],
          donacionesRepartidas: response.evento.donacionesRepartidas || []
        }
      });
    } catch (error) {
      console.error('Error al actualizar evento:', error);

      if (error.code === 5) { // NOT_FOUND
        return res.status(404).json({
          error: 'Not Found',
          mensaje: 'Evento no encontrado',
          codigo: 'RESOURCE_NOT_FOUND'
        });
      }

      if (error.code === 3) { // INVALID_ARGUMENT
        return res.status(400).json({
          error: 'Bad Request',
          mensaje: error.details || 'Datos de entrada inválidos',
          codigo: 'INVALID_INPUT'
        });
      }

      if (error.code === 9) { // FAILED_PRECONDITION
        return res.status(422).json({
          error: 'Unprocessable Entity',
          mensaje: 'No se puede actualizar el evento. Verifique las restricciones del negocio.',
          codigo: 'OPERATION_NOT_ALLOWED'
        });
      }

      if (error.code === 14) { // UNAVAILABLE
        return res.status(503).json({
          error: 'Service Unavailable',
          mensaje: 'Servicio de eventos no disponible',
          codigo: 'EVENT_SERVICE_UNAVAILABLE'
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
 * /api/eventos/{id}:
 *   delete:
 *     summary: Eliminar evento (Presidente, Coordinador)
 *     tags: [Eventos]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: integer
 *         description: ID del evento
 *     responses:
 *       200:
 *         description: Evento eliminado exitosamente
 *       401:
 *         description: Token inválido
 *       403:
 *         description: Sin permisos suficientes
 *       404:
 *         description: Evento no encontrado
 *       422:
 *         description: No se puede eliminar el evento (solo eventos futuros)
 */
router.delete('/:id', 
  autenticarToken, 
  autorizarRol([ROLES.PRESIDENTE, ROLES.COORDINADOR]), 
  validarId,
  async (req, res) => {
    try {
      const { id } = req.params;

      // First check if event exists
      try {
        await eventoClient.obtenerEvento({ id: parseInt(id) });
      } catch (error) {
        if (error.code === 5) { // NOT_FOUND
          return res.status(404).json({
            error: 'Not Found',
            mensaje: 'Evento no encontrado',
            codigo: 'RESOURCE_NOT_FOUND'
          });
        }
        throw error;
      }

      await eventoClient.eliminarEvento({
        id: parseInt(id),
        usuarioModificacion: req.usuario.nombreUsuario
      });

      res.json({
        mensaje: 'Evento eliminado exitosamente',
        codigo: 'EVENT_DELETED'
      });
    } catch (error) {
      console.error('Error al eliminar evento:', error);

      if (error.code === 5) { // NOT_FOUND
        return res.status(404).json({
          error: 'Not Found',
          mensaje: 'Evento no encontrado',
          codigo: 'RESOURCE_NOT_FOUND'
        });
      }

      if (error.code === 9) { // FAILED_PRECONDITION
        return res.status(422).json({
          error: 'Unprocessable Entity',
          mensaje: 'Solo se pueden eliminar eventos futuros',
          codigo: 'OPERATION_NOT_ALLOWED'
        });
      }

      if (error.code === 14) { // UNAVAILABLE
        return res.status(503).json({
          error: 'Service Unavailable',
          mensaje: 'Servicio de eventos no disponible',
          codigo: 'EVENT_SERVICE_UNAVAILABLE'
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
 * /api/eventos/{id}/participantes:
 *   post:
 *     summary: Agregar participante a evento
 *     tags: [Eventos]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: integer
 *         description: ID del evento
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - usuarioId
 *             properties:
 *               usuarioId:
 *                 type: integer
 *                 description: ID del usuario a agregar (Voluntarios solo pueden agregarse a sí mismos)
 *     responses:
 *       200:
 *         description: Participante agregado exitosamente
 *       400:
 *         description: Datos de entrada inválidos
 *       401:
 *         description: Token inválido
 *       403:
 *         description: Sin permisos suficientes
 *       404:
 *         description: Evento no encontrado
 *       409:
 *         description: El usuario ya es participante del evento
 */
router.post('/:id/participantes', 
  autenticarToken,
  autorizarAutoAsignacionVoluntario(),
  validarParticipanteEvento,
  async (req, res) => {
    try {
      const { id } = req.params;
      const { usuarioId } = req.body;

      const response = await eventoClient.agregarParticipante({
        eventoId: parseInt(id),
        usuarioId: parseInt(usuarioId),
        usuarioModificacion: req.usuario.nombreUsuario
      });

      res.json({
        mensaje: 'Participante agregado exitosamente al evento',
        participante: {
          eventoId: parseInt(id),
          usuarioId: parseInt(usuarioId)
        }
      });
    } catch (error) {
      console.error('Error al agregar participante:', error);

      if (error.code === 5) { // NOT_FOUND
        return res.status(404).json({
          error: 'Not Found',
          mensaje: 'Evento o usuario no encontrado',
          codigo: 'RESOURCE_NOT_FOUND'
        });
      }

      if (error.code === 6) { // ALREADY_EXISTS
        return res.status(409).json({
          error: 'Conflict',
          mensaje: 'El usuario ya es participante de este evento',
          codigo: 'DUPLICATE_ENTRY'
        });
      }

      if (error.code === 3) { // INVALID_ARGUMENT
        return res.status(400).json({
          error: 'Bad Request',
          mensaje: error.details || 'Datos de entrada inválidos',
          codigo: 'INVALID_INPUT'
        });
      }

      if (error.code === 9) { // FAILED_PRECONDITION
        return res.status(422).json({
          error: 'Unprocessable Entity',
          mensaje: 'No se puede agregar el participante. Verifique las restricciones del negocio.',
          codigo: 'OPERATION_NOT_ALLOWED'
        });
      }

      if (error.code === 14) { // UNAVAILABLE
        return res.status(503).json({
          error: 'Service Unavailable',
          mensaje: 'Servicio de eventos no disponible',
          codigo: 'EVENT_SERVICE_UNAVAILABLE'
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
 * /api/eventos/{id}/participantes/{usuarioId}:
 *   delete:
 *     summary: Quitar participante de evento
 *     tags: [Eventos]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: integer
 *         description: ID del evento
 *       - in: path
 *         name: usuarioId
 *         required: true
 *         schema:
 *           type: integer
 *         description: ID del usuario a quitar (Voluntarios solo pueden quitarse a sí mismos)
 *     responses:
 *       200:
 *         description: Participante removido exitosamente
 *       401:
 *         description: Token inválido
 *       403:
 *         description: Sin permisos suficientes
 *       404:
 *         description: Evento o usuario no encontrado
 */
router.delete('/:id/participantes/:usuarioId', 
  autenticarToken,
  autorizarAutoAsignacionVoluntario(),
  async (req, res) => {
    try {
      const { id, usuarioId } = req.params;

      const response = await eventoClient.quitarParticipante({
        eventoId: parseInt(id),
        usuarioId: parseInt(usuarioId),
        usuarioModificacion: req.usuario.nombreUsuario
      });

      res.json({
        mensaje: 'Participante removido exitosamente del evento',
        participante: {
          eventoId: parseInt(id),
          usuarioId: parseInt(usuarioId)
        }
      });
    } catch (error) {
      console.error('Error al quitar participante:', error);

      if (error.code === 5) { // NOT_FOUND
        return res.status(404).json({
          error: 'Not Found',
          mensaje: 'Evento, usuario o participación no encontrada',
          codigo: 'RESOURCE_NOT_FOUND'
        });
      }

      if (error.code === 3) { // INVALID_ARGUMENT
        return res.status(400).json({
          error: 'Bad Request',
          mensaje: error.details || 'Datos de entrada inválidos',
          codigo: 'INVALID_INPUT'
        });
      }

      if (error.code === 9) { // FAILED_PRECONDITION
        return res.status(422).json({
          error: 'Unprocessable Entity',
          mensaje: 'No se puede quitar el participante. Verifique las restricciones del negocio.',
          codigo: 'OPERATION_NOT_ALLOWED'
        });
      }

      if (error.code === 14) { // UNAVAILABLE
        return res.status(503).json({
          error: 'Service Unavailable',
          mensaje: 'Servicio de eventos no disponible',
          codigo: 'EVENT_SERVICE_UNAVAILABLE'
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