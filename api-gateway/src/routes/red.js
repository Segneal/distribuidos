// NGO Network routes
const express = require('express');
const router = express.Router();
const redService = require('../services/redService');
const { body, validationResult } = require('express-validator');
const { autenticarToken, autorizarRol } = require('../middleware');
const logger = require('../utils/logger');

/**
 * @swagger
 * /api/red/solicitudes-donaciones:
 *   get:
 *     summary: Listar solicitudes de donaciones externas
 *     tags: [Red de ONGs]
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       200:
 *         description: Lista de solicitudes externas
 *       401:
 *         description: Token inválido
 */
router.get('/solicitudes-donaciones', 
  autenticarToken,
  async (req, res) => {
    try {
      const solicitudes = await redService.getExternalDonationRequests();
      
      res.json({
        success: true,
        data: solicitudes,
        total: solicitudes.length
      });
      
    } catch (error) {
      logger.error('Error obteniendo solicitudes de donaciones:', error);
      res.status(500).json({
        success: false,
        mensaje: 'Error interno del servidor'
      });
    }
  }
);

/**
 * @swagger
 * /api/red/solicitudes-donaciones:
 *   post:
 *     summary: Crear solicitud de donaciones
 *     tags: [Red de ONGs]
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - donaciones
 *             properties:
 *               donaciones:
 *                 type: array
 *                 items:
 *                   type: object
 *                   properties:
 *                     categoria:
 *                       type: string
 *                       enum: [ROPA, ALIMENTOS, JUGUETES, UTILES_ESCOLARES]
 *                     descripcion:
 *                       type: string
 *     responses:
 *       201:
 *         description: Solicitud creada exitosamente
 *       400:
 *         description: Datos de entrada inválidos
 *       401:
 *         description: Token inválido
 */
router.post('/solicitudes-donaciones',
  autenticarToken,
  autorizarRol(['PRESIDENTE', 'VOCAL', 'COORDINADOR']),
  [
    body('donaciones')
      .isArray({ min: 1 })
      .withMessage('Debe incluir al menos una donación'),
    body('donaciones.*.categoria')
      .isIn(['ROPA', 'ALIMENTOS', 'JUGUETES', 'UTILES_ESCOLARES'])
      .withMessage('Categoría inválida'),
    body('donaciones.*.descripcion')
      .notEmpty()
      .withMessage('La descripción es requerida')
      .isLength({ max: 500 })
      .withMessage('La descripción no puede exceder 500 caracteres')
  ],
  async (req, res) => {
    try {
      // Validar entrada
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        return res.status(400).json({
          success: false,
          mensaje: 'Datos de entrada inválidos',
          errores: errors.array()
        });
      }

      const { donaciones } = req.body;
      const usuarioCreador = req.usuario.nombreUsuario;

      const resultado = await redService.createDonationRequest(donaciones, usuarioCreador);
      
      res.status(201).json(resultado);
      
    } catch (error) {
      logger.error('Error creando solicitud de donaciones:', error);
      res.status(500).json({
        success: false,
        mensaje: 'Error interno del servidor'
      });
    }
  }
);

/**
 * @swagger
 * /api/red/ofertas-donaciones:
 *   get:
 *     summary: Listar ofertas de donaciones externas
 *     tags: [Red de ONGs]
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       200:
 *         description: Lista de ofertas externas
 *       401:
 *         description: Token inválido
 */
router.get('/ofertas-donaciones', 
  autenticarToken,
  async (req, res) => {
    try {
      const ofertas = await redService.getExternalDonationOffers();
      
      res.json({
        success: true,
        data: ofertas,
        total: ofertas.length
      });
      
    } catch (error) {
      logger.error('Error obteniendo ofertas de donaciones:', error);
      res.status(500).json({
        success: false,
        mensaje: 'Error interno del servidor'
      });
    }
  }
);

/**
 * @swagger
 * /api/red/ofertas-donaciones:
 *   post:
 *     summary: Crear oferta de donaciones
 *     tags: [Red de ONGs]
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - donaciones
 *             properties:
 *               donaciones:
 *                 type: array
 *                 items:
 *                   type: object
 *                   properties:
 *                     categoria:
 *                       type: string
 *                       enum: [ROPA, ALIMENTOS, JUGUETES, UTILES_ESCOLARES]
 *                     descripcion:
 *                       type: string
 *                     cantidad:
 *                       type: integer
 *     responses:
 *       201:
 *         description: Oferta creada exitosamente
 *       400:
 *         description: Datos de entrada inválidos
 *       401:
 *         description: Token inválido
 */
