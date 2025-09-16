// User endpoints tests
const request = require('supertest');
const express = require('express');

// Mock the UsuarioClient before importing routes
const mockCrearUsuario = jest.fn();
const mockObtenerUsuario = jest.fn();
const mockListarUsuarios = jest.fn();
const mockActualizarUsuario = jest.fn();
const mockEliminarUsuario = jest.fn();
const mockAutenticarUsuario = jest.fn();
const mockValidarToken = jest.fn();

jest.mock('../grpc-clients/usuarioClient', () => {
  return jest.fn().mockImplementation(() => ({
    crearUsuario: mockCrearUsuario,
    obtenerUsuario: mockObtenerUsuario,
    listarUsuarios: mockListarUsuarios,
    actualizarUsuario: mockActualizarUsuario,
    eliminarUsuario: mockEliminarUsuario,
    autenticarUsuario: mockAutenticarUsuario,
    validarToken: mockValidarToken
  }));
});

// Mock middleware before importing routes
jest.mock('../middleware/autenticacion', () => ({
  autenticarToken: (req, res, next) => {
    if (req.headers.authorization) {
      req.usuario = {
        id: 1,
        nombreUsuario: 'admin',
        nombre: 'Admin',
        apellido: 'User',
        email: 'admin@ong.com',
        rol: 'PRESIDENTE',
        activo: true
      };
      next();
    } else {
      res.status(401).json({
        error: 'Unauthorized',
        mensaje: 'Token de acceso requerido',
        codigo: 'TOKEN_MISSING'
      });
    }
  }
}));

jest.mock('../middleware/autorizacion', () => ({
  autorizarRol: (roles) => (req, res, next) => {
    if (!req.usuario) {
      return res.status(401).json({
        error: 'Unauthorized',
        codigo: 'AUTHENTICATION_REQUIRED'
      });
    }
    if (roles.includes(req.usuario.rol)) {
      next();
    } else {
      res.status(403).json({
        error: 'Forbidden',
        codigo: 'INSUFFICIENT_PERMISSIONS'
      });
    }
  }
}));

const usuariosRoutes = require('../routes/usuarios');
const authRoutes = require('../routes/auth');
const { ROLES } = require('../config/constants');

