/**
 * Unit tests for donation transfer functionality
 */

const request = require('supertest');
const app = require('../app');

describe('Transferencias de Donaciones', () => {
  let authToken;
  let testDonacionId;

  beforeAll(async () => {
    // Login para obtener token
    const loginResponse = await request(app)
      .post('/api/auth/login')
      .send({
        identificador: 'admin@ong.com',
        clave: 'admin123'
      });

    if (loginResponse.body.success) {
      authToken = loginResponse.body.token;
    }

    // Crear donación de prueba
    const donacionResponse = await request(app)
      .post('/api/inventario')
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        categoria: 'ALIMENTOS',
        descripcion: 'Puré de tomates test',
        cantidad: 20
      });

    if (donacionResponse.body.success) {
      testDonacionId = donacionResponse.body.donacion.id;
    }
  });

  describe('POST /api/red/transferencias-donaciones', () => {
    test('debe transferir donaciones exitosamente', async () => {
      const transferData = {
        idSolicitud: 'SOL-TEST-001',
        idOrganizacionSolicitante: 'ong-test-solicitante',
        donaciones: [
          {
            categoria: 'ALIMENTOS',
            descripcion: 'Puré de tomates test',
            cantidad: 5
          }
        ]
      };

      const response = await request(app)
        .post('/api/red/transferencias-donaciones')
        .set('Authorization', `Bearer ${authToken}`)
        .send(transferData);

      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(response.body.idSolicitud).toBe('SOL-TEST-001');
      expect(response.body.donacionesTransferidas).toHaveLength(1);
    });

    test('debe rechazar transferencia sin autenticación', async () => {
      const transferData = {
        idSolicitud: 'SOL-TEST-002',
        idOrganizacionSolicitante: 'ong-test-solicitante',
        donaciones: [
          {
            categoria: 'ALIMENTOS',
            descripcion: 'Puré de tomates test',
            cantidad: 5
          }
        ]
      };

      const response = await request(app)
        .post('/api/red/transferencias-donaciones')
        .send(transferData);

      expect(response.status).toBe(401);
      expect(response.body.success).toBe(false);
    });

    test('debe validar datos de entrada requeridos', async () => {
      const transferData = {
        // Falta idSolicitud
        idOrganizacionSolicitante: 'ong-test-solicitante',
        donaciones: []
      };

      const response = await request(app)
        .post('/api/red/transferencias-donaciones')
        .set('Authorization', `Bearer ${authToken}`)
        .send(transferData);

      expect(response.status).toBe(400);
      expect(response.body.success).toBe(false);
      expect(response.body.errores).toBeDefined();
    });

    test('debe rechazar transferencia con stock insuficiente', async () => {
      const transferData = {
        idSolicitud: 'SOL-TEST-003',
        idOrganizacionSolicitante: 'ong-test-solicitante',
        donaciones: [
          {
            categoria: 'ALIMENTOS',
            descripcion: 'Puré de tomates test',
            cantidad: 1000 // Cantidad mayor al stock disponible
          }
        ]
      };

      const response = await request(app)
        .post('/api/red/transferencias-donaciones')
        .set('Authorization', `Bearer ${authToken}`)
        .send(transferData);

      expect(response.status).toBe(400);
      expect(response.body.success).toBe(false);
      expect(response.body.mensaje).toContain('Stock insuficiente');
    });

    test('debe validar categorías de donaciones', async () => {
      const transferData = {
        idSolicitud: 'SOL-TEST-004',
        idOrganizacionSolicitante: 'ong-test-solicitante',
        donaciones: [
          {
            categoria: 'CATEGORIA_INVALIDA',
            descripcion: 'Descripción test',
            cantidad: 1
          }
        ]
      };

      const response = await request(app)
        .post('/api/red/transferencias-donaciones')
        .set('Authorization', `Bearer ${authToken}`)
        .send(transferData);

      expect(response.status).toBe(400);
      expect(response.body.success).toBe(false);
      expect(response.body.errores).toBeDefined();
    });

    test('debe validar cantidades positivas', async () => {
      const transferData = {
        idSolicitud: 'SOL-TEST-005',
        idOrganizacionSolicitante: 'ong-test-solicitante',
        donaciones: [
          {
            categoria: 'ALIMENTOS',
            descripcion: 'Descripción test',
            cantidad: 0 // Cantidad inválida
          }
        ]
      };

      const response = await request(app)
        .post('/api/red/transferencias-donaciones')
        .set('Authorization', `Bearer ${authToken}`)
        .send(transferData);

      expect(response.status).toBe(400);
      expect(response.body.success).toBe(false);
      expect(response.body.errores).toBeDefined();
    });

    test('debe rechazar acceso a usuarios no autorizados', async () => {
      // Login como voluntario
      const voluntarioLogin = await request(app)
        .post('/api/auth/login')
        .send({
          identificador: 'voluntario@ong.com',
          clave: 'voluntario123'
        });

      let voluntarioToken = null;
      if (voluntarioLogin.body.success) {
        voluntarioToken = voluntarioLogin.body.token;
      }

      if (voluntarioToken) {
        const transferData = {
          idSolicitud: 'SOL-TEST-006',
          idOrganizacionSolicitante: 'ong-test-solicitante',
          donaciones: [
            {
              categoria: 'ALIMENTOS',
              descripcion: 'Descripción test',
              cantidad: 1
            }
          ]
        };

        const response = await request(app)
          .post('/api/red/transferencias-donaciones')
          .set('Authorization', `Bearer ${voluntarioToken}`)
          .send(transferData);

        expect(response.status).toBe(403);
        expect(response.body.success).toBe(false);
      }
    });
  });
});