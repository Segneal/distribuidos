/**
 * Cliente Kafka para API Gateway
 * Maneja productores y consumidores para comunicación entre ONGs
 */

const { Kafka } = require('kafkajs');
const logger = require('../utils/logger');

class KafkaClient {
  constructor() {
    this.kafka = new Kafka({
      clientId: 'ong-api-gateway',
      brokers: [process.env.KAFKA_BROKERS || 'localhost:9092'],
      retry: {
        initialRetryTime: 100,
        retries: 8
      }
    });
    
    this.producer = null;
    this.consumers = new Map();
    this.organizationId = process.env.ORGANIZATION_ID || 'ong-empuje-comunitario';
    this.isConnected = false;
  }

  async connect() {
    try {
      this.producer = this.kafka.producer({
        allowAutoTopicCreation: true,
        transactionTimeout: 30000
      });
      
      await this.producer.connect();
      this.isConnected = true;
      logger.info('Kafka producer conectado exitosamente');
    } catch (error) {
      logger.error('Error conectando a Kafka:', error);
      throw error;
    }
  }

  async disconnect() {
    try {
      if (this.producer) {
        await this.producer.disconnect();
      }
      
      for (const [topic, consumer] of this.consumers) {
        await consumer.disconnect();
      }
      
      this.isConnected = false;
      logger.info('Kafka desconectado exitosamente');
    } catch (error) {
      logger.error('Error desconectando Kafka:', error);
    }
  }

  async publishMessage(topic, message, key = null) {
    if (!this.isConnected || !this.producer) {
      throw new Error('Kafka producer no está conectado');
    }

    try {
      // Enriquecer mensaje con metadatos
      const enrichedMessage = {
        ...message,
        idOrganizacion: this.organizationId,
        timestamp: new Date().toISOString()
      };

      const result = await this.producer.send({
        topic,
        messages: [{
          key: key,
          value: JSON.stringify(enrichedMessage),
          timestamp: Date.now()
        }]
      });

      logger.info(`Mensaje enviado a topic '${topic}':`, {
        partition: result[0].partition,
        offset: result[0].baseOffset
      });

      return true;
    } catch (error) {
      logger.error(`Error enviando mensaje a topic '${topic}':`, error);
      throw error;
    }
  }

  async subscribeToTopic(topic, groupId, messageHandler) {
    try {
      const consumer = this.kafka.consumer({ 
        groupId: groupId || `${this.organizationId}-${topic}-consumer`,
        sessionTimeout: 30000,
        heartbeatInterval: 3000
      });

      await consumer.connect();
      await consumer.subscribe({ topic, fromBeginning: false });

      await consumer.run({
        eachMessage: async ({ topic, partition, message }) => {
          try {
            const messageValue = JSON.parse(message.value.toString());
            
            // Filtrar mensajes propios
            if (messageValue.idOrganizacion === this.organizationId) {
              logger.debug(`Ignorando mensaje propio en topic '${topic}'`);
              return;
            }

            // Procesar mensaje
            await messageHandler(messageValue);
            
          } catch (error) {
            logger.error(`Error procesando mensaje de topic '${topic}':`, error);
          }
        }
      });

      this.consumers.set(topic, consumer);
      logger.info(`Suscrito a topic '${topic}' con groupId '${groupId}'`);
      
    } catch (error) {
      logger.error(`Error suscribiéndose a topic '${topic}':`, error);
      throw error;
    }
  }

  async healthCheck() {
    try {
      if (!this.producer) {
        return false;
      }
      
      // Verificar conexión enviando un mensaje de prueba a un topic temporal
      const admin = this.kafka.admin();
      await admin.connect();
      const metadata = await admin.fetchTopicMetadata();
      await admin.disconnect();
      
      return true;
    } catch (error) {
      logger.warn('Health check de Kafka falló:', error);
      return false;
    }
  }
}

// Crear instancia singleton
const kafkaClient = new KafkaClient();

module.exports = kafkaClient;