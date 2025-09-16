// Inventory routes
const express = require('express');
const router = express.Router();
const InventarioClient = require('../grpc-clients/inventarioClient');
const { autenticarToken } = require('../middleware/autenticacion');
const { autorizarRol } = require('../middleware/autorizacion');
const { 
  validarCrearDonacion, 
  validarActualizarDonacion, 
  validarId,
  validarParametrosListado 
} = require('../middleware/validacion');
const { ROLES, HTTP_STATUS, GRPC_STATUS } = require('../config/constants');

const inventarioClient = new InventarioClient();

/**
 * @swagger
 * /api/inventario:
 *   get:
 *     summary: Listar donaciones (Presidente, Vocal)
 *     tags: [Inventario]
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
 *         description: Lista de donaciones
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 donaciones:
 *                   type: array
 *                   items:
 *                     $ref: '#/components/schemas/Donacion'
 *                 total:
 *                   type: integer
 *                 pagina:
 *                   type: integer
 *                 limite:
 *                   type: integer
 *       401:
 *         description: Token inválido
 *       403:
 *         description: Sin permisos suficientes
 *       503:
 *         description: Servicio no disponible
 */
router.get('/', 
  autenticarToken,
  autorizarRol([ROLES.PRESIDENTE, ROLES.VOCAL]),
  validarParametrosListado,
  async (req, res) => {
    try {
      const { page = 1, limit = 10, search = '' } = req.query;
      
      const request = {
        pagina: parseInt(page),
        limite: parseInt(limit),
        busqueda: search
      };

      const response = await inventarioClient.listarDonaciones(request);
      
      res.status(HTTP_STATUS.OK).json({
        donaciones: response.donaciones || [],
        total: response.total || 0,
        pagina: parseInt(page),
        limite: parseInt(limit)
      });
    } catch (error) {
      console.error('Error listing donations:', error);
      
      if (error.code === GRPC_STATUS.UNAVAILABLE) {
        return res.status(HTTP_STATUS.SERVICE_UNAVAILABLE).json({
          error: 'Service Unavailable',
          mensaje: 'Servicio de inventario no disponible',
          codigo: 'INVENTORY_SERVICE_UNAVAILABLE'
        });
      }
      
      res.status(HTTP_STATUS.INTERNAL_SERVER_ERROR).json({
        error: 'Internal Server Error',
        mensaje: 'Error interno al listar donaciones',
        codigo: 'INVENTORY_LIST_ERROR'
      });
    }
  }
);

/**
 * @swagger
 * /api/inventario:
 *   post:
 *     summary: Crear donación (Presidente, Vocal)
 *     tags: [Inventario]
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - categoria
 *               - descripcion
 *               - cantidad
 *             properties:
 *               categoria:
 *                 type: string
 *                 enum: [ROPA, ALIMENTOS, JUGUETES, UTILES_ESCOLARES]
 *               descripcion:
 *                 type: string
 *               cantidad:
 *                 type: integer
 *                 minimum: 1
 *     responses:
 *       201:
 *         description: Donación creada exitosamente
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/Donacion'
 *       400:
 *         description: Datos de entrada inválidos
 *       401:
 *         description: Token inválido
 *       403:
 *         description: Sin permisos suficientes
 *       503:
 *         description: Servicio no disponible
 */