router.post('/ofertas-donaciones',
  autenticarToken,
  autorizarRol(['PRESIDENTE', 'VOCAL', 'COORDINADOR']),
  [
    body('donaciones')
      .isArray({ min: 1 })
      .withMessage('Debe incluir al menos una donación'),
    body('donaciones.*.categoria')
      .isIn(['ROPA', 'ALIMENTOS', 'JUGUETES', 'UTILES_ESCOLARES'])
      .withMessage('Categoría inválida'),
    body('donaciones.*.descripcion')
      .notEmpty()
      .withMessage('La descripción es requerida')
      .isLength({ max: 500 })
      .withMessage('La descripción no puede exceder 500 caracteres'),
    body('donaciones.*.cantidad')
      .isInt({ min: 1 })
      .withMessage('La cantidad debe ser un número entero mayor a 0')
  ],
  async (req, res) => {
    try {
      // Validar entrada
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        return res.status(400).json({
          success: false,
          mensaje: 'Datos de entrada inválidos',
          errores: errors.array()
        });
      }

      const { donaciones } = req.body;
      const usuarioCreador = req.usuario.nombreUsuario;

      const resultado = await redService.createDonationOffer(donaciones, usuarioCreador);
      
      res.status(201).json(resultado);
      
    } catch (error) {
      logger.error('Error creando oferta de donaciones:', error);
      
      if (error.message.includes('No hay stock suficiente')) {
        return res.status(400).json({
          success: false,
          mensaje: error.message
        });
      }
      
      res.status(500).json({
        success: false,
        mensaje: 'Error interno del servidor'
      });
    }
  }
);

/**
 * @swagger
 * /api/red/transferencias-donaciones:
 *   post:
 *     summary: Transferir donaciones a otra ONG
 *     tags: [Red de ONGs]
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - idSolicitud
 *               - idOrganizacionSolicitante
 *               - donaciones
 *             properties:
 *               idSolicitud:
 *                 type: string
 *               idOrganizacionSolicitante:
 *                 type: string
 *               donaciones:
 *                 type: array
 *                 items:
 *                   type: object
 *                   properties:
 *                     categoria:
 *                       type: string
 *                       enum: [ROPA, ALIMENTOS, JUGUETES, UTILES_ESCOLARES]
 *                     descripcion:
 *                       type: string
 *                     cantidad:
 *                       type: integer
 *     responses:
 *       200:
 *         description: Transferencia realizada exitosamente
 *       400:
 *         description: Datos de entrada inválidos
 *       401:
 *         description: Token inválido
 */
router.post('/transferencias-donaciones',
  autenticarToken,
  autorizarRol(['PRESIDENTE', 'VOCAL', 'COORDINADOR']),
  [
    body('idSolicitud')
      .notEmpty()
      .withMessage('El ID de solicitud es requerido'),
    body('idOrganizacionSolicitante')
      .notEmpty()
      .withMessage('El ID de organización solicitante es requerido'),
    body('donaciones')
      .isArray({ min: 1 })
      .withMessage('Debe incluir al menos una donación'),
    body('donaciones.*.categoria')
      .isIn(['ROPA', 'ALIMENTOS', 'JUGUETES', 'UTILES_ESCOLARES'])
      .withMessage('Categoría inválida'),
    body('donaciones.*.descripcion')
      .notEmpty()
      .withMessage('La descripción es requerida'),
    body('donaciones.*.cantidad')
      .isInt({ min: 1 })
      .withMessage('La cantidad debe ser un número entero mayor a 0')
  ],
  async (req, res) => {
    try {
      // Validar entrada
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        return res.status(400).json({
          success: false,
          mensaje: 'Datos de entrada inválidos',
          errores: errors.array()
        });
      }

      const { idSolicitud, idOrganizacionSolicitante, donaciones } = req.body;
      const usuarioTransferencia = req.usuario.nombreUsuario;

      const resultado = await redService.transferDonations(
        idSolicitud,
        idOrganizacionSolicitante,
        donaciones,
        usuarioTransferencia
      );
      
      res.json(resultado);
      
    } catch (error) {
      logger.error('Error transfiriendo donaciones:', error);
      
      if (error.message.includes('Stock insuficiente')) {
        return res.status(400).json({
          success: false,
          mensaje: error.message
        });
      }
      
      res.status(500).json({
        success: false,
        mensaje: 'Error interno del servidor'
      });
    }
  }
);

/**
 * @swagger
 * /api/red/solicitudes-donaciones/{idSolicitud}:
 *   delete:
 *     summary: Dar de baja solicitud de donaciones propia
 *     tags: [Red de ONGs]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: idSolicitud
 *         required: true
 *         schema:
 *           type: string
 *         description: ID de la solicitud a dar de baja
 *     responses:
 *       200:
 *         description: Solicitud dada de baja exitosamente
 *       400:
 *         description: Solicitud no encontrada o ya inactiva
 *       401:
 *         description: Token inválido
 *       403:
 *         description: Sin permisos para esta operación
 */
router.delete('/solicitudes-donaciones/:idSolicitud',
  autenticarToken,
  autorizarRol(['PRESIDENTE', 'VOCAL', 'COORDINADOR']),
  async (req, res) => {
    try {
      const { idSolicitud } = req.params;
      const usuarioBaja = req.usuario.nombreUsuario;

      const resultado = await redService.cancelDonationRequest(idSolicitud, usuarioBaja);
      
      res.json(resultado);
      
    } catch (error) {
      logger.error('Error dando de baja solicitud:', error);
      
      if (error.message.includes('no encontrada') || error.message.includes('activa')) {
        return res.status(400).json({
          success: false,
          mensaje: error.message
        });
      }
      
      res.status(500).json({
        success: false,
        mensaje: 'Error interno del servidor'
      });
    }
  }
);

