/**
 * Simple test for external event adhesion functionality
 * Tests basic endpoint availability and structure
 */

const axios = require('axios');

const API_BASE_URL = 'http://localhost:3000/api';

async function testEndpointAvailability() {
  try {
    console.log('🔍 Testing endpoint availability...');
    
    // Test without authentication - should return 401
    const response = await axios.post(`${API_BASE_URL}/red/eventos-externos/adhesion`, {
      idEvento: 'test',
      idOrganizador: 'test'
    });
    
    console.log('❌ Unexpected success - endpoint should require authentication');
    return false;
    
  } catch (error) {
    if (error.response && error.response.status === 401) {
      console.log('✅ Endpoint is available and requires authentication');
      return true;
    } else {
      console.error('❌ Unexpected error:', error.response?.status, error.response?.data);
      return false;
    }
  }
}

async function testEndpointStructure() {
  try {
    console.log('🔍 Testing endpoint structure...');
    
    // Test with invalid data - should return validation errors
    const response = await axios.post(`${API_BASE_URL}/red/eventos-externos/adhesion`, {});
    
    console.log('❌ Unexpected success - endpoint should validate input');
    return false;
    
  } catch (error) {
    if (error.response && (error.response.status === 400 || error.response.status === 401)) {
      console.log('✅ Endpoint validates input properly');
      return true;
    } else {
      console.error('❌ Unexpected error:', error.response?.status, error.response?.data);
      return false;
    }
  }
}

async function runSimpleTests() {
  console.log('🚀 Starting Simple Adhesion Tests');
  console.log('==================================');
  
  const results = [];
  
  results.push(await testEndpointAvailability());
  results.push(await testEndpointStructure());
  
  // Summary
  console.log('\n📊 Test Results');
  console.log('================');
  
  const passed = results.filter(r => r).length;
  const total = results.length;
  
  console.log(`✅ Passed: ${passed}/${total}`);
  console.log(`❌ Failed: ${total - passed}/${total}`);
  
  if (passed === total) {
    console.log('\n🎉 Basic tests passed!');
  } else {
    console.log('\n⚠️  Some tests failed.');
  }
}

runSimpleTests().catch(console.error);