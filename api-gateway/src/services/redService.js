/**
 * Servicio para manejo de la red de ONGs
 * Gestiona solicitudes, ofertas y transferencias de donaciones
 */

const kafkaClient = require('../config/kafka');
const mysql = require('mysql2/promise');
const logger = require('../utils/logger');
const { v4: uuidv4 } = require('uuid');
const InventarioClient = require('../grpc-clients/inventarioClient');
const EventoClient = require('../grpc-clients/eventoClient');
const UsuarioClient = require('../grpc-clients/usuarioClient');

class RedService {
  constructor() {
    this.dbConfig = {
      host: process.env.DB_HOST || 'localhost',
      user: process.env.DB_USER || 'ong_user',
      password: process.env.DB_PASSWORD || 'ong_password',
      database: process.env.DB_NAME || 'ong_sistema',
      waitForConnections: true,
      connectionLimit: 10,
      queueLimit: 0
    };
    this.inventarioClient = new InventarioClient();
    this.eventoClient = new EventoClient();
    this.usuarioClient = new UsuarioClient();
    this.organizacionId = process.env.ORGANIZACION_ID || 'ong-empuje-comunitario';
  }

  async init() {
    try {
      // Intentar conectar Kafka, pero no fallar si no está disponible
      try {
        await kafkaClient.connect();
        
        // Suscribirse a topics relevantes
        await this.setupKafkaConsumers();
        
        logger.info('RedService inicializado exitosamente con Kafka');
      } catch (kafkaError) {
        logger.warn('Kafka no disponible durante inicialización, continuando sin funcionalidad de red:', kafkaError.message);
        // No lanzar error, permitir que el servicio funcione sin Kafka
      }
      
      logger.info('RedService inicializado');
    } catch (error) {
      logger.error('Error inicializando RedService:', error);
      throw error;
    }
  }

  async setupKafkaConsumers() {
    // Consumidor para solicitudes de donaciones externas
    await kafkaClient.subscribeToTopic(
      'solicitud-donaciones',
      'ong-empuje-comunitario-solicitudes-consumer',
      this.handleExternalDonationRequest.bind(this)
    );

    // Consumidor para bajas de solicitudes
    await kafkaClient.subscribeToTopic(
      'baja-solicitud-donaciones',
      'ong-empuje-comunitario-bajas-consumer',
      this.handleDonationRequestCancellation.bind(this)
    );

    // Consumidor para transferencias de donaciones dirigidas a nuestra organización
    await kafkaClient.subscribeToTopic(
      'transferencia-donaciones/ong-empuje-comunitario',
      'ong-empuje-comunitario-transferencias-consumer',
      this.handleIncomingDonationTransfer.bind(this)
    );

    // Consumidor para ofertas de donaciones externas
    await kafkaClient.subscribeToTopic(
      'oferta-donaciones',
      'ong-empuje-comunitario-ofertas-consumer',
      this.handleExternalDonationOffer.bind(this)
    );
  }

  async createDonationRequest(donaciones, usuarioCreador) {
    try {
      const connection = await mysql.createConnection(this.dbConfig);
      
      try {
        await connection.beginTransaction();
        
        // Generar ID único para la solicitud
        const idSolicitud = `SOL-${Date.now()}-${uuidv4().substring(0, 8)}`;
        
        // Guardar solicitud en base de datos local (opcional, para auditoría)
        const insertQuery = `
          INSERT INTO solicitudes_propias (id_solicitud, donaciones_json, usuario_creador, fecha_creacion)
          VALUES (?, ?, ?, NOW())
        `;
        
        await connection.execute(insertQuery, [
          idSolicitud,
          JSON.stringify(donaciones),
          usuarioCreador
        ]);
        
        // Publicar mensaje en Kafka
        const mensaje = {
          idSolicitud,
          donaciones: donaciones.map(d => ({
            categoria: d.categoria,
            descripcion: d.descripcion
          }))
        };
        
        await kafkaClient.publishMessage('solicitud-donaciones', mensaje, idSolicitud);
        
        await connection.commit();
        
        logger.info(`Solicitud de donaciones creada: ${idSolicitud}`);
        
        return {
          success: true,
          idSolicitud,
          mensaje: 'Solicitud de donaciones publicada exitosamente'
        };
        
      } catch (error) {
        await connection.rollback();
        throw error;
      } finally {
        await connection.end();
      }
      
    } catch (error) {
      logger.error('Error creando solicitud de donaciones:', error);
      throw error;
    }
  }

