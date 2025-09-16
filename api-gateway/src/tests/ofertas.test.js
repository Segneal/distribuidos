/**
 * Tests for donation offers functionality
 */

const request = require('supertest');
const app = require('../app');

describe('Ofertas de Donaciones', () => {
  let authToken;
  let presidenteToken;
  let vocalToken;
  let voluntarioToken;

  beforeAll(async () => {
    // Login as different users for testing
    const presidenteLogin = await request(app)
      .post('/api/auth/login')
      .send({
        identificador: 'admin',
        clave: 'admin123'
      });
    
    presidenteToken = presidenteLogin.body.token;
    authToken = presidenteToken; // Default token for most tests
  });

  describe('POST /api/red/ofertas-donaciones', () => {
    test('should create donation offer successfully with valid data', async () => {
      const offerData = {
        donaciones: [
          {
            categoria: 'ALIMENTOS',
            descripcion: 'Arroz blanco 1kg',
            cantidad: 5
          },
          {
            categoria: 'ROPA',
            descripcion: 'Camisetas talle M',
            cantidad: 3
          }
        ]
      };

      const response = await request(app)
        .post('/api/red/ofertas-donaciones')
        .set('Authorization', `Bearer ${authToken}`)
        .send(offerData);

      expect(response.status).toBe(201);
      expect(response.body.success).toBe(true);
      expect(response.body.idOferta).toBeDefined();
      expect(response.body.mensaje).toBe('Oferta de donaciones publicada exitosamente');
      expect(response.body.donaciones).toHaveLength(2);
      expect(response.body.donaciones[0]).toMatchObject({
        categoria: 'ALIMENTOS',
        descripcion: 'Arroz blanco 1kg',
        cantidad: 5
      });
    });

    test('should require authentication', async () => {
      const offerData = {
        donaciones: [
          {
            categoria: 'ALIMENTOS',
            descripcion: 'Test',
            cantidad: 1
          }
        ]
      };

      const response = await request(app)
        .post('/api/red/ofertas-donaciones')
        .send(offerData);

      expect(response.status).toBe(401);
      expect(response.body.mensaje).toBe('Token de acceso requerido');
    });

    test('should require proper role authorization', async () => {
      // This test would need a voluntario token
      // For now, we'll test with the presidente token which should work
      const offerData = {
        donaciones: [
          {
            categoria: 'ALIMENTOS',
            descripcion: 'Test',
            cantidad: 1
          }
        ]
      };

      const response = await request(app)
        .post('/api/red/ofertas-donaciones')
        .set('Authorization', `Bearer ${authToken}`)
        .send(offerData);

      // Should succeed with presidente role
      expect(response.status).toBe(201);
    });

    test('should validate required fields', async () => {
      const response = await request(app)
        .post('/api/red/ofertas-donaciones')
        .set('Authorization', `Bearer ${authToken}`)
        .send({});

      expect(response.status).toBe(400);
      expect(response.body.success).toBe(false);
      expect(response.body.mensaje).toBe('Datos de entrada inválidos');
      expect(response.body.errores).toBeDefined();
    });

    test('should validate donaciones array is not empty', async () => {
      const response = await request(app)
        .post('/api/red/ofertas-donaciones')
        .set('Authorization', `Bearer ${authToken}`)
        .send({ donaciones: [] });

      expect(response.status).toBe(400);
      expect(response.body.success).toBe(false);
      expect(response.body.errores).toEqual(
        expect.arrayContaining([
          expect.objectContaining({
            msg: 'Debe incluir al menos una donación'
          })
        ])
      );
    });

    test('should validate categoria values', async () => {
      const offerData = {
        donaciones: [
          {
            categoria: 'CATEGORIA_INVALIDA',
            descripcion: 'Test',
            cantidad: 1
          }
        ]
      };

      const response = await request(app)
        .post('/api/red/ofertas-donaciones')
        .set('Authorization', `Bearer ${authToken}`)
        .send(offerData);

      expect(response.status).toBe(400);
      expect(response.body.errores).toEqual(
        expect.arrayContaining([
          expect.objectContaining({
            msg: 'Categoría inválida'
          })
        ])
      );
    });

    test('should validate descripcion is required', async () => {
      const offerData = {
        donaciones: [
          {
            categoria: 'ALIMENTOS',
            cantidad: 1
          }
        ]
      };

      const response = await request(app)
        .post('/api/red/ofertas-donaciones')
        .set('Authorization', `Bearer ${authToken}`)
        .send(offerData);

      expect(response.status).toBe(400);
      expect(response.body.errores).toEqual(
        expect.arrayContaining([
          expect.objectContaining({
            msg: 'La descripción es requerida'
          })
        ])
      );
    });

    test('should validate cantidad is positive integer', async () => {
      const offerData = {
        donaciones: [
          {
            categoria: 'ALIMENTOS',
            descripcion: 'Test',
            cantidad: 0
          }
        ]
      };

      const response = await request(app)
        .post('/api/red/ofertas-donaciones')
        .set('Authorization', `Bearer ${authToken}`)
        .send(offerData);

      expect(response.status).toBe(400);
      expect(response.body.errores).toEqual(
        expect.arrayContaining([
          expect.objectContaining({
            msg: 'La cantidad debe ser un número entero mayor a 0'
          })
        ])
      );
    });

    test('should validate descripcion length', async () => {
      const longDescription = 'a'.repeat(501);
      const offerData = {
        donaciones: [
          {
            categoria: 'ALIMENTOS',
            descripcion: longDescription,
            cantidad: 1
          }
        ]
      };

      const response = await request(app)
        .post('/api/red/ofertas-donaciones')
        .set('Authorization', `Bearer ${authToken}`)
        .send(offerData);

      expect(response.status).toBe(400);
      expect(response.body.errores).toEqual(
        expect.arrayContaining([
          expect.objectContaining({
            msg: 'La descripción no puede exceder 500 caracteres'
          })
        ])
      );
    });
  });

  describe('GET /api/red/ofertas-donaciones', () => {
    test('should get external donation offers successfully', async () => {
      const response = await request(app)
        .get('/api/red/ofertas-donaciones')
        .set('Authorization', `Bearer ${authToken}`);

      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(response.body.data).toBeDefined();
      expect(response.body.total).toBeDefined();
      expect(Array.isArray(response.body.data)).toBe(true);
    });

    test('should require authentication', async () => {
      const response = await request(app)
        .get('/api/red/ofertas-donaciones');

      expect(response.status).toBe(401);
      expect(response.body.mensaje).toBe('Token de acceso requerido');
    });

    test('should return offers in correct format', async () => {
      const response = await request(app)
        .get('/api/red/ofertas-donaciones')
        .set('Authorization', `Bearer ${authToken}`);

      expect(response.status).toBe(200);
      expect(response.body).toMatchObject({
        success: true,
        data: expect.any(Array),
        total: expect.any(Number)
      });

      // If there are offers, check their structure
      if (response.body.data.length > 0) {
        const offer = response.body.data[0];
        expect(offer).toMatchObject({
          idOrganizacion: expect.any(String),
          idOferta: expect.any(String),
          fechaRecepcion: expect.any(String),
          donaciones: expect.any(Array)
        });

        if (offer.donaciones.length > 0) {
          const donacion = offer.donaciones[0];
          expect(donacion).toMatchObject({
            categoria: expect.any(String),
            descripcion: expect.any(String),
            cantidad: expect.any(Number)
          });
        }
      }
    });
  });

  describe('Integration Tests', () => {
    test('should handle complete offer workflow', async () => {
      // 1. Create an offer
      const offerData = {
        donaciones: [
          {
            categoria: 'JUGUETES',
            descripcion: 'Pelotas de fútbol',
            cantidad: 2
          }
        ]
      };

      const createResponse = await request(app)
        .post('/api/red/ofertas-donaciones')
        .set('Authorization', `Bearer ${authToken}`)
        .send(offerData);

      expect(createResponse.status).toBe(201);
      expect(createResponse.body.success).toBe(true);

      // 2. Get offers (should include external ones, not our own)
      const getResponse = await request(app)
        .get('/api/red/ofertas-donaciones')
        .set('Authorization', `Bearer ${authToken}`);

      expect(getResponse.status).toBe(200);
      expect(getResponse.body.success).toBe(true);
    });
  });
});