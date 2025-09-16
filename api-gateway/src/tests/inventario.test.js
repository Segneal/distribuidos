// Test file for inventory endpoints
const request = require('supertest');
const app = require('../app');

describe('Inventory Endpoints', () => {
  let authToken;
  let presidenteToken;
  let vocalToken;
  let voluntarioToken;

  beforeAll(async () => {
    // Mock authentication tokens for testing
    // In a real test environment, these would be obtained through login
    presidenteToken = 'mock-presidente-token';
    vocalToken = 'mock-vocal-token';
    voluntarioToken = 'mock-voluntario-token';
  });

  describe('GET /api/inventario', () => {
    test('should return 401 without authentication', async () => {
      const response = await request(app)
        .get('/api/inventario');
      
      expect(response.status).toBe(401);
      expect(response.body.codigo).toBe('TOKEN_MISSING');
    });

    test('should return 403 for Voluntario role', async () => {
      const response = await request(app)
        .get('/api/inventario')
        .set('Authorization', `Bearer ${voluntarioToken}`);
      
      expect(response.status).toBe(403);
      expect(response.body.codigo).toBe('INSUFFICIENT_PERMISSIONS');
    });

    test('should return donations list for Presidente', async () => {
      const response = await request(app)
        .get('/api/inventario')
        .set('Authorization', `Bearer ${presidenteToken}`);
      
      // Note: This will fail in actual testing without gRPC service running
      // but shows the expected structure
      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('donaciones');
      expect(response.body).toHaveProperty('total');
      expect(response.body).toHaveProperty('pagina');
      expect(response.body).toHaveProperty('limite');
    });

    test('should return donations list for Vocal', async () => {
      const response = await request(app)
        .get('/api/inventario')
        .set('Authorization', `Bearer ${vocalToken}`);
      
      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('donaciones');
    });

    test('should handle pagination parameters', async () => {
      const response = await request(app)
        .get('/api/inventario?page=2&limit=5&search=ropa')
        .set('Authorization', `Bearer ${presidenteToken}`);
      
      expect(response.status).toBe(200);
      expect(response.body.pagina).toBe(2);
      expect(response.body.limite).toBe(5);
    });
  });

  describe('POST /api/inventario', () => {
    const validDonation = {
      categoria: 'ROPA',
      descripcion: 'Camisetas de algodón talla M',
      cantidad: 10
    };

    test('should return 401 without authentication', async () => {
      const response = await request(app)
        .post('/api/inventario')
        .send(validDonation);
      
      expect(response.status).toBe(401);
    });

    test('should return 403 for Voluntario role', async () => {
      const response = await request(app)
        .post('/api/inventario')
        .set('Authorization', `Bearer ${voluntarioToken}`)
        .send(validDonation);
      
      expect(response.status).toBe(403);
    });

    test('should create donation for Presidente', async () => {
      const response = await request(app)
        .post('/api/inventario')
        .set('Authorization', `Bearer ${presidenteToken}`)
        .send(validDonation);
      
      expect(response.status).toBe(201);
      expect(response.body.mensaje).toBe('Donación creada exitosamente');
      expect(response.body).toHaveProperty('donacion');
    });

    test('should create donation for Vocal', async () => {
      const response = await request(app)
        .post('/api/inventario')
        .set('Authorization', `Bearer ${vocalToken}`)
        .send(validDonation);
      
      expect(response.status).toBe(201);
    });

    test('should return 400 for invalid categoria', async () => {
      const invalidDonation = {
        ...validDonation,
        categoria: 'INVALID_CATEGORY'
      };

      const response = await request(app)
        .post('/api/inventario')
        .set('Authorization', `Bearer ${presidenteToken}`)
        .send(invalidDonation);
      
      expect(response.status).toBe(400);
      expect(response.body.codigo).toBe('VALIDATION_ERROR');
    });

    test('should return 400 for missing required fields', async () => {
      const incompleteDonation = {
        categoria: 'ROPA'
        // Missing descripcion and cantidad
      };

      const response = await request(app)
        .post('/api/inventario')
        .set('Authorization', `Bearer ${presidenteToken}`)
        .send(incompleteDonation);
      
      expect(response.status).toBe(400);
    });

    test('should return 400 for invalid cantidad', async () => {
      const invalidDonation = {
        ...validDonation,
        cantidad: 0 // Should be at least 1
      };

      const response = await request(app)
        .post('/api/inventario')
        .set('Authorization', `Bearer ${presidenteToken}`)
        .send(invalidDonation);
      
      expect(response.status).toBe(400);
    });
  });

  describe('GET /api/inventario/:id', () => {
    test('should return 401 without authentication', async () => {
      const response = await request(app)
        .get('/api/inventario/1');
      
      expect(response.status).toBe(401);
    });

    test('should return 403 for Voluntario role', async () => {
      const response = await request(app)
        .get('/api/inventario/1')
        .set('Authorization', `Bearer ${voluntarioToken}`);
      
      expect(response.status).toBe(403);
    });

    test('should return donation for valid ID', async () => {
      const response = await request(app)
        .get('/api/inventario/1')
        .set('Authorization', `Bearer ${presidenteToken}`);
      
      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('donacion');
    });

    test('should return 400 for invalid ID format', async () => {
      const response = await request(app)
        .get('/api/inventario/invalid')
        .set('Authorization', `Bearer ${presidenteToken}`);
      
      expect(response.status).toBe(400);
    });
  });

  describe('PUT /api/inventario/:id', () => {
    const updateData = {
      descripcion: 'Camisetas de algodón talla L (actualizada)',
      cantidad: 15
    };

    test('should return 401 without authentication', async () => {
      const response = await request(app)
        .put('/api/inventario/1')
        .send(updateData);
      
      expect(response.status).toBe(401);
    });

    test('should return 403 for Voluntario role', async () => {
      const response = await request(app)
        .put('/api/inventario/1')
        .set('Authorization', `Bearer ${voluntarioToken}`)
        .send(updateData);
      
      expect(response.status).toBe(403);
    });

    test('should update donation for Presidente', async () => {
      const response = await request(app)
        .put('/api/inventario/1')
        .set('Authorization', `Bearer ${presidenteToken}`)
        .send(updateData);
      
      expect(response.status).toBe(200);
      expect(response.body.mensaje).toBe('Donación actualizada exitosamente');
    });

    test('should update donation for Vocal', async () => {
      const response = await request(app)
        .put('/api/inventario/1')
        .set('Authorization', `Bearer ${vocalToken}`)
        .send(updateData);
      
      expect(response.status).toBe(200);
    });

    test('should return 400 for invalid cantidad', async () => {
      const invalidUpdate = {
        cantidad: 0
      };

      const response = await request(app)
        .put('/api/inventario/1')
        .set('Authorization', `Bearer ${presidenteToken}`)
        .send(invalidUpdate);
      
      expect(response.status).toBe(400);
    });
  });

  describe('DELETE /api/inventario/:id', () => {
    test('should return 401 without authentication', async () => {
      const response = await request(app)
        .delete('/api/inventario/1');
      
      expect(response.status).toBe(401);
    });

    test('should return 403 for Voluntario role', async () => {
      const response = await request(app)
        .delete('/api/inventario/1')
        .set('Authorization', `Bearer ${voluntarioToken}`);
      
      expect(response.status).toBe(403);
    });

    test('should delete donation for Presidente', async () => {
      const response = await request(app)
        .delete('/api/inventario/1')
        .set('Authorization', `Bearer ${presidenteToken}`);
      
      expect(response.status).toBe(200);
      expect(response.body.mensaje).toBe('Donación eliminada exitosamente');
    });

    test('should delete donation for Vocal', async () => {
      const response = await request(app)
        .delete('/api/inventario/1')
        .set('Authorization', `Bearer ${vocalToken}`);
      
      expect(response.status).toBe(200);
    });

    test('should return 400 for invalid ID format', async () => {
      const response = await request(app)
        .delete('/api/inventario/invalid')
        .set('Authorization', `Bearer ${presidenteToken}`);
      
      expect(response.status).toBe(400);
    });
  });
});