  async getExternalDonationRequests() {
    try {
      const connection = await mysql.createConnection(this.dbConfig);
      
      try {
        const query = `
          SELECT 
            id_organizacion,
            id_solicitud,
            categoria,
            descripcion,
            fecha_recepcion,
            activa
          FROM solicitudes_externas 
          WHERE activa = true
          ORDER BY fecha_recepcion DESC
        `;
        
        const [rows] = await connection.execute(query);
        
        // Agrupar por organización y solicitud
        const solicitudesAgrupadas = {};
        
        rows.forEach(row => {
          const key = `${row.id_organizacion}-${row.id_solicitud}`;
          
          if (!solicitudesAgrupadas[key]) {
            solicitudesAgrupadas[key] = {
              idOrganizacion: row.id_organizacion,
              idSolicitud: row.id_solicitud,
              fechaRecepcion: row.fecha_recepcion,
              donaciones: []
            };
          }
          
          solicitudesAgrupadas[key].donaciones.push({
            categoria: row.categoria,
            descripcion: row.descripcion
          });
        });
        
        return Object.values(solicitudesAgrupadas);
        
      } finally {
        await connection.end();
      }
      
    } catch (error) {
      logger.error('Error obteniendo solicitudes externas:', error);
      throw error;
    }
  }

  async handleExternalDonationRequest(message) {
    try {
      logger.info('Procesando solicitud externa de donaciones:', message);
      
      const connection = await mysql.createConnection(this.dbConfig);
      
      try {
        await connection.beginTransaction();
        
        // Verificar si ya existe la solicitud
        const checkQuery = `
          SELECT COUNT(*) as count 
          FROM solicitudes_externas 
          WHERE id_organizacion = ? AND id_solicitud = ?
        `;
        
        const [existing] = await connection.execute(checkQuery, [
          message.idOrganizacion,
          message.idSolicitud
        ]);
        
        if (existing[0].count > 0) {
          logger.debug(`Solicitud ya existe: ${message.idOrganizacion}-${message.idSolicitud}`);
          return;
        }
        
        // Insertar cada donación solicitada
        const insertQuery = `
          INSERT INTO solicitudes_externas 
          (id_organizacion, id_solicitud, categoria, descripcion, fecha_recepcion)
          VALUES (?, ?, ?, ?, NOW())
        `;
        
        for (const donacion of message.donaciones) {
          await connection.execute(insertQuery, [
            message.idOrganizacion,
            message.idSolicitud,
            donacion.categoria,
            donacion.descripcion
          ]);
        }
        
        await connection.commit();
        
        logger.info(`Solicitud externa procesada: ${message.idOrganizacion}-${message.idSolicitud}`);
        
      } catch (error) {
        await connection.rollback();
        throw error;
      } finally {
        await connection.end();
      }
      
    } catch (error) {
      logger.error('Error procesando solicitud externa:', error);
    }
  }

  async handleDonationRequestCancellation(message) {
    try {
      logger.info('Procesando baja de solicitud:', message);
      
      const connection = await mysql.createConnection(this.dbConfig);
      
      try {
        const updateQuery = `
          UPDATE solicitudes_externas 
          SET activa = false 
          WHERE id_organizacion = ? AND id_solicitud = ?
        `;
        
        const [result] = await connection.execute(updateQuery, [
          message.idOrganizacion,
          message.idSolicitud
        ]);
        
        if (result.affectedRows > 0) {
          logger.info(`Solicitud dada de baja: ${message.idOrganizacion}-${message.idSolicitud}`);
        }
        
      } finally {
        await connection.end();
      }
      
    } catch (error) {
      logger.error('Error procesando baja de solicitud:', error);
    }
  }

