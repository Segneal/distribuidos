/**
 * Tests for Red de ONGs endpoints
 */

const request = require('supertest');
const app = require('../app');

describe('Red de ONGs Endpoints', () => {
  let authToken;
  let presidenteToken;

  beforeAll(async () => {
    // Login as admin to get token
    const loginResponse = await request(app)
      .post('/api/auth/login')
      .send({
        identificador: 'admin',
        clave: 'admin123'
      });
    
    authToken = loginResponse.body.token;
    presidenteToken = authToken; // Admin is Presidente
  });

  describe('POST /api/red/solicitudes-donaciones', () => {
    test('should create donation request successfully', async () => {
      const donationRequest = {
        donaciones: [
          {
            categoria: 'ALIMENTOS',
            descripcion: 'Leche en polvo para niños'
          },
          {
            categoria: 'ROPA',
            descripcion: 'Ropa de abrigo para invierno'
          }
        ]
      };

      const response = await request(app)
        .post('/api/red/solicitudes-donaciones')
        .set('Authorization', `Bearer ${presidenteToken}`)
        .send(donationRequest);

      expect(response.status).toBe(201);
      expect(response.body.success).toBe(true);
      expect(response.body.idSolicitud).toBeDefined();
      expect(response.body.mensaje).toContain('exitosamente');
    });

    test('should reject request without authentication', async () => {
      const donationRequest = {
        donaciones: [
          {
            categoria: 'ALIMENTOS',
            descripcion: 'Leche en polvo'
          }
        ]
      };

      const response = await request(app)
        .post('/api/red/solicitudes-donaciones')
        .send(donationRequest);

      expect(response.status).toBe(401);
    });

    test('should reject request with invalid categoria', async () => {
      const donationRequest = {
        donaciones: [
          {
            categoria: 'CATEGORIA_INVALIDA',
            descripcion: 'Descripción válida'
          }
        ]
      };

      const response = await request(app)
        .post('/api/red/solicitudes-donaciones')
        .set('Authorization', `Bearer ${presidenteToken}`)
        .send(donationRequest);

      expect(response.status).toBe(400);
      expect(response.body.success).toBe(false);
      expect(response.body.errores).toBeDefined();
    });

    test('should reject request with empty donaciones array', async () => {
      const donationRequest = {
        donaciones: []
      };

      const response = await request(app)
        .post('/api/red/solicitudes-donaciones')
        .set('Authorization', `Bearer ${presidenteToken}`)
        .send(donationRequest);

      expect(response.status).toBe(400);
      expect(response.body.success).toBe(false);
    });

    test('should reject request with missing descripcion', async () => {
      const donationRequest = {
        donaciones: [
          {
            categoria: 'ALIMENTOS'
            // Missing descripcion
          }
        ]
      };

      const response = await request(app)
        .post('/api/red/solicitudes-donaciones')
        .set('Authorization', `Bearer ${presidenteToken}`)
        .send(donationRequest);

      expect(response.status).toBe(400);
      expect(response.body.success).toBe(false);
    });
  });

  describe('GET /api/red/solicitudes-donaciones', () => {
    test('should get external donation requests successfully', async () => {
      const response = await request(app)
        .get('/api/red/solicitudes-donaciones')
        .set('Authorization', `Bearer ${authToken}`);

      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(response.body.data).toBeDefined();
      expect(Array.isArray(response.body.data)).toBe(true);
      expect(response.body.total).toBeDefined();
    });

    test('should reject request without authentication', async () => {
      const response = await request(app)
        .get('/api/red/solicitudes-donaciones');

      expect(response.status).toBe(401);
    });
  });
});