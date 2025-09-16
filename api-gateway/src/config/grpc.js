// Modern gRPC client configuration using @grpc/grpc-js
const grpc = require('@grpc/grpc-js');
const protoLoader = require('@grpc/proto-loader');
const path = require('path');

// Load proto files with modern options
const PROTO_PATH = path.join(__dirname, '../../grpc-services/proto');

// Common proto loader options
const protoOptions = {
  keepCase: true,
  longs: String,
  enums: String,
  defaults: true,
  oneofs: true,
  includeDirs: [PROTO_PATH]
};

// Load proto files
const packageDefinitions = {
  usuario: protoLoader.loadSync(path.join(PROTO_PATH, 'user.proto'), protoOptions),
  inventario: protoLoader.loadSync(path.join(PROTO_PATH, 'inventory.proto'), protoOptions),
  evento: protoLoader.loadSync(path.join(PROTO_PATH, 'events.proto'), protoOptions)
};

// Create gRPC service definitions
const protoDescriptors = {
  usuario: grpc.loadPackageDefinition(packageDefinitions.usuario),
  inventario: grpc.loadPackageDefinition(packageDefinitions.inventario),
  evento: grpc.loadPackageDefinition(packageDefinitions.evento)
};

// gRPC client configuration with connection options
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
    // Use SSL credentials in production
    return grpc.credentials.createSsl();
  }
  // Use insecure credentials in development
  return grpc.credentials.createInsecure();
};

module.exports = {
  grpc,
  packageDefinitions,
  protoDescriptors,
  grpcConfig,
  createCredentials,
  protoOptions
};