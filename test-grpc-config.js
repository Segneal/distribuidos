// Test script to verify gRPC configuration
const path = require('path');

console.log('Testing gRPC configuration...');

try {
  // Test proto path
  const PROTO_PATH = path.join(__dirname, 'grpc-services/proto');
  console.log('Proto path:', PROTO_PATH);
  
  // Check if proto files exist
  const fs = require('fs');
  const userProtoPath = path.join(PROTO_PATH, 'user.proto');
  const inventoryProtoPath = path.join(PROTO_PATH, 'inventory.proto');
  const eventsProtoPath = path.join(PROTO_PATH, 'events.proto');
  
  console.log('User proto exists:', fs.existsSync(userProtoPath));
  console.log('Inventory proto exists:', fs.existsSync(inventoryProtoPath));
  console.log('Events proto exists:', fs.existsSync(eventsProtoPath));
  
  // Try to load gRPC config
  const grpcConfig = require('./api-gateway/src/config/grpc');
  console.log('gRPC config loaded successfully');
  console.log('Proto descriptors:', Object.keys(grpcConfig.protoDescriptors));
  
  // Check if usuario service is available
  if (grpcConfig.protoDescriptors.usuario && grpcConfig.protoDescriptors.usuario.usuario) {
    console.log('Usuario service available:', !!grpcConfig.protoDescriptors.usuario.usuario.UsuarioService);
  } else {
    console.log('Usuario service not found in proto descriptors');
  }
  
} catch (error) {
  console.error('Error testing gRPC config:', error.message);
  console.error('Stack:', error.stack);
}