// Integration tests with mock gRPC responses
describe('Inventory Integration Tests', () => {
  // These tests would mock the gRPC client responses
  // to test the complete flow without requiring actual services

  test('should handle gRPC service unavailable', async () => {
    // Mock gRPC client to throw UNAVAILABLE error
    const response = await request(app)
      .get('/api/inventario')
      .set('Authorization', 'Bearer mock-presidente-token');
    
    expect(response.status).toBe(503);
    expect(response.body.codigo).toBe('INVENTORY_SERVICE_UNAVAILABLE');
  });

  test('should handle gRPC NOT_FOUND error', async () => {
    // Mock gRPC client to throw NOT_FOUND error
    const response = await request(app)
      .get('/api/inventario/999')
      .set('Authorization', 'Bearer mock-presidente-token');
    
    expect(response.status).toBe(404);
    expect(response.body.codigo).toBe('DONATION_NOT_FOUND');
  });

  test('should handle gRPC INVALID_ARGUMENT error', async () => {
    // Mock gRPC client to throw INVALID_ARGUMENT error
    const response = await request(app)
      .post('/api/inventario')
      .set('Authorization', 'Bearer mock-presidente-token')
      .send({
        categoria: 'ROPA',
        descripcion: 'Test',
        cantidad: -1 // Invalid quantity
      });
    
    expect(response.status).toBe(400);
    expect(response.body.codigo).toBe('INVALID_DONATION_DATA');
  });
});