describe('User Endpoints', () => {
  let app;

  beforeEach(() => {
    app = express();
    app.use(express.json());
    
    app.use('/api/auth', authRoutes);
    app.use('/api/usuarios', usuariosRoutes);
    
    // Clear all mocks
    jest.clearAllMocks();
  });

  describe('POST /api/auth/login', () => {
    test('should authenticate user with valid credentials', async () => {
      const mockResponse = {
        exitoso: true,
        token: 'jwt-token-123',
        usuario: {
          id: 1,
          nombreUsuario: 'testuser',
          nombre: 'Test',
          apellido: 'User',
          email: 'test@ong.com',
          rol: 'PRESIDENTE',
          activo: true
        }
      };

      mockAutenticarUsuario.mockResolvedValue(mockResponse);

      const response = await request(app)
        .post('/api/auth/login')
        .send({
          identificador: 'testuser',
          clave: 'password123'
        })
        .expect(200);

      expect(response.body).toMatchObject({
        mensaje: 'Login exitoso',
        token: 'jwt-token-123',
        usuario: {
          id: 1,
          nombreUsuario: 'testuser',
          rol: 'PRESIDENTE'
        }
      });

      expect(mockAutenticarUsuario).toHaveBeenCalledWith({
        identificador: 'testuser',
        clave: 'password123'
      });
    });

    test('should reject invalid credentials', async () => {
      const mockResponse = {
        exitoso: false,
        mensaje: 'Credenciales incorrectas'
      };

      mockAutenticarUsuario.mockResolvedValue(mockResponse);

      const response = await request(app)
        .post('/api/auth/login')
        .send({
          identificador: 'testuser',
          clave: 'wrongpassword'
        })
        .expect(401);

      expect(response.body).toMatchObject({
        error: 'Unauthorized',
        mensaje: 'Credenciales incorrectas',
        codigo: 'INVALID_CREDENTIALS'
      });
    });
  });

  describe('GET /api/usuarios', () => {
    test('should list users for Presidente', async () => {
      const mockResponse = {
        usuarios: [
          {
            id: 1,
            nombreUsuario: 'user1',
            nombre: 'User',
            apellido: 'One',
            telefono: '123456789',
            email: 'user1@ong.com',
            rol: 'VOCAL',
            activo: true,
            fechaHoraAlta: '2024-01-01T10:00:00Z',
            usuarioAlta: 'admin'
          }
        ],
        total: 1
      };

      mockListarUsuarios.mockResolvedValue(mockResponse);

      const response = await request(app)
        .get('/api/usuarios')
        .set('Authorization', 'Bearer valid-token')
        .expect(200);

      expect(response.body).toMatchObject({
        usuarios: expect.arrayContaining([
          expect.objectContaining({
            id: 1,
            nombreUsuario: 'user1',
            rol: 'VOCAL'
          })
        ]),
        total: 1,
        page: 1,
        limit: 50
      });

      expect(mockListarUsuarios).toHaveBeenCalledWith({
        page: 1,
        limit: 50,
        search: ''
      });
    });
  });

  describe('GET /api/usuarios/:id', () => {
    test('should get user by ID for Presidente', async () => {
      const mockResponse = {
        usuario: {
          id: 1,
          nombreUsuario: 'user1',
          nombre: 'User',
          apellido: 'One',
          telefono: '123456789',
          email: 'user1@ong.com',
          rol: 'VOCAL',
          activo: true,
          fechaHoraAlta: '2024-01-01T10:00:00Z',
          usuarioAlta: 'admin'
        }
      };

      mockObtenerUsuario.mockResolvedValue(mockResponse);

      const response = await request(app)
        .get('/api/usuarios/1')
        .set('Authorization', 'Bearer valid-token')
        .expect(200);

      expect(response.body).toMatchObject({
        usuario: {
          id: 1,
          nombreUsuario: 'user1',
          rol: 'VOCAL'
        }
      });

      expect(mockObtenerUsuario).toHaveBeenCalledWith({ id: 1 });
    });

    test('should return 404 for non-existent user', async () => {
      const grpcError = new Error('User not found');
      grpcError.code = 5; // NOT_FOUND
      mockObtenerUsuario.mockRejectedValue(grpcError);

      const response = await request(app)
        .get('/api/usuarios/999')
        .set('Authorization', 'Bearer valid-token')
        .expect(404);

      expect(response.body).toMatchObject({
        error: 'Not Found',
        mensaje: 'Usuario no encontrado',
        codigo: 'RESOURCE_NOT_FOUND'
      });
    });
  });

  describe('POST /api/usuarios', () => {
    test('should create user for Presidente', async () => {
      const mockResponse = {
        usuario: {
          id: 2,
          nombreUsuario: 'newuser',
          nombre: 'New',
          apellido: 'User',
          telefono: '987654321',
          email: 'newuser@ong.com',
          rol: 'VOLUNTARIO',
          activo: true,
          fechaHoraAlta: '2024-01-01T11:00:00Z',
          usuarioAlta: 'admin'
        }
      };

      mockCrearUsuario.mockResolvedValue(mockResponse);

      const userData = {
        nombreUsuario: 'newuser',
        nombre: 'New',
        apellido: 'User',
        telefono: '987654321',
        email: 'newuser@ong.com',
        rol: 'VOLUNTARIO'
      };

      const response = await request(app)
        .post('/api/usuarios')
        .set('Authorization', 'Bearer valid-token')
        .send(userData)
        .expect(201);

      expect(response.body).toMatchObject({
        mensaje: 'Usuario creado exitosamente',
        usuario: {
          id: 2,
          nombreUsuario: 'newuser',
          rol: 'VOLUNTARIO'
        }
      });

      expect(mockCrearUsuario).toHaveBeenCalledWith({
        ...userData,
        usuarioCreador: 'admin'
      });
    });

    test('should reject duplicate username/email', async () => {
      const grpcError = new Error('Duplicate entry');
      grpcError.code = 6; // ALREADY_EXISTS
      mockCrearUsuario.mockRejectedValue(grpcError);

      const userData = {
        nombreUsuario: 'existinguser',
        nombre: 'Existing',
        apellido: 'User',
        email: 'existing@ong.com',
        rol: 'VOLUNTARIO'
      };

      const response = await request(app)
        .post('/api/usuarios')
        .set('Authorization', 'Bearer valid-token')
        .send(userData)
        .expect(409);

      expect(response.body).toMatchObject({
        error: 'Conflict',
        mensaje: 'El nombre de usuario o email ya existe',
        codigo: 'DUPLICATE_ENTRY'
      });
    });
  });

  describe('PUT /api/usuarios/:id', () => {
    test('should update user for Presidente', async () => {
      // Mock the obtenerUsuario call first (for existence check)
      const mockExistingUser = {
        usuario: {
          id: 1,
          nombreUsuario: 'user1',
          nombre: 'User',
          apellido: 'One',
          email: 'user1@ong.com',
          rol: 'VOCAL',
          activo: true
        }
      };

      const mockUpdatedUser = {
        usuario: {
          id: 1,
          nombreUsuario: 'user1',
          nombre: 'Updated',
          apellido: 'User',
          telefono: '111222333',
          email: 'updated@ong.com',
          rol: 'COORDINADOR',
          activo: true,
          fechaHoraModificacion: '2024-01-01T12:00:00Z',
          usuarioModificacion: 'admin'
        }
      };

      mockObtenerUsuario.mockResolvedValue(mockExistingUser);
      mockActualizarUsuario.mockResolvedValue(mockUpdatedUser);

      const updateData = {
        nombre: 'Updated',
        telefono: '111222333',
        email: 'updated@ong.com',
        rol: 'COORDINADOR'
      };

      const response = await request(app)
        .put('/api/usuarios/1')
        .set('Authorization', 'Bearer valid-token')
        .send(updateData)
        .expect(200);

      expect(response.body).toMatchObject({
        mensaje: 'Usuario actualizado exitosamente',
        usuario: {
          id: 1,
          nombre: 'Updated',
          rol: 'COORDINADOR'
        }
      });

      expect(mockActualizarUsuario).toHaveBeenCalledWith({
        id: 1,
        ...updateData,
        usuarioModificacion: 'admin'
      });
    });
  });

  describe('DELETE /api/usuarios/:id', () => {
    test('should delete user for Presidente', async () => {
      // Mock the obtenerUsuario call first (for existence check)
      const mockExistingUser = {
        usuario: {
          id: 1,
          nombreUsuario: 'user1',
          activo: true
        }
      };

      mockObtenerUsuario.mockResolvedValue(mockExistingUser);
      mockEliminarUsuario.mockResolvedValue({});

      const response = await request(app)
        .delete('/api/usuarios/1')
        .set('Authorization', 'Bearer valid-token')
        .expect(200);

      expect(response.body).toMatchObject({
        mensaje: 'Usuario eliminado exitosamente (baja lógica)',
        codigo: 'USER_DELETED'
      });

      expect(mockEliminarUsuario).toHaveBeenCalledWith({
        id: 1,
        usuarioModificacion: 'admin'
      });
    });
  });
});