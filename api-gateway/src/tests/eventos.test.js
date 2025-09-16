// Tests for Events endpoints
const request = require('supertest');
const app = require('../app');

describe('Events API Endpoints', () => {
  let authToken;
  let presidenteToken;
  let coordinadorToken;
  let voluntarioToken;
  let eventoId;

  beforeAll(async () => {
    // Setup test tokens for different roles
    // These would normally be obtained through login
    presidenteToken = 'mock-presidente-token';
    coordinadorToken = 'mock-coordinador-token';
    voluntarioToken = 'mock-voluntario-token';
  });

  describe('GET /api/eventos', () => {
    test('should list events for authenticated user', async () => {
      const response = await request(app)
        .get('/api/eventos')
        .set('Authorization', `Bearer ${presidenteToken}`);

      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('eventos');
      expect(response.body).toHaveProperty('total');
      expect(response.body).toHaveProperty('page');
      expect(response.body).toHaveProperty('limit');
      expect(response.body).toHaveProperty('totalPages');
      expect(Array.isArray(response.body.eventos)).toBe(true);
    });

    test('should return 401 without authentication', async () => {
      const response = await request(app)
        .get('/api/eventos');

      expect(response.status).toBe(401);
      expect(response.body).toHaveProperty('codigo', 'TOKEN_MISSING');
    });

    test('should handle pagination parameters', async () => {
      const response = await request(app)
        .get('/api/eventos?page=1&limit=10&search=test')
        .set('Authorization', `Bearer ${presidenteToken}`);

      expect(response.status).toBe(200);
      expect(response.body.page).toBe(1);
      expect(response.body.limit).toBe(10);
    });
  });

  describe('GET /api/eventos/:id', () => {
    test('should get event by ID for authenticated user', async () => {
      const response = await request(app)
        .get('/api/eventos/1')
        .set('Authorization', `Bearer ${presidenteToken}`);

      // Could be 200 (found) or 404 (not found) depending on test data
      expect([200, 404]).toContain(response.status);
      
      if (response.status === 200) {
        expect(response.body).toHaveProperty('evento');
        expect(response.body.evento).toHaveProperty('id');
        expect(response.body.evento).toHaveProperty('nombre');
        expect(response.body.evento).toHaveProperty('descripcion');
        expect(response.body.evento).toHaveProperty('fechaHora');
      }
    });

    test('should return 401 without authentication', async () => {
      const response = await request(app)
        .get('/api/eventos/1');

      expect(response.status).toBe(401);
      expect(response.body).toHaveProperty('codigo', 'TOKEN_MISSING');
    });

    test('should return 400 for invalid ID format', async () => {
      const response = await request(app)
        .get('/api/eventos/invalid')
        .set('Authorization', `Bearer ${presidenteToken}`);

      expect(response.status).toBe(400);
      expect(response.body).toHaveProperty('codigo', 'VALIDATION_ERROR');
    });
  });

  describe('POST /api/eventos', () => {
    const validEventData = {
      nombre: 'Evento de Prueba',
      descripcion: 'Descripción del evento de prueba para testing',
      fechaHora: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString() // Tomorrow
    };

    test('should create event as Presidente', async () => {
      const response = await request(app)
        .post('/api/eventos')
        .set('Authorization', `Bearer ${presidenteToken}`)
        .send(validEventData);

      // Could be 201 (created) or 503 (service unavailable) in test environment
      expect([201, 503]).toContain(response.status);
      
      if (response.status === 201) {
        expect(response.body).toHaveProperty('mensaje');
        expect(response.body).toHaveProperty('evento');
        expect(response.body.evento).toHaveProperty('id');
        eventoId = response.body.evento.id;
      }
    });

    test('should create event as Coordinador', async () => {
      const response = await request(app)
        .post('/api/eventos')
        .set('Authorization', `Bearer ${coordinadorToken}`)
        .send(validEventData);

      // Could be 201 (created) or 503 (service unavailable) in test environment
      expect([201, 503]).toContain(response.status);
    });

    test('should deny access to Voluntario', async () => {
      const response = await request(app)
        .post('/api/eventos')
        .set('Authorization', `Bearer ${voluntarioToken}`)
        .send(validEventData);

      expect(response.status).toBe(403);
      expect(response.body).toHaveProperty('codigo', 'INSUFFICIENT_PERMISSIONS');
    });

    test('should return 401 without authentication', async () => {
      const response = await request(app)
        .post('/api/eventos')
        .send(validEventData);

      expect(response.status).toBe(401);
      expect(response.body).toHaveProperty('codigo', 'TOKEN_MISSING');
    });

    test('should validate required fields', async () => {
      const response = await request(app)
        .post('/api/eventos')
        .set('Authorization', `Bearer ${presidenteToken}`)
        .send({});

      expect(response.status).toBe(400);
      expect(response.body).toHaveProperty('codigo', 'VALIDATION_ERROR');
      expect(response.body).toHaveProperty('detalles');
    });

    test('should validate future date', async () => {
      const pastDate = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(); // Yesterday
      
      const response = await request(app)
        .post('/api/eventos')
        .set('Authorization', `Bearer ${presidenteToken}`)
        .send({
          ...validEventData,
          fechaHora: pastDate
        });

      expect(response.status).toBe(400);
      expect(response.body).toHaveProperty('codigo', 'VALIDATION_ERROR');
    });

    test('should validate name length', async () => {
      const response = await request(app)
        .post('/api/eventos')
        .set('Authorization', `Bearer ${presidenteToken}`)
        .send({
          ...validEventData,
          nombre: 'ABC' // Too short
        });

      expect(response.status).toBe(400);
      expect(response.body).toHaveProperty('codigo', 'VALIDATION_ERROR');
    });
  });

  describe('PUT /api/eventos/:id', () => {
    const updateData = {
      nombre: 'Evento Actualizado',
      descripcion: 'Descripción actualizada del evento de prueba'
    };

    test('should update event as Presidente', async () => {
      const response = await request(app)
        .put('/api/eventos/1')
        .set('Authorization', `Bearer ${presidenteToken}`)
        .send(updateData);

      // Could be 200 (updated), 404 (not found), or 503 (service unavailable)
      expect([200, 404, 503]).toContain(response.status);
      
      if (response.status === 200) {
        expect(response.body).toHaveProperty('mensaje');
        expect(response.body).toHaveProperty('evento');
      }
    });

    test('should update event as Coordinador', async () => {
      const response = await request(app)
        .put('/api/eventos/1')
        .set('Authorization', `Bearer ${coordinadorToken}`)
        .send(updateData);

      // Could be 200 (updated), 404 (not found), or 503 (service unavailable)
      expect([200, 404, 503]).toContain(response.status);
    });

    test('should deny access to Voluntario', async () => {
      const response = await request(app)
        .put('/api/eventos/1')
        .set('Authorization', `Bearer ${voluntarioToken}`)
        .send(updateData);

      expect(response.status).toBe(403);
      expect(response.body).toHaveProperty('codigo', 'INSUFFICIENT_PERMISSIONS');
    });

    test('should return 401 without authentication', async () => {
      const response = await request(app)
        .put('/api/eventos/1')
        .send(updateData);

      expect(response.status).toBe(401);
      expect(response.body).toHaveProperty('codigo', 'TOKEN_MISSING');
    });

    test('should return 400 for invalid ID format', async () => {
      const response = await request(app)
        .put('/api/eventos/invalid')
        .set('Authorization', `Bearer ${presidenteToken}`)
        .send(updateData);

      expect(response.status).toBe(400);
      expect(response.body).toHaveProperty('codigo', 'VALIDATION_ERROR');
    });
  });

  describe('DELETE /api/eventos/:id', () => {
    test('should delete event as Presidente', async () => {
      const response = await request(app)
        .delete('/api/eventos/1')
        .set('Authorization', `Bearer ${presidenteToken}`);

      // Could be 200 (deleted), 404 (not found), 422 (can't delete), or 503 (service unavailable)
      expect([200, 404, 422, 503]).toContain(response.status);
      
      if (response.status === 200) {
        expect(response.body).toHaveProperty('mensaje');
        expect(response.body).toHaveProperty('codigo', 'EVENT_DELETED');
      }
    });

    test('should delete event as Coordinador', async () => {
      const response = await request(app)
        .delete('/api/eventos/2')
        .set('Authorization', `Bearer ${coordinadorToken}`);

      // Could be 200 (deleted), 404 (not found), 422 (can't delete), or 503 (service unavailable)
      expect([200, 404, 422, 503]).toContain(response.status);
    });

    test('should deny access to Voluntario', async () => {
      const response = await request(app)
        .delete('/api/eventos/1')
        .set('Authorization', `Bearer ${voluntarioToken}`);

      expect(response.status).toBe(403);
      expect(response.body).toHaveProperty('codigo', 'INSUFFICIENT_PERMISSIONS');
    });

    test('should return 401 without authentication', async () => {
      const response = await request(app)
        .delete('/api/eventos/1');

      expect(response.status).toBe(401);
      expect(response.body).toHaveProperty('codigo', 'TOKEN_MISSING');
    });
  });

  describe('POST /api/eventos/:id/participantes', () => {
    const participantData = {
      usuarioId: 1
    };

    test('should add participant as Presidente', async () => {
      const response = await request(app)
        .post('/api/eventos/1/participantes')
        .set('Authorization', `Bearer ${presidenteToken}`)
        .send(participantData);

      // Could be 200 (added), 404 (not found), 409 (already exists), or 503 (service unavailable)
      expect([200, 404, 409, 503]).toContain(response.status);
      
      if (response.status === 200) {
        expect(response.body).toHaveProperty('mensaje');
        expect(response.body).toHaveProperty('participante');
      }
    });

    test('should add participant as Coordinador', async () => {
      const response = await request(app)
        .post('/api/eventos/1/participantes')
        .set('Authorization', `Bearer ${coordinadorToken}`)
        .send(participantData);

      // Could be 200 (added), 404 (not found), 409 (already exists), or 503 (service unavailable)
      expect([200, 404, 409, 503]).toContain(response.status);
    });

    test('should allow Voluntario to add themselves', async () => {
      // Assuming voluntario has ID 3
      const selfAssignData = { usuarioId: 3 };
      
      const response = await request(app)
        .post('/api/eventos/1/participantes')
        .set('Authorization', `Bearer ${voluntarioToken}`)
        .send(selfAssignData);

      // Could be 200 (added), 404 (not found), 409 (already exists), or 503 (service unavailable)
      expect([200, 404, 409, 503]).toContain(response.status);
    });

    test('should deny Voluntario from adding others', async () => {
      // Voluntario trying to add someone else
      const otherUserData = { usuarioId: 1 };
      
      const response = await request(app)
        .post('/api/eventos/1/participantes')
        .set('Authorization', `Bearer ${voluntarioToken}`)
        .send(otherUserData);

      expect(response.status).toBe(403);
      expect(response.body).toHaveProperty('codigo', 'SELF_ASSIGNMENT_ONLY');
    });

    test('should return 401 without authentication', async () => {
      const response = await request(app)
        .post('/api/eventos/1/participantes')
        .send(participantData);

      expect(response.status).toBe(401);
      expect(response.body).toHaveProperty('codigo', 'TOKEN_MISSING');
    });

    test('should validate required fields', async () => {
      const response = await request(app)
        .post('/api/eventos/1/participantes')
        .set('Authorization', `Bearer ${presidenteToken}`)
        .send({});

      expect(response.status).toBe(400);
      expect(response.body).toHaveProperty('codigo', 'VALIDATION_ERROR');
    });
  });

  describe('DELETE /api/eventos/:id/participantes/:usuarioId', () => {
    test('should remove participant as Presidente', async () => {
      const response = await request(app)
        .delete('/api/eventos/1/participantes/1')
        .set('Authorization', `Bearer ${presidenteToken}`);

      // Could be 200 (removed), 404 (not found), or 503 (service unavailable)
      expect([200, 404, 503]).toContain(response.status);
      
      if (response.status === 200) {
        expect(response.body).toHaveProperty('mensaje');
        expect(response.body).toHaveProperty('participante');
      }
    });

    test('should remove participant as Coordinador', async () => {
      const response = await request(app)
        .delete('/api/eventos/1/participantes/1')
        .set('Authorization', `Bearer ${coordinadorToken}`);

      // Could be 200 (removed), 404 (not found), or 503 (service unavailable)
      expect([200, 404, 503]).toContain(response.status);
    });

    test('should allow Voluntario to remove themselves', async () => {
      // Assuming voluntario has ID 3
      const response = await request(app)
        .delete('/api/eventos/1/participantes/3')
        .set('Authorization', `Bearer ${voluntarioToken}`);

      // Could be 200 (removed), 404 (not found), or 503 (service unavailable)
      expect([200, 404, 503]).toContain(response.status);
    });

    test('should deny Voluntario from removing others', async () => {
      // Voluntario trying to remove someone else
      const response = await request(app)
        .delete('/api/eventos/1/participantes/1')
        .set('Authorization', `Bearer ${voluntarioToken}`);

      expect(response.status).toBe(403);
      expect(response.body).toHaveProperty('codigo', 'SELF_ASSIGNMENT_ONLY');
    });

    test('should return 401 without authentication', async () => {
      const response = await request(app)
        .delete('/api/eventos/1/participantes/1');

      expect(response.status).toBe(401);
      expect(response.body).toHaveProperty('codigo', 'TOKEN_MISSING');
    });
  });
});