/**
 * @swagger
 * /api/red/eventos-externos:
 *   get:
 *     summary: Listar eventos externos
 *     tags: [Red de ONGs]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: query
 *         name: pagina
 *         schema:
 *           type: integer
 *           minimum: 1
 *           default: 1
 *         description: Número de página
 *       - in: query
 *         name: tamanoPagina
 *         schema:
 *           type: integer
 *           minimum: 1
 *           maximum: 100
 *           default: 10
 *         description: Tamaño de página
 *       - in: query
 *         name: soloFuturos
 *         schema:
 *           type: boolean
 *           default: true
 *         description: Mostrar solo eventos futuros
 *     responses:
 *       200:
 *         description: Lista de eventos externos
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 success:
 *                   type: boolean
 *                 data:
 *                   type: array
 *                   items:
 *                     type: object
 *                     properties:
 *                       idOrganizacion:
 *                         type: string
 *                       idEvento:
 *                         type: string
 *                       nombre:
 *                         type: string
 *                       descripcion:
 *                         type: string
 *                       fechaHora:
 *                         type: string
 *                       fechaRecepcion:
 *                         type: string
 *                 total:
 *                   type: integer
 *       401:
 *         description: Token inválido
 */
router.get('/eventos-externos', 
  autenticarToken,
  async (req, res) => {
    try {
      const pagina = parseInt(req.query.pagina) || 1;
      const tamanoPagina = Math.min(parseInt(req.query.tamanoPagina) || 10, 100);
      const soloFuturos = req.query.soloFuturos !== 'false'; // Default true
      
      const resultado = await redService.getExternalEvents(pagina, tamanoPagina, soloFuturos);
      
      res.json(resultado);
      
    } catch (error) {
      logger.error('Error obteniendo eventos externos:', error);
      res.status(500).json({
        success: false,
        mensaje: 'Error interno del servidor'
      });
    }
  }
);

/**
 * @swagger
 * /api/red/eventos-externos/adhesion:
 *   post:
 *     summary: Adherirse a evento externo (solo Voluntarios)
 *     tags: [Red de ONGs]
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - idEvento
 *               - idOrganizador
 *             properties:
 *               idEvento:
 *                 type: string
 *                 description: ID del evento externo
 *               idOrganizador:
 *                 type: string
 *                 description: ID de la organización que organiza el evento
 *     responses:
 *       200:
 *         description: Adhesión realizada exitosamente
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 success:
 *                   type: boolean
 *                 mensaje:
 *                   type: string
 *                 idEvento:
 *                   type: string
 *                 idOrganizador:
 *                   type: string
 *                 voluntario:
 *                   type: object
 *                   properties:
 *                     id:
 *                       type: integer
 *                     nombre:
 *                       type: string
 *                     apellido:
 *                       type: string
 *                     email:
 *                       type: string
 *                 fechaAdhesion:
 *                   type: string
 *       400:
 *         description: Datos de entrada inválidos o evento no disponible
 *       401:
 *         description: Token inválido
 *       403:
 *         description: Solo voluntarios pueden adherirse
 */
router.post('/eventos-externos/adhesion',
  autenticarToken,
  autorizarRol(['VOLUNTARIO']),
  [
    body('idEvento')
      .notEmpty()
      .withMessage('El ID del evento es requerido')
      .isLength({ max: 100 })
      .withMessage('El ID del evento no puede exceder 100 caracteres'),
    body('idOrganizador')
      .notEmpty()
      .withMessage('El ID del organizador es requerido')
      .isLength({ max: 100 })
      .withMessage('El ID del organizador no puede exceder 100 caracteres')
  ],
  async (req, res) => {
    try {
      // Validar entrada
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        return res.status(400).json({
          success: false,
          mensaje: 'Datos de entrada inválidos',
          errores: errors.array()
        });
      }

      const { idEvento, idOrganizador } = req.body;
      const usuarioId = req.usuario.id;

      const resultado = await redService.adhereToExternalEvent(idEvento, idOrganizador, usuarioId);
      
      res.json(resultado);
      
    } catch (error) {
      logger.error('Error adhiriéndose a evento externo:', error);
      
      if (error.message.includes('Solo los voluntarios') || 
          error.message.includes('debe estar activo')) {
        return res.status(403).json({
          success: false,
          mensaje: error.message
        });
      }
      
      if (error.message.includes('no existe') || 
          error.message.includes('no está disponible') ||
          error.message.includes('eventos pasados') ||
          error.message.includes('se encuentra adherido')) {
        return res.status(400).json({
          success: false,
          mensaje: error.message
        });
      }
      
      res.status(500).json({
        success: false,
        mensaje: 'Error interno del servidor'
      });
    }
  }
);

module.exports = router;