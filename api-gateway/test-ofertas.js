/**
 * Test script for donation offers functionality
 * Tests both creating offers and consuming external offers
 */

const axios = require('axios');

const API_BASE = 'http://localhost:3000/api';

// Test credentials
const testCredentials = {
  identificador: 'admin',
  clave: 'admin123'
};

let authToken = '';

async function login() {
  try {
    console.log('🔐 Iniciando sesión...');
    const response = await axios.post(`${API_BASE}/auth/login`, testCredentials);
    
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

async function createDonationOffer() {
  try {
    console.log('\n📤 Creando oferta de donaciones...');
    
    const offerData = {
      donaciones: [
        {
          categoria: 'ALIMENTOS',
          descripcion: 'Arroz blanco 1kg',
          cantidad: 10
        },
        {
          categoria: 'ROPA',
          descripcion: 'Camisetas talle M',
          cantidad: 5
        }
      ]
    };
    
    const response = await axios.post(
      `${API_BASE}/red/ofertas-donaciones`,
      offerData,
      {
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        }
      }
    );
    
    if (response.data.success) {
      console.log('✅ Oferta creada exitosamente:');
      console.log(`   ID Oferta: ${response.data.idOferta}`);
      console.log(`   Donaciones: ${response.data.donaciones.length}`);
      response.data.donaciones.forEach((d, i) => {
        console.log(`   ${i + 1}. ${d.categoria} - ${d.descripcion} (${d.cantidad})`);
      });
      return response.data.idOferta;
    } else {
      console.error('❌ Error creando oferta:', response.data.mensaje);
      return null;
    }
  } catch (error) {
    console.error('❌ Error creando oferta:', error.response?.data || error.message);
    return null;
  }
}

async function getExternalOffers() {
  try {
    console.log('\n📋 Obteniendo ofertas externas...');
    
    const response = await axios.get(
      `${API_BASE}/red/ofertas-donaciones`,
      {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      }
    );
    
    if (response.data.success) {
      console.log(`✅ Ofertas externas obtenidas: ${response.data.total}`);
      
      if (response.data.data.length > 0) {
        response.data.data.forEach((oferta, i) => {
          console.log(`\n   Oferta ${i + 1}:`);
          console.log(`   Organización: ${oferta.idOrganizacion}`);
          console.log(`   ID Oferta: ${oferta.idOferta}`);
          console.log(`   Fecha: ${oferta.fechaRecepcion}`);
          console.log(`   Donaciones:`);
          oferta.donaciones.forEach((d, j) => {
            console.log(`     ${j + 1}. ${d.categoria} - ${d.descripcion} (${d.cantidad})`);
          });
        });
      } else {
        console.log('   No hay ofertas externas disponibles');
      }
      
      return response.data.data;
    } else {
      console.error('❌ Error obteniendo ofertas:', response.data.mensaje);
      return [];
    }
  } catch (error) {
    console.error('❌ Error obteniendo ofertas:', error.response?.data || error.message);
    return [];
  }
}

async function testOfferValidation() {
  try {
    console.log('\n🧪 Probando validaciones de oferta...');
    
    // Test 1: Oferta sin donaciones
    try {
      await axios.post(
        `${API_BASE}/red/ofertas-donaciones`,
        { donaciones: [] },
        {
          headers: {
            'Authorization': `Bearer ${authToken}`,
            'Content-Type': 'application/json'
          }
        }
      );
      console.log('❌ Debería haber fallado - oferta sin donaciones');
    } catch (error) {
      if (error.response?.status === 400) {
        console.log('✅ Validación correcta - oferta sin donaciones rechazada');
      }
    }
    
    // Test 2: Categoría inválida
    try {
      await axios.post(
        `${API_BASE}/red/ofertas-donaciones`,
        {
          donaciones: [{
            categoria: 'CATEGORIA_INVALIDA',
            descripcion: 'Test',
            cantidad: 1
          }]
        },
        {
          headers: {
            'Authorization': `Bearer ${authToken}`,
            'Content-Type': 'application/json'
          }
        }
      );
      console.log('❌ Debería haber fallado - categoría inválida');
    } catch (error) {
      if (error.response?.status === 400) {
        console.log('✅ Validación correcta - categoría inválida rechazada');
      }
    }
    
    // Test 3: Cantidad inválida
    try {
      await axios.post(
        `${API_BASE}/red/ofertas-donaciones`,
        {
          donaciones: [{
            categoria: 'ALIMENTOS',
            descripcion: 'Test',
            cantidad: 0
          }]
        },
        {
          headers: {
            'Authorization': `Bearer ${authToken}`,
            'Content-Type': 'application/json'
          }
        }
      );
      console.log('❌ Debería haber fallado - cantidad inválida');
    } catch (error) {
      if (error.response?.status === 400) {
        console.log('✅ Validación correcta - cantidad inválida rechazada');
      }
    }
    
  } catch (error) {
    console.error('❌ Error en pruebas de validación:', error.message);
  }
}

async function runTests() {
  console.log('🚀 Iniciando pruebas de ofertas de donaciones...\n');
  
  // Login
  const loginSuccess = await login();
  if (!loginSuccess) {
    console.log('❌ No se pudo hacer login. Terminando pruebas.');
    return;
  }
  
  // Test validations
  await testOfferValidation();
  
  // Create offer
  const offerId = await createDonationOffer();
  
  // Get external offers
  await getExternalOffers();
  
  console.log('\n✅ Pruebas de ofertas completadas');
}

// Run tests
runTests().catch(console.error);