  async transferDonations(idSolicitud, idOrganizacionSolicitante, donaciones, usuarioTransferencia) {
    try {
      logger.info(`Iniciando transferencia de donaciones para solicitud: ${idSolicitud}`);
      
      const connection = await mysql.createConnection(this.dbConfig);
      
      try {
        await connection.beginTransaction();
        
        // Validar y descontar stock para cada donación
        const donacionesTransferidas = [];
        
        for (const donacion of donaciones) {
          // Buscar donación en inventario por categoría y descripción
          const findQuery = `
            SELECT id, cantidad 
            FROM donaciones 
            WHERE categoria = ? AND descripcion = ? AND eliminado = false AND cantidad >= ?
            ORDER BY fecha_hora_alta ASC
            LIMIT 1
          `;
          
          const [donacionesEncontradas] = await connection.execute(findQuery, [
            donacion.categoria,
            donacion.descripcion,
            donacion.cantidad
          ]);
          
          if (donacionesEncontradas.length === 0) {
            throw new Error(`Stock insuficiente para ${donacion.categoria} - ${donacion.descripcion}. Cantidad requerida: ${donacion.cantidad}`);
          }
          
          const donacionEncontrada = donacionesEncontradas[0];
          
          // Validar stock usando el servicio de inventario
          const stockValidation = await this.inventarioClient.validarStock({
            donacionId: donacionEncontrada.id,
            cantidadRequerida: donacion.cantidad
          });
          
          if (!stockValidation.exitoso || !stockValidation.tieneStockSuficiente) {
            throw new Error(`Stock insuficiente para ${donacion.categoria} - ${donacion.descripcion}. Disponible: ${stockValidation.cantidadDisponible}, Requerido: ${donacion.cantidad}`);
          }
          
          // Descontar stock
          const stockUpdate = await this.inventarioClient.actualizarStock({
            donacionId: donacionEncontrada.id,
            cantidadCambio: -donacion.cantidad,
            usuarioModificacion: usuarioTransferencia,
            motivo: `Transferencia a ${idOrganizacionSolicitante} - Solicitud: ${idSolicitud}`
          });
          
          if (!stockUpdate.exitoso) {
            throw new Error(`Error actualizando stock para ${donacion.categoria} - ${donacion.descripcion}: ${stockUpdate.mensaje}`);
          }
          
          donacionesTransferidas.push({
            categoria: donacion.categoria,
            descripcion: donacion.descripcion,
            cantidad: donacion.cantidad
          });
          
          logger.info(`Stock descontado: ${donacion.categoria} - ${donacion.descripcion}, Cantidad: ${donacion.cantidad}`);
        }
        
        // Registrar transferencia en base de datos local
        const insertTransferQuery = `
          INSERT INTO transferencias_enviadas 
          (id_solicitud, id_organizacion_solicitante, donaciones_json, usuario_transferencia, fecha_transferencia)
          VALUES (?, ?, ?, ?, NOW())
        `;
        
        await connection.execute(insertTransferQuery, [
          idSolicitud,
          idOrganizacionSolicitante,
          JSON.stringify(donacionesTransferidas),
          usuarioTransferencia
        ]);
        
        // Publicar mensaje en Kafka
        const mensaje = {
          idSolicitud,
          idOrganizacionDonante: this.organizacionId,
          donaciones: donacionesTransferidas,
          timestamp: new Date().toISOString()
        };
        
        const topicName = `transferencia-donaciones/${idOrganizacionSolicitante}`;
        await kafkaClient.publishMessage(topicName, mensaje, idSolicitud);
        
        await connection.commit();
        
        logger.info(`Transferencia completada exitosamente para solicitud: ${idSolicitud}`);
        
        return {
          success: true,
          mensaje: 'Transferencia realizada exitosamente',
          idSolicitud,
          donacionesTransferidas,
          idOrganizacionSolicitante
        };
        
      } catch (error) {
        await connection.rollback();
        throw error;
      } finally {
        await connection.end();
      }
      
    } catch (error) {
      logger.error('Error transfiriendo donaciones:', error);
      throw error;
    }
  }

