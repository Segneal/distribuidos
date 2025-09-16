/**
 * Unit tests for external event adhesion functionality
 */

const request = require('supertest');
const express = require('express');

// Mock the redService
jest.mock('../services/redService', () => ({
  adhereToExternalEvent: jest.fn()
}));

// Mock the middleware
jest.mock('../middleware/autenticacion', () => ({
  autenticarToken: (req, res, next) => {
    if (!req.usuario) {
      return res.status(401).json({
        error: 'Unauthorized',
        mensaje: 'Token de acceso requerido'
      });
    }
    next();
  }
}));

jest.mock('../middleware/autorizacion', () => ({
  autorizarRol: (roles) => (req, res, next) => {
    if (!req.usuario) {
      return res.status(401).json({
        error: 'Unauthorized',
        mensaje: 'Autenticación requerida'
      });
    }
    
    const rolesArray = Array.isArray(roles) ? roles : [roles];
    if (!rolesArray.includes(req.usuario.rol)) {
      return res.status(403).json({
        error: 'Forbidden',
        mensaje: 'No tiene permisos para esta operación'
      });
    }
    next();
  }
}));

const redService = require('../services/redService');
const redRoutes = require('../routes/red');

// Mock middleware
const mockAuth = (req, res, next) => {
  req.usuario = {
    id: 1,
    nombreUsuario: 'voluntario_test',
    rol: 'VOLUNTARIO',
    nombre: 'Test',
    apellido: 'Volunteer',
    email: 'voluntario@test.com'
  };
  next();
};

const mockAuthNonVolunteer = (req, res, next) => {
  req.usuario = {
    id: 2,
    nombreUsuario: 'presidente_test',
    rol: 'PRESIDENTE',
    nombre: 'Test',
    apellido: 'President',
    email: 'presidente@test.com'
  };
  next();
};

// Create test app
const createTestApp = (authMiddleware = mockAuth) => {
  const app = express();
  app.use(express.json());
  app.use('/api/red', authMiddleware, redRoutes);
  return app;
};

describe('POST /api/red/eventos-externos/adhesion', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('should successfully adhere to external event as volunteer', async () => {
    const mockResponse = {
      success: true,
      mensaje: 'Adhesión al evento externo realizada exitosamente',
      idEvento: 'EVT-001',
      idOrganizador: 'ong-test',
      voluntario: {
        id: 1,
        nombre: 'Test',
        apellido: 'Volunteer',
        email: 'voluntario@test.com'
      },
      fechaAdhesion: '2024-01-15T10:30:00Z'
    };

    redService.adhereToExternalEvent.mockResolvedValue(mockResponse);

    const app = createTestApp();
    
    const response = await request(app)
      .post('/api/red/eventos-externos/adhesion')
      .send({
        idEvento: 'EVT-001',
        idOrganizador: 'ong-test'
      });

    expect(response.status).toBe(200);
    expect(response.body.success).toBe(true);
    expect(response.body.mensaje).toBe('Adhesión al evento externo realizada exitosamente');
    expect(redService.adhereToExternalEvent).toHaveBeenCalledWith('EVT-001', 'ong-test', 1);
  });

  test('should reject adhesion from non-volunteer', async () => {
    const app = createTestApp(mockAuthNonVolunteer);
    
    const response = await request(app)
      .post('/api/red/eventos-externos/adhesion')
      .send({
        idEvento: 'EVT-001',
        idOrganizador: 'ong-test'
      });

    expect(response.status).toBe(403);
    expect(response.body.error).toBe('Forbidden');
    expect(response.body.mensaje).toContain('permisos');
    expect(redService.adhereToExternalEvent).not.toHaveBeenCalled();
  });

  test('should validate required fields', async () => {
    const app = createTestApp();
    
    const response = await request(app)
      .post('/api/red/eventos-externos/adhesion')
      .send({
        idEvento: '', // Empty event ID
        idOrganizador: 'ong-test'
      });

    expect(response.status).toBe(400);
    expect(response.body.success).toBe(false);
    expect(response.body.mensaje).toBe('Datos de entrada inválidos');
    expect(response.body.errores).toBeDefined();
    expect(redService.adhereToExternalEvent).not.toHaveBeenCalled();
  });

  test('should validate missing fields', async () => {
    const app = createTestApp();
    
    const response = await request(app)
      .post('/api/red/eventos-externos/adhesion')
      .send({
        idEvento: 'EVT-001'
        // Missing idOrganizador
      });

    expect(response.status).toBe(400);
    expect(response.body.success).toBe(false);
    expect(response.body.mensaje).toBe('Datos de entrada inválidos');
    expect(response.body.errores).toBeDefined();
    expect(redService.adhereToExternalEvent).not.toHaveBeenCalled();
  });

  test('should handle service errors - event not found', async () => {
    redService.adhereToExternalEvent.mockRejectedValue(
      new Error('El evento externo no existe o no está disponible para adhesión')
    );

    const app = createTestApp();
    
    const response = await request(app)
      .post('/api/red/eventos-externos/adhesion')
      .send({
        idEvento: 'EVT-NONEXISTENT',
        idOrganizador: 'ong-test'
      });

    expect(response.status).toBe(400);
    expect(response.body.success).toBe(false);
    expect(response.body.mensaje).toContain('no existe');
  });

  test('should handle service errors - already adhered', async () => {
    redService.adhereToExternalEvent.mockRejectedValue(
      new Error('Ya se encuentra adherido a este evento')
    );

    const app = createTestApp();
    
    const response = await request(app)
      .post('/api/red/eventos-externos/adhesion')
      .send({
        idEvento: 'EVT-001',
        idOrganizador: 'ong-test'
      });

    expect(response.status).toBe(400);
    expect(response.body.success).toBe(false);
    expect(response.body.mensaje).toContain('adherido');
  });

  test('should handle service errors - past event', async () => {
    redService.adhereToExternalEvent.mockRejectedValue(
      new Error('No se puede adherir a eventos pasados')
    );

    const app = createTestApp();
    
    const response = await request(app)
      .post('/api/red/eventos-externos/adhesion')
      .send({
        idEvento: 'EVT-PAST',
        idOrganizador: 'ong-test'
      });

    expect(response.status).toBe(400);
    expect(response.body.success).toBe(false);
    expect(response.body.mensaje).toContain('eventos pasados');
  });

  test('should handle internal server errors', async () => {
    redService.adhereToExternalEvent.mockRejectedValue(
      new Error('Database connection failed')
    );

    const app = createTestApp();
    
    const response = await request(app)
      .post('/api/red/eventos-externos/adhesion')
      .send({
        idEvento: 'EVT-001',
        idOrganizador: 'ong-test'
      });

    expect(response.status).toBe(500);
    expect(response.body.success).toBe(false);
    expect(response.body.mensaje).toBe('Error interno del servidor');
  });

  test('should validate field length limits', async () => {
    const app = createTestApp();
    
    const longString = 'a'.repeat(101); // Exceeds 100 character limit
    
    const response = await request(app)
      .post('/api/red/eventos-externos/adhesion')
      .send({
        idEvento: longString,
        idOrganizador: 'ong-test'
      });

    expect(response.status).toBe(400);
    expect(response.body.success).toBe(false);
    expect(response.body.mensaje).toBe('Datos de entrada inválidos');
    expect(response.body.errores).toBeDefined();
    expect(redService.adhereToExternalEvent).not.toHaveBeenCalled();
  });
});