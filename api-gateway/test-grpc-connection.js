// Test gRPC connection
const UsuarioClient = require('./src/grpc-clients/usuarioClient');

async function testGrpcConnection() {
  console.log('🔧 Probando conexión gRPC...');
  
  try {
    const usuarioClient = new UsuarioClient();
    console.log('✅ Cliente gRPC creado exitosamente');
    
    // Test authentication
    const response = await usuarioClient.autenticarUsuario({
      identificador: 'admin',
      clave: 'password123'
    });
    
    console.log('✅ Respuesta gRPC recibida:', response);
    
  } catch (error) {
    console.error('❌ Error en conexión gRPC:', error);
    console.error('Código de error:', error.code);
    console.error('Detalles:', error.details);
    console.error('Stack:', error.stack);
  }
}

testGrpcConnection();