  async handleIncomingDonationTransfer(message) {
    try {
      logger.info('Procesando transferencia entrante:', message);
      
      const connection = await mysql.createConnection(this.dbConfig);
      
      try {
        await connection.beginTransaction();
        
        // Verificar si ya se procesó esta transferencia
        const checkQuery = `
          SELECT COUNT(*) as count 
          FROM transferencias_recibidas 
          WHERE id_solicitud = ? AND id_organizacion_donante = ?
        `;
        
        const [existing] = await connection.execute(checkQuery, [
          message.idSolicitud,
          message.idOrganizacionDonante
        ]);
        
        if (existing[0].count > 0) {
          logger.debug(`Transferencia ya procesada: ${message.idSolicitud} de ${message.idOrganizacionDonante}`);
          return;
        }
        
        // Procesar cada donación recibida
        for (const donacion of message.donaciones) {
          // Buscar si ya existe una donación similar en inventario
          const findQuery = `
            SELECT id 
            FROM donaciones 
            WHERE categoria = ? AND descripcion = ? AND eliminado = false
            LIMIT 1
          `;
          
          const [donacionesExistentes] = await connection.execute(findQuery, [
            donacion.categoria,
            donacion.descripcion
          ]);
          
          if (donacionesExistentes.length > 0) {
            // Actualizar cantidad de donación existente
            const donacionId = donacionesExistentes[0].id;
            
            const stockUpdate = await this.inventarioClient.actualizarStock({
              donacionId: donacionId,
              cantidadCambio: donacion.cantidad,
              usuarioModificacion: 'SISTEMA_RED',
              motivo: `Transferencia recibida de ${message.idOrganizacionDonante} - Solicitud: ${message.idSolicitud}`
            });
            
            if (!stockUpdate.exitoso) {
              logger.error(`Error actualizando stock existente: ${stockUpdate.mensaje}`);
              continue;
            }
            
          } else {
            // Crear nueva donación
            const nuevaDonacion = await this.inventarioClient.crearDonacion({
              categoria: donacion.categoria,
              descripcion: donacion.descripcion,
              cantidad: donacion.cantidad,
              usuarioCreador: 'SISTEMA_RED'
            });
            
            if (!nuevaDonacion.exitoso) {
              logger.error(`Error creando nueva donación: ${nuevaDonacion.mensaje}`);
              continue;
            }
          }
          
          logger.info(`Donación recibida agregada al inventario: ${donacion.categoria} - ${donacion.descripcion}, Cantidad: ${donacion.cantidad}`);
        }
        
        // Registrar transferencia recibida
        const insertQuery = `
          INSERT INTO transferencias_recibidas 
          (id_solicitud, id_organizacion_donante, donaciones_json, fecha_recepcion)
          VALUES (?, ?, ?, NOW())
        `;
        
        await connection.execute(insertQuery, [
          message.idSolicitud,
          message.idOrganizacionDonante,
          JSON.stringify(message.donaciones)
        ]);
        
        await connection.commit();
        
        logger.info(`Transferencia entrante procesada exitosamente: ${message.idSolicitud} de ${message.idOrganizacionDonante}`);
        
      } catch (error) {
        await connection.rollback();
        throw error;
      } finally {
        await connection.end();
      }
      
    } catch (error) {
      logger.error('Error procesando transferencia entrante:', error);
    }
  }

