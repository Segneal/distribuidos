// Debug proto loading
const path = require('path');

console.log('🔧 Verificando carga de proto files...');

try {
  // Verificar si los archivos proto existen
  const fs = require('fs');
  const protoPath = path.join(__dirname, 'grpc-services/proto');
  
  console.log('📁 Verificando directorio proto:', protoPath);
  
  if (fs.existsSync(protoPath)) {
    console.log('✅ Directorio proto existe');
    const files = fs.readdirSync(protoPath);
    console.log('📄 Archivos encontrados:', files);
    
    // Verificar user.proto específicamente
    const userProtoPath = path.join(protoPath, 'user.proto');
    if (fs.existsSync(userProtoPath)) {
      console.log('✅ user.proto existe');
      const content = fs.readFileSync(userProtoPath, 'utf8');
      console.log('📝 Primeras líneas de user.proto:');
      console.log(content.split('\n').slice(0, 10).join('\n'));
    } else {
      console.log('❌ user.proto no existe');
    }
  } else {
    console.log('❌ Directorio proto no existe');
  }
  
  // Intentar cargar la configuración gRPC
  console.log('\n🔧 Intentando cargar configuración gRPC...');
  const grpcConfig = require('./api-gateway/src/config/grpc');
  console.log('✅ Configuración gRPC cargada');
  
  // Verificar proto descriptors
  console.log('\n🔧 Verificando proto descriptors...');
  console.log('Descriptors disponibles:', Object.keys(grpcConfig.protoDescriptors));
  
  if (grpcConfig.protoDescriptors.usuario) {
    console.log('✅ Descriptor usuario existe');
    console.log('Contenido usuario:', Object.keys(grpcConfig.protoDescriptors.usuario));
    
    if (grpcConfig.protoDescriptors.usuario.usuario) {
      console.log('✅ Paquete usuario.usuario existe');
      console.log('Contenido usuario.usuario:', Object.keys(grpcConfig.protoDescriptors.usuario.usuario));
      
      if (grpcConfig.protoDescriptors.usuario.usuario.UsuarioService) {
        console.log('✅ UsuarioService existe');
        console.log('Tipo de UsuarioService:', typeof grpcConfig.protoDescriptors.usuario.usuario.UsuarioService);
      } else {
        console.log('❌ UsuarioService no existe');
      }
    } else {
      console.log('❌ Paquete usuario.usuario no existe');
    }
  } else {
    console.log('❌ Descriptor usuario no existe');
  }
  
} catch (error) {
  console.error('❌ Error:', error);
}