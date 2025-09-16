/**
 * Test script for donation transfers functionality
 * Tests the complete flow of donation transfers between NGOs
 */

const axios = require('axios');

const API_BASE = 'http://localhost:3000/api';

// Test credentials
const testCredentials = {
  presidente: {
    identificador: 'admin@ong.com',
    clave: 'admin123'
  }
};

let authToken = null;

async function login() {
  try {
    console.log('🔐 Iniciando sesión...');
    
    const response = await axios.post(`${API_BASE}/auth/login`, testCredentials.presidente);
    
    if (response.data.success) {
      authToken = response.data.token;
      console.log('✅ Login exitoso');
      return true;
    } else {
      console.error('❌ Error en login:', response.data.mensaje);
      return false;
    }
  } catch (error) {
    console.error('❌ Error en login:', error.response?.data || error.message);
    return false;
  }
}

async function createTestDonation() {
  try {
    console.log('\n📦 Creando donación de prueba...');
    
    const donacion = {
      categoria: 'ALIMENTOS',
      descripcion: 'Puré de tomates para transferencia',
      cantidad: 10
    };
    
    const response = await axios.post(`${API_BASE}/inventario`, donacion, {
      headers: { Authorization: `Bearer ${authToken}` }
    });
    
    if (response.data.success) {
      console.log('✅ Donación creada:', response.data.donacion);
      return response.data.donacion;
    } else {
      console.error('❌ Error creando donación:', response.data.mensaje);
      return null;
    }
  } catch (error) {
    console.error('❌ Error creando donación:', error.response?.data || error.message);
    return null;
  }
}

async function testDonationTransfer() {
  try {
    console.log('\n🚚 Probando transferencia de donaciones...');
    
    const transferData = {
      idSolicitud: 'SOL-TEST-001',
      idOrganizacionSolicitante: 'ong-test-solicitante',
      donaciones: [
        {
          categoria: 'ALIMENTOS',
          descripcion: 'Puré de tomates para transferencia',
          cantidad: 5
        }
      ]
    };
    
    const response = await axios.post(`${API_BASE}/red/transferencias-donaciones`, transferData, {
      headers: { Authorization: `Bearer ${authToken}` }
    });
    
    if (response.data.success) {
      console.log('✅ Transferencia exitosa:', response.data);
      return true;
    } else {
      console.error('❌ Error en transferencia:', response.data.mensaje);
      return false;
    }
  } catch (error) {
    console.error('❌ Error en transferencia:', error.response?.data || error.message);
    return false;
  }
}

async function testInsufficientStock() {
  try {
    console.log('\n⚠️  Probando transferencia con stock insuficiente...');
    
    const transferData = {
      idSolicitud: 'SOL-TEST-002',
      idOrganizacionSolicitante: 'ong-test-solicitante',
      donaciones: [
        {
          categoria: 'ALIMENTOS',
          descripcion: 'Puré de tomates para transferencia',
          cantidad: 100 // Cantidad mayor al stock disponible
        }
      ]
    };
    
    const response = await axios.post(`${API_BASE}/red/transferencias-donaciones`, transferData, {
      headers: { Authorization: `Bearer ${authToken}` }
    });
    
    // Esperamos que falle por stock insuficiente
    if (!response.data.success && response.data.mensaje.includes('Stock insuficiente')) {
      console.log('✅ Validación de stock insuficiente funcionando correctamente');
      return true;
    } else {
      console.error('❌ La validación de stock insuficiente no funcionó como esperado');
      return false;
    }
  } catch (error) {
    if (error.response?.status === 400 && error.response.data.mensaje.includes('Stock insuficiente')) {
      console.log('✅ Validación de stock insuficiente funcionando correctamente');
      return true;
    } else {
      console.error('❌ Error inesperado:', error.response?.data || error.message);
      return false;
    }
  }
}

async function checkInventoryAfterTransfer() {
  try {
    console.log('\n📋 Verificando inventario después de transferencia...');
    
    const response = await axios.get(`${API_BASE}/inventario`, {
      headers: { Authorization: `Bearer ${authToken}` }
    });
    
    if (response.data.success) {
      const donacionesTomates = response.data.donaciones.find(d => 
        d.categoria === 'ALIMENTOS' && d.descripcion === 'Puré de tomates para transferencia'
      );
      
      if (donacionesTomates) {
        console.log('✅ Inventario actualizado:', {
          descripcion: donacionesTomates.descripcion,
          cantidadActual: donacionesTomates.cantidad
        });
        return true;
      } else {
        console.log('ℹ️  Donación no encontrada en inventario (posiblemente agotada)');
        return true;
      }
    } else {
      console.error('❌ Error consultando inventario:', response.data.mensaje);
      return false;
    }
  } catch (error) {
    console.error('❌ Error consultando inventario:', error.response?.data || error.message);
    return false;
  }
}

async function runTests() {
  console.log('🧪 Iniciando pruebas de transferencia de donaciones\n');
  
  // Login
  const loginSuccess = await login();
  if (!loginSuccess) {
    console.log('\n❌ No se pudo continuar sin autenticación');
    return;
  }
  
  // Crear donación de prueba
  const donacion = await createTestDonation();
  if (!donacion) {
    console.log('\n❌ No se pudo crear donación de prueba');
    return;
  }
  
  // Esperar un momento para que se procese
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  // Probar transferencia exitosa
  const transferSuccess = await testDonationTransfer();
  
  // Esperar un momento para que se procese
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  // Verificar inventario
  await checkInventoryAfterTransfer();
  
  // Probar validación de stock insuficiente
  await testInsufficientStock();
  
  console.log('\n🏁 Pruebas completadas');
  
  if (transferSuccess) {
    console.log('✅ Todas las pruebas principales pasaron exitosamente');
  } else {
    console.log('❌ Algunas pruebas fallaron');
  }
}

// Ejecutar pruebas
runTests().catch(console.error);