router.post('/', 
  autenticarToken,
  autorizarRol([ROLES.PRESIDENTE, ROLES.VOCAL]),
  validarCrearDonacion,
  async (req, res) => {
    try {
      const { categoria, descripcion, cantidad } = req.body;
      
      const request = {
        categoria,
        descripcion,
        cantidad: parseInt(cantidad),
        usuarioCreador: req.usuario.nombreUsuario
      };

      const response = await inventarioClient.crearDonacion(request);
      
      res.status(HTTP_STATUS.CREATED).json({
        mensaje: 'Donación creada exitosamente',
        donacion: response.donacion
      });
    } catch (error) {
      console.error('Error creating donation:', error);
      
      if (error.code === GRPC_STATUS.INVALID_ARGUMENT) {
        return res.status(HTTP_STATUS.BAD_REQUEST).json({
          error: 'Bad Request',
          mensaje: error.details || 'Datos de entrada inválidos',
          codigo: 'INVALID_DONATION_DATA'
        });
      }
      
      if (error.code === GRPC_STATUS.UNAVAILABLE) {
        return res.status(HTTP_STATUS.SERVICE_UNAVAILABLE).json({
          error: 'Service Unavailable',
          mensaje: 'Servicio de inventario no disponible',
          codigo: 'INVENTORY_SERVICE_UNAVAILABLE'
        });
      }
      
      res.status(HTTP_STATUS.INTERNAL_SERVER_ERROR).json({
        error: 'Internal Server Error',
        mensaje: 'Error interno al crear donación',
        codigo: 'DONATION_CREATE_ERROR'
      });
    }
  }
);

/**
 * @swagger
 * /api/inventario/{id}:
 *   put:
 *     summary: Actualizar donación (Presidente, Vocal)
 *     tags: [Inventario]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: integer
 *         description: ID de la donación
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               descripcion:
 *                 type: string
 *               cantidad:
 *                 type: integer
 *                 minimum: 1
 *     responses:
 *       200:
 *         description: Donación actualizada exitosamente
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/Donacion'
 *       400:
 *         description: Datos de entrada inválidos
 *       401:
 *         description: Token inválido
 *       403:
 *         description: Sin permisos suficientes
 *       404:
 *         description: Donación no encontrada
 *       503:
 *         description: Servicio no disponible
 */
router.put('/:id', 
  autenticarToken,
  autorizarRol([ROLES.PRESIDENTE, ROLES.VOCAL]),
  validarActualizarDonacion,
  async (req, res) => {
    try {
      const donacionId = parseInt(req.params.id);
      const { descripcion, cantidad } = req.body;
      
      const request = {
        id: donacionId,
        descripcion,
        cantidad: cantidad ? parseInt(cantidad) : undefined,
        usuarioModificacion: req.usuario.nombreUsuario
      };

      const response = await inventarioClient.actualizarDonacion(request);
      
      res.status(HTTP_STATUS.OK).json({
        mensaje: 'Donación actualizada exitosamente',
        donacion: response.donacion
      });
    } catch (error) {
      console.error('Error updating donation:', error);
      
      if (error.code === GRPC_STATUS.NOT_FOUND) {
        return res.status(HTTP_STATUS.NOT_FOUND).json({
          error: 'Not Found',
          mensaje: 'Donación no encontrada',
          codigo: 'DONATION_NOT_FOUND'
        });
      }
      
      if (error.code === GRPC_STATUS.INVALID_ARGUMENT) {
        return res.status(HTTP_STATUS.BAD_REQUEST).json({
          error: 'Bad Request',
          mensaje: error.details || 'Datos de entrada inválidos',
          codigo: 'INVALID_DONATION_DATA'
        });
      }
      
      if (error.code === GRPC_STATUS.UNAVAILABLE) {
        return res.status(HTTP_STATUS.SERVICE_UNAVAILABLE).json({
          error: 'Service Unavailable',
          mensaje: 'Servicio de inventario no disponible',
          codigo: 'INVENTORY_SERVICE_UNAVAILABLE'
        });
      }
      
      res.status(HTTP_STATUS.INTERNAL_SERVER_ERROR).json({
        error: 'Internal Server Error',
        mensaje: 'Error interno al actualizar donación',
        codigo: 'DONATION_UPDATE_ERROR'
      });
    }
  }
);

/**
 * @swagger
 * /api/inventario/{id}:
 *   delete:
 *     summary: Eliminar donación (Presidente, Vocal)
 *     tags: [Inventario]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: integer
 *         description: ID de la donación
 *     responses:
 *       200:
 *         description: Donación eliminada exitosamente
 *       401:
 *         description: Token inválido
 *       403:
 *         description: Sin permisos suficientes
 *       404:
 *         description: Donación no encontrada
 *       503:
 *         description: Servicio no disponible
 */
