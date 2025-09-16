/**
 * Test script for external events functionality
 * Tests task 7.6 implementation
 */

const axios = require('axios');

const API_BASE_URL = 'http://localhost:3000/api';

// Test configuration
const testConfig = {
  // Use existing test user credentials
  loginCredentials: {
    identificador: 'admin@ong.com',
    clave: 'admin123'
  }
};

let authToken = '';

async function login() {
  try {
    console.log('🔐 Iniciando sesión...');
    
    const response = await axios.post(`${API_BASE_URL}/auth/login`, testConfig.loginCredentials);
    
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

async function testGetExternalEvents() {
  try {
    console.log('\n📋 Probando GET /api/red/eventos-externos...');
    
    const response = await axios.get(`${API_BASE_URL}/red/eventos-externos`, {
      headers: {
        'Authorization': `Bearer ${authToken}`
      },
      params: {
        pagina: 1,
        tamanoPagina: 10,
        soloFuturos: true
      }
    });
    
    console.log('✅ Respuesta exitosa:');
    console.log('- Success:', response.data.success);
    console.log('- Total eventos:', response.data.total);
    console.log('- Eventos encontrados:', response.data.data?.length || 0);
    
    if (response.data.data && response.data.data.length > 0) {
      console.log('- Primer evento:', {
        idOrganizacion: response.data.data[0].idOrganizacion,
        nombre: response.data.data[0].nombre,
        fechaHora: response.data.data[0].fechaHora
      });
    }
    
    return true;
  } catch (error) {
    console.error('❌ Error obteniendo eventos externos:', error.response?.data?.mensaje || error.message);
    return false;
  }
}

async function testGetExternalEventsWithPagination() {
  try {
    console.log('\n📋 Probando paginación de eventos externos...');
    
    const response = await axios.get(`${API_BASE_URL}/red/eventos-externos`, {
      headers: {
        'Authorization': `Bearer ${authToken}`
      },
      params: {
        pagina: 1,
        tamanoPagina: 5,
        soloFuturos: false // Include past events
      }
    });
    
    console.log('✅ Paginación funcionando:');
    console.log('- Página 1, tamaño 5');
    console.log('- Total eventos:', response.data.total);
    console.log('- Eventos en página:', response.data.data?.length || 0);
    
    return true;
  } catch (error) {
    console.error('❌ Error en paginación:', error.response?.data?.mensaje || error.message);
    return false;
  }
}

async function testUnauthorizedAccess() {
  try {
    console.log('\n🔒 Probando acceso sin autenticación...');
    
    const response = await axios.get(`${API_BASE_URL}/red/eventos-externos`);
    
    // This should not succeed
    console.log('❌ Acceso no autorizado permitido (esto es un error)');
    return false;
  } catch (error) {
    if (error.response?.status === 401) {
      console.log('✅ Acceso correctamente denegado sin token');
      return true;
    } else {
      console.error('❌ Error inesperado:', error.message);
      return false;
    }
  }
}

async function runTests() {
  console.log('🚀 Iniciando pruebas de eventos externos (Task 7.6)');
  console.log('================================================');
  
  const results = [];
  
  // Test 1: Login
  results.push(await login());
  
  if (!authToken) {
    console.log('\n❌ No se pudo obtener token de autenticación. Abortando pruebas.');
    return;
  }
  
  // Test 2: Get external events
  results.push(await testGetExternalEvents());
  
  // Test 3: Test pagination
  results.push(await testGetExternalEventsWithPagination());
  
  // Test 4: Test unauthorized access
  results.push(await testUnauthorizedAccess());
  
  // Summary
  const passed = results.filter(r => r).length;
  const total = results.length;
  
  console.log('\n📊 RESUMEN DE PRUEBAS');
  console.log('====================');
  console.log(`✅ Pasaron: ${passed}/${total}`);
  console.log(`❌ Fallaron: ${total - passed}/${total}`);
  
  if (passed === total) {
    console.log('\n🎉 ¡Todas las pruebas de eventos externos pasaron!');
    console.log('✅ Task 7.6 implementado correctamente');
  } else {
    console.log('\n⚠️  Algunas pruebas fallaron. Revisar implementación.');
  }
}

// Handle unhandled promise rejections
process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
});

// Run tests
runTests().catch(console.error);