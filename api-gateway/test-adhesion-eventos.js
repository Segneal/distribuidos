/**
 * Test script for external event adhesion functionality
 * Tests the POST /api/red/eventos-externos/adhesion endpoint
 */

const axios = require('axios');

const API_BASE_URL = 'http://localhost:3000/api';

// Test configuration
const testConfig = {
  // Volunteer user credentials for testing
  volunteerCredentials: {
    identificador: 'voluntario@ong.com',
    clave: 'password123'
  },
  // Non-volunteer user credentials for testing authorization
  presidentCredentials: {
    identificador: 'presidente@ong.com', 
    clave: 'password123'
  },
  // Test external event data
  externalEvent: {
    idEvento: 'EVT-EXT-001',
    idOrganizador: 'ong-hermanos-unidos'
  }
};

let volunteerToken = null;
let presidentToken = null;

async function authenticateUser(credentials, userType) {
  try {
    console.log(`\n🔐 Authenticating ${userType}...`);
    
    const response = await axios.post(`${API_BASE_URL}/auth/login`, credentials);
    
    if (response.data.success && response.data.token) {
      console.log(`✅ ${userType} authenticated successfully`);
      console.log(`   User: ${response.data.usuario.nombre} ${response.data.usuario.apellido}`);
      console.log(`   Role: ${response.data.usuario.rol}`);
      return response.data.token;
    } else {
      throw new Error(`Authentication failed: ${response.data.mensaje}`);
    }
  } catch (error) {
    console.error(`❌ ${userType} authentication failed:`, error.response?.data || error.message);
    return null;
  }
}

async function testAdhesionAsVolunteer() {
  try {
    console.log('\n📋 Testing adhesion as Volunteer...');
    
    const response = await axios.post(
      `${API_BASE_URL}/red/eventos-externos/adhesion`,
      testConfig.externalEvent,
      {
        headers: {
          'Authorization': `Bearer ${volunteerToken}`,
          'Content-Type': 'application/json'
        }
      }
    );
    
    console.log('✅ Adhesion successful:');
    console.log('   Response:', JSON.stringify(response.data, null, 2));
    
    return true;
  } catch (error) {
    console.error('❌ Adhesion failed:');
    if (error.response) {
      console.error('   Status:', error.response.status);
      console.error('   Data:', JSON.stringify(error.response.data, null, 2));
    } else {
      console.error('   Error:', error.message);
    }
    return false;
  }
}

async function testAdhesionAsNonVolunteer() {
  try {
    console.log('\n🚫 Testing adhesion as non-Volunteer (should fail)...');
    
    const response = await axios.post(
      `${API_BASE_URL}/red/eventos-externos/adhesion`,
      testConfig.externalEvent,
      {
        headers: {
          'Authorization': `Bearer ${presidentToken}`,
          'Content-Type': 'application/json'
        }
      }
    );
    
    console.log('❌ Unexpected success - non-volunteers should not be able to adhere');
    console.log('   Response:', JSON.stringify(response.data, null, 2));
    
    return false;
  } catch (error) {
    if (error.response && error.response.status === 403) {
      console.log('✅ Correctly rejected non-volunteer adhesion');
      console.log('   Status:', error.response.status);
      console.log('   Message:', error.response.data.mensaje);
      return true;
    } else {
      console.error('❌ Unexpected error:');
      console.error('   Status:', error.response?.status);
      console.error('   Data:', JSON.stringify(error.response?.data, null, 2));
      return false;
    }
  }
}

async function testInvalidData() {
  try {
    console.log('\n📝 Testing with invalid data (should fail)...');
    
    const invalidData = {
      idEvento: '', // Empty event ID
      idOrganizador: testConfig.externalEvent.idOrganizador
    };
    
    const response = await axios.post(
      `${API_BASE_URL}/red/eventos-externos/adhesion`,
      invalidData,
      {
        headers: {
          'Authorization': `Bearer ${volunteerToken}`,
          'Content-Type': 'application/json'
        }
      }
    );
    
    console.log('❌ Unexpected success with invalid data');
    console.log('   Response:', JSON.stringify(response.data, null, 2));
    
    return false;
  } catch (error) {
    if (error.response && error.response.status === 400) {
      console.log('✅ Correctly rejected invalid data');
      console.log('   Status:', error.response.status);
      console.log('   Errors:', JSON.stringify(error.response.data.errores, null, 2));
      return true;
    } else {
      console.error('❌ Unexpected error:');
      console.error('   Status:', error.response?.status);
      console.error('   Data:', JSON.stringify(error.response?.data, null, 2));
      return false;
    }
  }
}

async function testWithoutAuthentication() {
  try {
    console.log('\n🔒 Testing without authentication (should fail)...');
    
    const response = await axios.post(
      `${API_BASE_URL}/red/eventos-externos/adhesion`,
      testConfig.externalEvent
    );
    
    console.log('❌ Unexpected success without authentication');
    console.log('   Response:', JSON.stringify(response.data, null, 2));
    
    return false;
  } catch (error) {
    if (error.response && error.response.status === 401) {
      console.log('✅ Correctly rejected unauthenticated request');
      console.log('   Status:', error.response.status);
      console.log('   Message:', error.response.data.mensaje);
      return true;
    } else {
      console.error('❌ Unexpected error:');
      console.error('   Status:', error.response?.status);
      console.error('   Data:', JSON.stringify(error.response?.data, null, 2));
      return false;
    }
  }
}

async function runTests() {
  console.log('🚀 Starting External Event Adhesion Tests');
  console.log('==========================================');
  
  // Authenticate users
  volunteerToken = await authenticateUser(testConfig.volunteerCredentials, 'Volunteer');
  presidentToken = await authenticateUser(testConfig.presidentCredentials, 'President');
  
  if (!volunteerToken || !presidentToken) {
    console.log('\n❌ Authentication failed. Cannot proceed with tests.');
    return;
  }
  
  // Run tests
  const results = [];
  
  results.push(await testWithoutAuthentication());
  results.push(await testInvalidData());
  results.push(await testAdhesionAsNonVolunteer());
  results.push(await testAdhesionAsVolunteer());
  
  // Summary
  console.log('\n📊 Test Results Summary');
  console.log('=======================');
  
  const passed = results.filter(r => r).length;
  const total = results.length;
  
  console.log(`✅ Passed: ${passed}/${total}`);
  console.log(`❌ Failed: ${total - passed}/${total}`);
  
  if (passed === total) {
    console.log('\n🎉 All tests passed!');
  } else {
    console.log('\n⚠️  Some tests failed. Check the output above for details.');
  }
}

// Handle unhandled promise rejections
process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
});

// Run tests
runTests().catch(console.error);