router.delete('/:id', 
  autenticarToken,
  autorizarRol([ROLES.PRESIDENTE, ROLES.VOCAL]),
  validarId,
  async (req, res) => {
    try {
      const donacionId = parseInt(req.params.id);
      
      const request = {
        id: donacionId,
        usuarioEliminacion: req.usuario.nombreUsuario
      };

      const response = await inventarioClient.eliminarDonacion(request);
      
      res.status(HTTP_STATUS.OK).json({
        mensaje: 'Donación eliminada exitosamente',
        eliminado: response.eliminado
      });
    } catch (error) {
      console.error('Error deleting donation:', error);
      
      if (error.code === GRPC_STATUS.NOT_FOUND) {
        return res.status(HTTP_STATUS.NOT_FOUND).json({
          error: 'Not Found',
          mensaje: 'Donación no encontrada',
          codigo: 'DONATION_NOT_FOUND'
        });
      }
      
      if (error.code === GRPC_STATUS.FAILED_PRECONDITION) {
        return res.status(HTTP_STATUS.BAD_REQUEST).json({
          error: 'Bad Request',
          mensaje: error.details || 'No se puede eliminar la donación',
          codigo: 'DONATION_DELETE_FAILED'
        });
      }
      
      if (error.code === GRPC_STATUS.UNAVAILABLE) {
        return res.status(HTTP_STATUS.SERVICE_UNAVAILABLE).json({
          error: 'Service Unavailable',
          mensaje: 'Servicio de inventario no disponible',
          codigo: 'INVENTORY_SERVICE_UNAVAILABLE'
        });
      }
      
      res.status(HTTP_STATUS.INTERNAL_SERVER_ERROR).json({
        error: 'Internal Server Error',
        mensaje: 'Error interno al eliminar donación',
        codigo: 'DONATION_DELETE_ERROR'
      });
    }
  }
);

/**
 * @swagger
 * /api/inventario/{id}:
 *   get:
 *     summary: Obtener donación por ID (Presidente, Vocal)
 *     tags: [Inventario]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: integer
 *         description: ID de la donación
 *     responses:
 *       200:
 *         description: Donación encontrada
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/Donacion'
 *       401:
 *         description: Token inválido
 *       403:
 *         description: Sin permisos suficientes
 *       404:
 *         description: Donación no encontrada
 *       503:
 *         description: Servicio no disponible
 */
router.get('/:id', 
  autenticarToken,
  autorizarRol([ROLES.PRESIDENTE, ROLES.VOCAL]),
  validarId,
  async (req, res) => {
    try {
      const donacionId = parseInt(req.params.id);
      
      const request = {
        id: donacionId
      };

      const response = await inventarioClient.obtenerDonacion(request);
      
      res.status(HTTP_STATUS.OK).json({
        donacion: response.donacion
      });
    } catch (error) {
      console.error('Error getting donation:', error);
      
      if (error.code === GRPC_STATUS.NOT_FOUND) {
        return res.status(HTTP_STATUS.NOT_FOUND).json({
          error: 'Not Found',
          mensaje: 'Donación no encontrada',
          codigo: 'DONATION_NOT_FOUND'
        });
      }
      
      if (error.code === GRPC_STATUS.UNAVAILABLE) {
        return res.status(HTTP_STATUS.SERVICE_UNAVAILABLE).json({
          error: 'Service Unavailable',
          mensaje: 'Servicio de inventario no disponible',
          codigo: 'INVENTORY_SERVICE_UNAVAILABLE'
        });
      }
      
      res.status(HTTP_STATUS.INTERNAL_SERVER_ERROR).json({
        error: 'Internal Server Error',
        mensaje: 'Error interno al obtener donación',
        codigo: 'DONATION_GET_ERROR'
      });
    }
  }
);

module.exports = router;