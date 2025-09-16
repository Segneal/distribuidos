// Basic tests for API Gateway
const request = require('supertest');

// Mock the gRPC configuration to avoid proto file dependencies in tests
jest.mock('../config/grpc-simple', () => ({
  grpc: {},
  protoDescriptors: {
    usuario: { usuario: { UsuarioService: jest.fn() } },
    inventario: { inventario: { InventarioService: jest.fn() } },
    evento: { evento: { EventoService: jest.fn() } }
  },
  grpcConfig: {
    userService: { host: 'localhost', port: '50051', options: {} },
    inventoryService: { host: 'localhost', port: '50052', options: {} },
    eventsService: { host: 'localhost', port: '50053', options: {} }
  },
  createCredentials: jest.fn(() => ({}))
}));

const app = require('../app-working');

describe('API Gateway Basic Tests', () => {
  test('GET / should return API information', async () => {
    const response = await request(app)
      .get('/')
      .expect(200);
    
    expect(response.body.message).toBe('Sistema ONG API Gateway');
    expect(response.body.version).toBe('1.0.0');
    expect(response.body.endpoints).toBeDefined();
    expect(response.body.endpoints.auth).toBe('/api/auth');
  });

  test('GET /health should return health status', async () => {
    const response = await request(app)
      .get('/health')
      .expect(200);
    
    expect(response.body.status).toBe('OK');
    expect(response.body.service).toBe('API Gateway');
    expect(response.body.timestamp).toBeDefined();
  });

  test('GET /api should return API routes information', async () => {
    const response = await request(app)
      .get('/api')
      .expect(200);
    
    expect(response.body.endpoints).toBeDefined();
  });

  test('GET /nonexistent should return 404', async () => {
    const response = await request(app)
      .get('/nonexistent')
      .expect(404);
    
    expect(response.body.error).toBe('Not Found');
    expect(response.body.mensaje).toBe('Ruta no encontrada');
  });

  test('GET /api-docs should serve Swagger documentation', async () => {
    const response = await request(app)
      .get('/api-docs/')
      .expect(200);
    
    expect(response.text).toContain('swagger-ui');
  });

  test('POST /api/auth/login should return not implemented', async () => {
    const response = await request(app)
      .post('/api/auth/login')
      .send({ identificador: 'test', clave: 'test' })
      .expect(501);
    
    expect(response.body.mensaje).toBe('Endpoint no implementado aún');
  });

  test('GET /api/usuarios should return not implemented', async () => {
    const response = await request(app)
      .get('/api/usuarios')
      .expect(501);
    
    expect(response.body.mensaje).toBe('Endpoint no implementado aún');
  });
});