  async createDonationOffer(donaciones, usuarioCreador) {
    try {
      const connection = await mysql.createConnection(this.dbConfig);
      
      try {
        await connection.beginTransaction();
        
        // Generar ID único para la oferta
        const idOferta = `OFE-${Date.now()}-${uuidv4().substring(0, 8)}`;
        
        // Validar que las donaciones existan en nuestro inventario
        const donacionesValidadas = [];
        
        for (const donacion of donaciones) {
          // Buscar donación en inventario
          const findQuery = `
            SELECT id, cantidad 
            FROM donaciones 
            WHERE categoria = ? AND descripcion = ? AND eliminado = false AND cantidad >= ?
            ORDER BY fecha_hora_alta ASC
            LIMIT 1
          `;
          
          const [donacionesEncontradas] = await connection.execute(findQuery, [
            donacion.categoria,
            donacion.descripcion,
            donacion.cantidad
          ]);
          
          if (donacionesEncontradas.length === 0) {
            throw new Error(`No hay stock suficiente para ofrecer ${donacion.categoria} - ${donacion.descripcion}. Cantidad requerida: ${donacion.cantidad}`);
          }
          
          donacionesValidadas.push({
            categoria: donacion.categoria,
            descripcion: donacion.descripcion,
            cantidad: donacion.cantidad
          });
        }
        
        // Guardar oferta en base de datos local (para auditoría)
        const insertQuery = `
          INSERT INTO ofertas_propias (id_oferta, donaciones_json, usuario_creador, fecha_creacion)
          VALUES (?, ?, ?, NOW())
        `;
        
        await connection.execute(insertQuery, [
          idOferta,
          JSON.stringify(donacionesValidadas),
          usuarioCreador
        ]);
        
        // Publicar mensaje en Kafka
        const mensaje = {
          idOrganizacion: this.organizacionId,
          idOferta,
          donaciones: donacionesValidadas,
          timestamp: new Date().toISOString()
        };
        
        await kafkaClient.publishMessage('oferta-donaciones', mensaje, idOferta);
        
        await connection.commit();
        
        logger.info(`Oferta de donaciones creada: ${idOferta}`);
        
        return {
          success: true,
          idOferta,
          mensaje: 'Oferta de donaciones publicada exitosamente',
          donaciones: donacionesValidadas
        };
        
      } catch (error) {
        await connection.rollback();
        throw error;
      } finally {
        await connection.end();
      }
      
    } catch (error) {
      logger.error('Error creando oferta de donaciones:', error);
      throw error;
    }
  }

  async getExternalDonationOffers() {
    try {
      const connection = await mysql.createConnection(this.dbConfig);
      
      try {
        const query = `
          SELECT 
            id_organizacion,
            id_oferta,
            categoria,
            descripcion,
            cantidad,
            fecha_recepcion
          FROM ofertas_externas 
          ORDER BY fecha_recepcion DESC
        `;
        
        const [rows] = await connection.execute(query);
        
        // Agrupar por organización y oferta
        const ofertasAgrupadas = {};
        
        rows.forEach(row => {
          const key = `${row.id_organizacion}-${row.id_oferta}`;
          
          if (!ofertasAgrupadas[key]) {
            ofertasAgrupadas[key] = {
              idOrganizacion: row.id_organizacion,
              idOferta: row.id_oferta,
              fechaRecepcion: row.fecha_recepcion,
              donaciones: []
            };
          }
          
          ofertasAgrupadas[key].donaciones.push({
            categoria: row.categoria,
            descripcion: row.descripcion,
            cantidad: row.cantidad
          });
        });
        
        return Object.values(ofertasAgrupadas);
        
      } finally {
        await connection.end();
      }
      
    } catch (error) {
      logger.error('Error obteniendo ofertas externas:', error);
      throw error;
    }
  }

