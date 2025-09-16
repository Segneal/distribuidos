// Middleware tests
const request = require('supertest');
const express = require('express');

// Mock the UsuarioClient before importing middleware
const mockValidarToken = jest.fn();
jest.mock('../grpc-clients/usuarioClient', () => {
  return jest.fn().mockImplementation(() => ({
    validarToken: mockValidarToken
  }));
});

const {
  autenticarToken,
  autorizarRol,
  validarLogin,
  handleGrpcError,
  handleGeneralError
} = require('../middleware');
const { ROLES } = require('../config/constants');

describe('Authentication Middleware', () => {
  let app;

  beforeEach(() => {
    app = express();
    app.use(express.json());
    
    // Clear all mocks
    jest.clearAllMocks();
  });

  describe('autenticarToken', () => {
    test('should reject request without token', async () => {
      app.get('/test', autenticarToken, (req, res) => {
        res.json({ success: true });
      });

      const response = await request(app)
        .get('/test')
        .expect(401);

      expect(response.body).toMatchObject({
        error: 'Unauthorized',
        mensaje: 'Token de acceso requerido',
        codigo: 'TOKEN_MISSING'
      });
    });

    test('should reject request with invalid token', async () => {
      mockValidarToken.mockResolvedValue({
        valido: false,
        mensaje: 'Token inválido'
      });

      app.get('/test', autenticarToken, (req, res) => {
        res.json({ success: true });
      });

      const response = await request(app)
        .get('/test')
        .set('Authorization', 'Bearer invalid-token')
        .expect(401);

      expect(response.body).toMatchObject({
        error: 'Unauthorized',
        mensaje: 'Token inválido',
        codigo: 'TOKEN_INVALID'
      });
    });

    test('should accept request with valid token', async () => {
      const mockUser = {
        id: 1,
        nombreUsuario: 'testuser',
        nombre: 'Test',
        apellido: 'User',
        email: 'test@example.com',
        rol: 'PRESIDENTE',
        activo: true
      };

      mockValidarToken.mockResolvedValue({
        valido: true,
        usuario: mockUser
      });

      app.get('/test', autenticarToken, (req, res) => {
        res.json({ 
          success: true, 
          user: req.usuario 
        });
      });

      const response = await request(app)
        .get('/test')
        .set('Authorization', 'Bearer valid-token')
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.user).toMatchObject({
        id: 1,
        nombreUsuario: 'testuser',
        rol: 'PRESIDENTE'
      });
    });

    test('should reject inactive user', async () => {
      const mockUser = {
        id: 1,
        nombreUsuario: 'testuser',
        nombre: 'Test',
        apellido: 'User',
        email: 'test@example.com',
        rol: 'PRESIDENTE',
        activo: false
      };

      mockValidarToken.mockResolvedValue({
        valido: true,
        usuario: mockUser
      });

      app.get('/test', autenticarToken, (req, res) => {
        res.json({ success: true });
      });

      const response = await request(app)
        .get('/test')
        .set('Authorization', 'Bearer valid-token')
        .expect(401);

      expect(response.body).toMatchObject({
        error: 'Unauthorized',
        mensaje: 'Usuario inactivo',
        codigo: 'USER_INACTIVE'
      });
    });
  });

  describe('autorizarRol', () => {
    beforeEach(() => {
      // Mock authentication middleware to add user to request
      app.use((req, res, next) => {
        req.usuario = {
          id: 1,
          rol: 'VOCAL'
        };
        next();
      });
    });

    test('should allow access for authorized role', async () => {
      app.get('/test', autorizarRol([ROLES.VOCAL, ROLES.PRESIDENTE]), (req, res) => {
        res.json({ success: true });
      });

      const response = await request(app)
        .get('/test')
        .expect(200);

      expect(response.body.success).toBe(true);
    });

    test('should deny access for unauthorized role', async () => {
      app.get('/test', autorizarRol([ROLES.PRESIDENTE]), (req, res) => {
        res.json({ success: true });
      });

      const response = await request(app)
        .get('/test')
        .expect(403);

      expect(response.body).toMatchObject({
        error: 'Forbidden',
        codigo: 'INSUFFICIENT_PERMISSIONS'
      });
    });

    test('should require authentication', async () => {
      // Override middleware to not add user
      app = express();
      app.get('/test', autorizarRol([ROLES.PRESIDENTE]), (req, res) => {
        res.json({ success: true });
      });

      const response = await request(app)
        .get('/test')
        .expect(401);

      expect(response.body).toMatchObject({
        error: 'Unauthorized',
        codigo: 'AUTHENTICATION_REQUIRED'
      });
    });
  });
});

describe('Validation Middleware', () => {
  let app;

  beforeEach(() => {
    app = express();
    app.use(express.json());
  });

  describe('validarLogin', () => {
    test('should accept valid login data', async () => {
      app.post('/login', validarLogin, (req, res) => {
        res.json({ success: true });
      });

      const response = await request(app)
        .post('/login')
        .send({
          identificador: 'testuser',
          clave: 'password123'
        })
        .expect(200);

      expect(response.body.success).toBe(true);
    });

    test('should reject missing identificador', async () => {
      app.post('/login', validarLogin, (req, res) => {
        res.json({ success: true });
      });

      const response = await request(app)
        .post('/login')
        .send({
          clave: 'password123'
        })
        .expect(400);

      expect(response.body).toMatchObject({
        error: 'Validation Error',
        codigo: 'VALIDATION_ERROR'
      });
    });

    test('should reject missing clave', async () => {
      app.post('/login', validarLogin, (req, res) => {
        res.json({ success: true });
      });

      const response = await request(app)
        .post('/login')
        .send({
          identificador: 'testuser'
        })
        .expect(400);

      expect(response.body).toMatchObject({
        error: 'Validation Error',
        codigo: 'VALIDATION_ERROR'
      });
    });
  });
});

describe('Error Handling Middleware', () => {
  let app;

  beforeEach(() => {
    app = express();
    app.use(express.json());
  });

  test('should handle gRPC errors', async () => {
    app.get('/test', (req, res, next) => {
      const grpcError = new Error('gRPC error');
      grpcError.code = 5; // NOT_FOUND
      grpcError.details = 'Resource not found';
      next(grpcError);
    });

    app.use(handleGrpcError);
    app.use(handleGeneralError);

    const response = await request(app)
      .get('/test')
      .expect(404);

    expect(response.body).toMatchObject({
      error: 'Not Found',
      mensaje: 'Recurso no encontrado'
    });
  });

  test('should handle general errors', async () => {
    app.get('/test', (req, res, next) => {
      const error = new Error('General error');
      next(error);
    });

    app.use(handleGrpcError);
    app.use(handleGeneralError);

    const response = await request(app)
      .get('/test')
      .expect(500);

    expect(response.body).toMatchObject({
      error: 'Internal Server Error',
      codigo: 'INTERNAL_ERROR'
    });
  });
});