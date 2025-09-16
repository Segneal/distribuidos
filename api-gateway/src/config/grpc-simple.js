// Simplified gRPC configuration for development
const grpc = require('@grpc/grpc-js');

// Mock gRPC configuration for development when proto files are not available
const grpcConfig = {
  userService: {
    host: process.env.USER_SERVICE_HOST || 'localhost',
    port: process.env.USER_SERVICE_PORT || '50051',
    options: {
      'grpc.keepalive_time_ms': 30000,
      'grpc.keepalive_timeout_ms': 5000,
      'grpc.keepalive_permit_without_calls': true,
      'grpc.http2.max_pings_without_data': 0,
      'grpc.http2.min_time_between_pings_ms': 10000,
      'grpc.http2.min_ping_interval_without_data_ms': 300000
    }
  },
  inventoryService: {
    host: process.env.INVENTORY_SERVICE_HOST || 'localhost',
    port: process.env.INVENTORY_SERVICE_PORT || '50052',
    options: {
      'grpc.keepalive_time_ms': 30000,
      'grpc.keepalive_timeout_ms': 5000,
      'grpc.keepalive_permit_without_calls': true,
      'grpc.http2.max_pings_without_data': 0,
      'grpc.http2.min_time_between_pings_ms': 10000,
      'grpc.http2.min_ping_interval_without_data_ms': 300000
    }
  },
  eventsService: {
    host: process.env.EVENTS_SERVICE_HOST || 'localhost',
    port: process.env.EVENTS_SERVICE_PORT || '50053',
    options: {
      'grpc.keepalive_time_ms': 30000,
      'grpc.keepalive_timeout_ms': 5000,
      'grpc.keepalive_permit_without_calls': true,
      'grpc.http2.max_pings_without_data': 0,
      'grpc.http2.min_time_between_pings_ms': 10000,
      'grpc.http2.min_ping_interval_without_data_ms': 300000
    }
  }
};

// Create credentials
const createCredentials = () => {
  if (process.env.NODE_ENV === 'production') {
    return grpc.credentials.createSsl();
  }
  return grpc.credentials.createInsecure();
};

// Mock proto descriptors for development
const protoDescriptors = {
  usuario: {
    usuario: {
      UsuarioService: class MockUsuarioService {
        constructor(address, credentials, options) {
          console.log(`Mock Usuario Service client created for ${address}`);
        }
      }
    }
  },
  inventario: {
    inventario: {
      InventarioService: class MockInventarioService {
        constructor(address, credentials, options) {
          console.log(`Mock Inventario Service client created for ${address}`);
        }
      }
    }
  },
  evento: {
    evento: {
      EventoService: class MockEventoService {
        constructor(address, credentials, options) {
          console.log(`Mock Evento Service client created for ${address}`);
        }
      }
    }
  }
};

module.exports = {
  grpc,
  protoDescriptors,
  grpcConfig,
  createCredentials
};