  async handleExternalDonationOffer(message) {
    try {
      logger.info('Procesando oferta externa de donaciones:', message);
      
      // No procesar nuestras propias ofertas
      if (message.idOrganizacion === this.organizacionId) {
        logger.debug('Ignorando oferta propia');
        return;
      }
      
      const connection = await mysql.createConnection(this.dbConfig);
      
      try {
        await connection.beginTransaction();
        
        // Verificar si ya existe la oferta
        const checkQuery = `
          SELECT COUNT(*) as count 
          FROM ofertas_externas 
          WHERE id_organizacion = ? AND id_oferta = ?
        `;
        
        const [existing] = await connection.execute(checkQuery, [
          message.idOrganizacion,
          message.idOferta
        ]);
        
        if (existing[0].count > 0) {
          logger.debug(`Oferta ya existe: ${message.idOrganizacion}-${message.idOferta}`);
          return;
        }
        
        // Insertar cada donación ofrecida
        const insertQuery = `
          INSERT INTO ofertas_externas 
          (id_organizacion, id_oferta, categoria, descripcion, cantidad, fecha_recepcion)
          VALUES (?, ?, ?, ?, ?, NOW())
        `;
        
        for (const donacion of message.donaciones) {
          await connection.execute(insertQuery, [
            message.idOrganizacion,
            message.idOferta,
            donacion.categoria,
            donacion.descripcion,
            donacion.cantidad
          ]);
        }
        
        await connection.commit();
        
        logger.info(`Oferta externa procesada: ${message.idOrganizacion}-${message.idOferta}`);
        
      } catch (error) {
        await connection.rollback();
        throw error;
      } finally {
        await connection.end();
      }
      
    } catch (error) {
      logger.error('Error procesando oferta externa:', error);
    }
  }

  async cancelDonationRequest(idSolicitud, usuarioBaja) {
    try {
      logger.info(`Iniciando baja de solicitud: ${idSolicitud}`);
      
      const connection = await mysql.createConnection(this.dbConfig);
      
      try {
        await connection.beginTransaction();
        
        // Verificar que la solicitud existe y está activa
        const checkQuery = `
          SELECT id, activa, usuario_creador, fecha_creacion
          FROM solicitudes_propias 
          WHERE id_solicitud = ?
        `;
        
        const [solicitudes] = await connection.execute(checkQuery, [idSolicitud]);
        
        if (solicitudes.length === 0) {
          throw new Error(`Solicitud no encontrada: ${idSolicitud}`);
        }
        
        const solicitud = solicitudes[0];
        
        if (!solicitud.activa) {
          throw new Error(`La solicitud ${idSolicitud} ya no está activa`);
        }
        
        // Marcar solicitud como inactiva en nuestra base de datos
        const updateQuery = `
          UPDATE solicitudes_propias 
          SET activa = false, 
              fecha_baja = NOW(),
              usuario_baja = ?
          WHERE id_solicitud = ?
        `;
        
        const [updateResult] = await connection.execute(updateQuery, [
          usuarioBaja,
          idSolicitud
        ]);
        
        if (updateResult.affectedRows === 0) {
          throw new Error(`No se pudo actualizar la solicitud: ${idSolicitud}`);
        }
        
        // Publicar mensaje de baja en Kafka
        const mensaje = {
          idSolicitud,
          fechaBaja: new Date().toISOString(),
          usuarioBaja
        };
        
        await kafkaClient.publishMessage('baja-solicitud-donaciones', mensaje, idSolicitud);
        
        await connection.commit();
        
        logger.info(`Solicitud dada de baja exitosamente: ${idSolicitud}`);
        
        return {
          success: true,
          mensaje: 'Solicitud dada de baja exitosamente',
          idSolicitud,
          fechaBaja: mensaje.fechaBaja
        };
        
      } catch (error) {
        await connection.rollback();
        throw error;
      } finally {
        await connection.end();
      }
      
    } catch (error) {
      logger.error('Error dando de baja solicitud:', error);
      throw error;
    }
  }

  async getExternalEvents(pagina = 1, tamanoPagina = 10, soloFuturos = true) {
    try {
      logger.info('Obteniendo eventos externos de la red');
      
      const request = {
        pagina,
        tamanoPagina,
        soloFuturos
      };
      
      const response = await this.eventoClient.listarEventosExternos(request);
      
      if (!response.exitoso) {
        throw new Error(response.mensaje);
      }
      
      return {
        success: true,
        data: response.eventos,
        total: response.totalRegistros,
        mensaje: response.mensaje
      };
      
    } catch (error) {
      logger.error('Error obteniendo eventos externos:', error);
      throw error;
    }
  }

