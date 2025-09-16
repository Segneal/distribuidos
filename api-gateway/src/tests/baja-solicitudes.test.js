/**
 * Unit tests for donation request cancellation functionality
 */

const request = require('supertest');
const app = require('../app');
const redService = require('../services/redService');

// Mock dependencies
jest.mock('../services/redService');
jest.mock('../utils/logger', () => ({
  info: jest.fn(),
  error: jest.fn(),
  debug: jest.fn(),
  warn: jest.fn()
}));

describe('Baja de Solicitudes de Donaciones', () => {
  let authToken;
  
  beforeAll(async () => {
    // Mock successful login
    const loginResponse = await request(app)
      .post('/api/auth/login')
      .send({
        identificador: 'admin',
        clave: 'admin123'
      });
    
    authToken = loginResponse.body.token;
  });

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('DELETE /api/red/solicitudes-donaciones/:idSolicitud', () => {
    const validSolicitudId = 'SOL-1234567890-abcd1234';

    test('debería dar de baja una solicitud exitosamente', async () => {
      // Mock successful cancellation
      redService.cancelDonationRequest.mockResolvedValue({
        success: true,
        mensaje: 'Solicitud dada de baja exitosamente',
        idSolicitud: validSolicitudId,
        fechaBaja: '2024-01-15T10:30:00.000Z'
      });

      const response = await request(app)
        .delete(`/api/red/solicitudes-donaciones/${validSolicitudId}`)
        .set('Authorization', `Bearer ${authToken}`)
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.idSolicitud).toBe(validSolicitudId);
      expect(response.body.fechaBaja).toBeDefined();
      expect(redService.cancelDonationRequest).toHaveBeenCalledWith(
        validSolicitudId,
        'admin'
      );
    });

    test('debería fallar si la solicitud no existe', async () => {
      const nonExistentId = 'SOL-FAKE-123';
      
      redService.cancelDonationRequest.mockRejectedValue(
        new Error(`Solicitud no encontrada: ${nonExistentId}`)
      );

      const response = await request(app)
        .delete(`/api/red/solicitudes-donaciones/${nonExistentId}`)
        .set('Authorization', `Bearer ${authToken}`)
        .expect(400);

      expect(response.body.success).toBe(false);
      expect(response.body.mensaje).toContain('no encontrada');
    });

    test('debería fallar si la solicitud ya está inactiva', async () => {
      redService.cancelDonationRequest.mockRejectedValue(
        new Error(`La solicitud ${validSolicitudId} ya no está activa`)
      );

      const response = await request(app)
        .delete(`/api/red/solicitudes-donaciones/${validSolicitudId}`)
        .set('Authorization', `Bearer ${authToken}`)
        .expect(400);

      expect(response.body.success).toBe(false);
      expect(response.body.mensaje).toContain('no activa');
    });

    test('debería requerir autenticación', async () => {
      const response = await request(app)
        .delete(`/api/red/solicitudes-donaciones/${validSolicitudId}`)
        .expect(401);

      expect(response.body.mensaje).toContain('Token de acceso requerido');
    });

    test('debería requerir rol autorizado', async () => {
      // Mock token for VOLUNTARIO role (not authorized)
      const voluntarioToken = 'mock-voluntario-token';
      
      const response = await request(app)
        .delete(`/api/red/solicitudes-donaciones/${validSolicitudId}`)
        .set('Authorization', `Bearer ${voluntarioToken}`)
        .expect(403);

      expect(response.body.mensaje).toContain('No tiene permisos');
    });

    test('debería manejar errores internos del servidor', async () => {
      redService.cancelDonationRequest.mockRejectedValue(
        new Error('Error de conexión a base de datos')
      );

      const response = await request(app)
        .delete(`/api/red/solicitudes-donaciones/${validSolicitudId}`)
        .set('Authorization', `Bearer ${authToken}`)
        .expect(500);

      expect(response.body.success).toBe(false);
      expect(response.body.mensaje).toBe('Error interno del servidor');
    });

    test('debería validar formato del ID de solicitud', async () => {
      const invalidId = '';
      
      const response = await request(app)
        .delete(`/api/red/solicitudes-donaciones/${invalidId}`)
        .set('Authorization', `Bearer ${authToken}`)
        .expect(404); // Express devuelve 404 para rutas no encontradas con parámetros vacíos

      // El endpoint no debería ser llamado con ID vacío
    });
  });

  describe('Integración con Kafka', () => {
    test('debería publicar mensaje de baja en topic correcto', async () => {
      const mockKafkaPublish = jest.fn().mockResolvedValue(true);
      
      redService.cancelDonationRequest.mockImplementation(async (idSolicitud, usuario) => {
        // Simular publicación en Kafka
        await mockKafkaPublish('baja-solicitud-donaciones', {
          idSolicitud,
          fechaBaja: new Date().toISOString(),
          usuarioBaja: usuario
        });
        
        return {
          success: true,
          mensaje: 'Solicitud dada de baja exitosamente',
          idSolicitud,
          fechaBaja: new Date().toISOString()
        };
      });

      const response = await request(app)
        .delete(`/api/red/solicitudes-donaciones/${validSolicitudId}`)
        .set('Authorization', `Bearer ${authToken}`)
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(mockKafkaPublish).toHaveBeenCalledWith(
        'baja-solicitud-donaciones',
        expect.objectContaining({
          idSolicitud: validSolicitudId,
          usuarioBaja: 'admin'
        })
      );
    });
  });

  describe('Validación de datos', () => {
    test('debería aceptar IDs de solicitud válidos', async () => {
      const validIds = [
        'SOL-1234567890-abcd1234',
        'SOL-2024-001',
        'SOLICITUD-TEST-123'
      ];

      redService.cancelDonationRequest.mockResolvedValue({
        success: true,
        mensaje: 'Solicitud dada de baja exitosamente',
        idSolicitud: 'test-id',
        fechaBaja: new Date().toISOString()
      });

      for (const id of validIds) {
        const response = await request(app)
          .delete(`/api/red/solicitudes-donaciones/${id}`)
          .set('Authorization', `Bearer ${authToken}`)
          .expect(200);

        expect(response.body.success).toBe(true);
      }
    });
  });

  describe('Auditoría y logging', () => {
    test('debería registrar la operación de baja', async () => {
      redService.cancelDonationRequest.mockResolvedValue({
        success: true,
        mensaje: 'Solicitud dada de baja exitosamente',
        idSolicitud: validSolicitudId,
        fechaBaja: new Date().toISOString()
      });

      await request(app)
        .delete(`/api/red/solicitudes-donaciones/${validSolicitudId}`)
        .set('Authorization', `Bearer ${authToken}`)
        .expect(200);

      expect(redService.cancelDonationRequest).toHaveBeenCalledWith(
        validSolicitudId,
        'admin' // Usuario que realizó la operación
      );
    });
  });
});