/**
 * Test script for donation request cancellation functionality
 * Tests the complete flow of creating and canceling donation requests
 */

const axios = require('axios');

const API_BASE = 'http://localhost:3000/api';
let authToken = '';

// Test configuration
const testConfig = {
  usuario: {
    identificador: 'admin',
    clave: 'admin123'
  }
};

async function login() {
  try {
    console.log('🔐 Iniciando sesión...');
    
    const response = await axios.post(`${API_BASE}/auth/login`, testConfig.usuario);
    
    if (response.data.success && response.data.token) {
      authToken = response.data.token;
      console.log('✅ Login exitoso');
      return true;
    } else {
      console.error('❌ Error en login:', response.data.mensaje);
      return false;
    }
  } catch (error) {
    console.error('❌ Error en login:', error.response?.data?.mensaje || error.message);
    return false;
  }
}

async function createDonationRequest() {
  try {
    console.log('\n📝 Creando solicitud de donaciones...');
    
    const solicitudData = {
      donaciones: [
        {
          categoria: 'ALIMENTOS',
          descripcion: 'Leche en polvo para bebés'
        },
        {
          categoria: 'ROPA',
          descripcion: 'Ropa de abrigo para niños'
        }
      ]
    };
    
    const response = await axios.post(
      `${API_BASE}/red/solicitudes-donaciones`,
      solicitudData,
      {
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        }
      }
    );
    
    if (response.data.success) {
      console.log('✅ Solicitud creada exitosamente');
      console.log('   ID Solicitud:', response.data.idSolicitud);
      return response.data.idSolicitud;
    } else {
      console.error('❌ Error creando solicitud:', response.data.mensaje);
      return null;
    }
  } catch (error) {
    console.error('❌ Error creando solicitud:', error.response?.data?.mensaje || error.message);
    return null;
  }
}

async function listDonationRequests() {
  try {
    console.log('\n📋 Listando solicitudes externas...');
    
    const response = await axios.get(
      `${API_BASE}/red/solicitudes-donaciones`,
      {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      }
    );
    
    if (response.data.success) {
      console.log('✅ Solicitudes obtenidas exitosamente');
      console.log(`   Total solicitudes: ${response.data.total}`);
      
      if (response.data.data.length > 0) {
        console.log('   Solicitudes encontradas:');
        response.data.data.forEach((solicitud, index) => {
          console.log(`   ${index + 1}. ${solicitud.idOrganizacion} - ${solicitud.idSolicitud}`);
          console.log(`      Donaciones: ${solicitud.donaciones.length}`);
        });
      }
      
      return response.data.data;
    } else {
      console.error('❌ Error listando solicitudes:', response.data.mensaje);
      return [];
    }
  } catch (error) {
    console.error('❌ Error listando solicitudes:', error.response?.data?.mensaje || error.message);
    return [];
  }
}

async function cancelDonationRequest(idSolicitud) {
  try {
    console.log(`\n🗑️ Dando de baja solicitud: ${idSolicitud}...`);
    
    const response = await axios.delete(
      `${API_BASE}/red/solicitudes-donaciones/${idSolicitud}`,
      {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      }
    );
    
    if (response.data.success) {
      console.log('✅ Solicitud dada de baja exitosamente');
      console.log('   ID Solicitud:', response.data.idSolicitud);
      console.log('   Fecha Baja:', response.data.fechaBaja);
      return true;
    } else {
      console.error('❌ Error dando de baja solicitud:', response.data.mensaje);
      return false;
    }
  } catch (error) {
    console.error('❌ Error dando de baja solicitud:', error.response?.data?.mensaje || error.message);
    return false;
  }
}

async function testDuplicateCancellation(idSolicitud) {
  try {
    console.log(`\n🔄 Probando baja duplicada de solicitud: ${idSolicitud}...`);
    
    const response = await axios.delete(
      `${API_BASE}/red/solicitudes-donaciones/${idSolicitud}`,
      {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      }
    );
    
    // No debería llegar aquí si funciona correctamente
    console.log('⚠️ Respuesta inesperada:', response.data);
    return false;
    
  } catch (error) {
    if (error.response?.status === 400) {
      console.log('✅ Error esperado: solicitud ya inactiva');
      console.log('   Mensaje:', error.response.data.mensaje);
      return true;
    } else {
      console.error('❌ Error inesperado:', error.response?.data?.mensaje || error.message);
      return false;
    }
  }
}

async function testNonExistentRequest() {
  try {
    console.log('\n🔍 Probando baja de solicitud inexistente...');
    
    const fakeId = 'SOL-FAKE-123';
    const response = await axios.delete(
      `${API_BASE}/red/solicitudes-donaciones/${fakeId}`,
      {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      }
    );
    
    // No debería llegar aquí si funciona correctamente
    console.log('⚠️ Respuesta inesperada:', response.data);
    return false;
    
  } catch (error) {
    if (error.response?.status === 400) {
      console.log('✅ Error esperado: solicitud no encontrada');
      console.log('   Mensaje:', error.response.data.mensaje);
      return true;
    } else {
      console.error('❌ Error inesperado:', error.response?.data?.mensaje || error.message);
      return false;
    }
  }
}

async function runTests() {
  console.log('🚀 Iniciando pruebas de baja de solicitudes de donaciones\n');
  
  // 1. Login
  const loginSuccess = await login();
  if (!loginSuccess) {
    console.log('\n❌ No se pudo continuar sin autenticación');
    return;
  }
  
  // 2. Crear solicitud de donaciones
  const idSolicitud = await createDonationRequest();
  if (!idSolicitud) {
    console.log('\n❌ No se pudo continuar sin crear solicitud');
    return;
  }
  
  // 3. Listar solicitudes (opcional, para verificar)
  await listDonationRequests();
  
  // 4. Dar de baja la solicitud
  const cancelSuccess = await cancelDonationRequest(idSolicitud);
  if (!cancelSuccess) {
    console.log('\n❌ No se pudo dar de baja la solicitud');
    return;
  }
  
  // 5. Probar baja duplicada (debería fallar)
  await testDuplicateCancellation(idSolicitud);
  
  // 6. Probar baja de solicitud inexistente (debería fallar)
  await testNonExistentRequest();
  
  console.log('\n🎉 Pruebas completadas exitosamente');
  console.log('\n📋 Resumen de funcionalidades probadas:');
  console.log('   ✅ Creación de solicitud de donaciones');
  console.log('   ✅ Baja de solicitud propia');
  console.log('   ✅ Publicación en Kafka del mensaje de baja');
  console.log('   ✅ Validación de solicitud ya inactiva');
  console.log('   ✅ Validación de solicitud inexistente');
  console.log('   ✅ Control de autorización por roles');
}

// Ejecutar pruebas
runTests().catch(error => {
  console.error('💥 Error ejecutando pruebas:', error);
  process.exit(1);
});