  async adhereToExternalEvent(idEvento, idOrganizador, usuarioId) {
    try {
      logger.info(`Iniciando adhesión a evento externo: ${idEvento} de organización: ${idOrganizador}`);
      
      // Obtener información completa del voluntario
      const usuarioResponse = await this.usuarioClient.obtenerUsuario({ id: usuarioId });
      
      if (!usuarioResponse.exitoso) {
        throw new Error(`Error obteniendo información del usuario: ${usuarioResponse.mensaje}`);
      }
      
      const usuario = usuarioResponse.usuario;
      
      // Validar que el usuario sea Voluntario
      if (usuario.rol !== 'VOLUNTARIO') {
        throw new Error('Solo los voluntarios pueden adherirse a eventos externos');
      }
      
      // Validar que el usuario esté activo
      if (!usuario.activo) {
        throw new Error('El usuario debe estar activo para adherirse a eventos');
      }
      
      const connection = await mysql.createConnection(this.dbConfig);
      
      try {
        await connection.beginTransaction();
        
        // Verificar que el evento externo existe y está activo
        const checkEventQuery = `
          SELECT id_organizacion, id_evento, nombre, descripcion, fecha_hora, activo
          FROM eventos_externos 
          WHERE id_organizacion = ? AND id_evento = ? AND activo = true
        `;
        
        const [eventos] = await connection.execute(checkEventQuery, [idOrganizador, idEvento]);
        
        if (eventos.length === 0) {
          throw new Error('El evento externo no existe o no está disponible para adhesión');
        }
        
        const evento = eventos[0];
        
        // Verificar que el evento sea futuro
        const fechaEvento = new Date(evento.fecha_hora);
        const ahora = new Date();
        
        if (fechaEvento <= ahora) {
          throw new Error('No se puede adherir a eventos pasados');
        }
        
        // Verificar si ya se adhirió a este evento
        const checkAdhesionQuery = `
          SELECT COUNT(*) as count 
          FROM adhesiones_eventos_externos 
          WHERE id_organizacion = ? AND id_evento = ? AND usuario_id = ?
        `;
        
        const [existing] = await connection.execute(checkAdhesionQuery, [
          idOrganizador,
          idEvento,
          usuarioId
        ]);
        
        if (existing[0].count > 0) {
          throw new Error('Ya se encuentra adherido a este evento');
        }
        
        // Registrar adhesión en base de datos local
        const insertAdhesionQuery = `
          INSERT INTO adhesiones_eventos_externos 
          (id_organizacion, id_evento, usuario_id, fecha_adhesion)
          VALUES (?, ?, ?, NOW())
        `;
        
        await connection.execute(insertAdhesionQuery, [
          idOrganizador,
          idEvento,
          usuarioId
        ]);
        
        // Preparar mensaje para Kafka con datos completos del voluntario
        const mensaje = {
          idEvento,
          idOrganizacion: this.organizacionId,
          idVoluntario: usuarioId,
          nombre: usuario.nombre,
          apellido: usuario.apellido,
          telefono: usuario.telefono,
          email: usuario.email,
          fechaAdhesion: new Date().toISOString()
        };
        
        // Publicar mensaje en topic específico del organizador
        const topicName = `adhesion-evento/${idOrganizador}`;
        await kafkaClient.publishMessage(topicName, mensaje, `${idEvento}-${usuarioId}`);
        
        await connection.commit();
        
        logger.info(`Adhesión completada exitosamente: Usuario ${usuarioId} al evento ${idEvento} de ${idOrganizador}`);
        
        return {
          success: true,
          mensaje: 'Adhesión al evento externo realizada exitosamente',
          idEvento,
          idOrganizador,
          voluntario: {
            id: usuarioId,
            nombre: usuario.nombre,
            apellido: usuario.apellido,
            email: usuario.email
          },
          fechaAdhesion: mensaje.fechaAdhesion
        };
        
      } catch (error) {
        await connection.rollback();
        throw error;
      } finally {
        await connection.end();
      }
      
    } catch (error) {
      logger.error('Error adhiriéndose a evento externo:', error);
      throw error;
    }
  }
}

module.exports = new RedService();