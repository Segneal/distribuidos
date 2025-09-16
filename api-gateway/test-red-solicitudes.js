/**
 * Test script for donation request functionality
 * Tests both API endpoints and Kafka integration
 */

const axios = require('axios');

const API_BASE = 'http://localhost:3000/api';

async function testDonationRequests() {
  try {
    console.log('🧪 Testing Donation Request Functionality...\n');

    // Step 1: Login to get token
    console.log('1. Logging in as admin...');
    const loginResponse = await axios.post(`${API_BASE}/auth/login`, {
      identificador: 'admin',
      clave: 'admin123'
    });

    if (loginResponse.status !== 200) {
      throw new Error('Login failed');
    }

    const token = loginResponse.data.token;
    console.log('✅ Login successful\n');

    // Step 2: Create donation request
    console.log('2. Creating donation request...');
    const donationRequest = {
      donaciones: [
        {
          categoria: 'ALIMENTOS',
          descripcion: 'Leche en polvo para niños pequeños'
        },
        {
          categoria: 'ROPA',
          descripcion: 'Ropa de abrigo para invierno - tallas variadas'
        },
        {
          categoria: 'JUGUETES',
          descripcion: 'Juguetes educativos para niños de 3-8 años'
        }
      ]
    };

    const createResponse = await axios.post(
      `${API_BASE}/red/solicitudes-donaciones`,
      donationRequest,
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      }
    );

    if (createResponse.status !== 201) {
      throw new Error('Failed to create donation request');
    }

    console.log('✅ Donation request created successfully');
    console.log('📋 Request ID:', createResponse.data.idSolicitud);
    console.log('📝 Message:', createResponse.data.mensaje);
    console.log();

    // Step 3: Wait a moment for Kafka processing
    console.log('3. Waiting for Kafka processing...');
    await new Promise(resolve => setTimeout(resolve, 2000));
    console.log('✅ Wait completed\n');

    // Step 4: Get external donation requests
    console.log('4. Fetching external donation requests...');
    const getResponse = await axios.get(
      `${API_BASE}/red/solicitudes-donaciones`,
      {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      }
    );

    if (getResponse.status !== 200) {
      throw new Error('Failed to get donation requests');
    }

    console.log('✅ External requests fetched successfully');
    console.log('📊 Total requests:', getResponse.data.total);
    
    if (getResponse.data.data.length > 0) {
      console.log('📋 Sample requests:');
      getResponse.data.data.slice(0, 3).forEach((request, index) => {
        console.log(`   ${index + 1}. Org: ${request.idOrganizacion}`);
        console.log(`      ID: ${request.idSolicitud}`);
        console.log(`      Donations: ${request.donaciones.length} items`);
        console.log(`      Date: ${request.fechaRecepcion}`);
      });
    } else {
      console.log('📋 No external requests found (this is normal for isolated testing)');
    }

    console.log('\n🎉 All tests completed successfully!');

  } catch (error) {
    console.error('❌ Test failed:', error.message);
    
    if (error.response) {
      console.error('📄 Response status:', error.response.status);
      console.error('📄 Response data:', JSON.stringify(error.response.data, null, 2));
    }
    
    process.exit(1);
  }
}

// Test validation scenarios
async function testValidation() {
  try {
    console.log('\n🧪 Testing Validation Scenarios...\n');

    // Login first
    const loginResponse = await axios.post(`${API_BASE}/auth/login`, {
      identificador: 'admin',
      clave: 'admin123'
    });
    const token = loginResponse.data.token;

    // Test 1: Invalid categoria
    console.log('1. Testing invalid categoria...');
    try {
      await axios.post(
        `${API_BASE}/red/solicitudes-donaciones`,
        {
          donaciones: [
            {
              categoria: 'CATEGORIA_INVALIDA',
              descripcion: 'Test description'
            }
          ]
        },
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );
      console.log('❌ Should have failed with invalid categoria');
    } catch (error) {
      if (error.response && error.response.status === 400) {
        console.log('✅ Correctly rejected invalid categoria');
      } else {
        throw error;
      }
    }

    // Test 2: Empty donaciones array
    console.log('2. Testing empty donaciones array...');
    try {
      await axios.post(
        `${API_BASE}/red/solicitudes-donaciones`,
        { donaciones: [] },
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );
      console.log('❌ Should have failed with empty array');
    } catch (error) {
      if (error.response && error.response.status === 400) {
        console.log('✅ Correctly rejected empty donaciones array');
      } else {
        throw error;
      }
    }

    // Test 3: Missing descripcion
    console.log('3. Testing missing descripcion...');
    try {
      await axios.post(
        `${API_BASE}/red/solicitudes-donaciones`,
        {
          donaciones: [
            {
              categoria: 'ALIMENTOS'
              // Missing descripcion
            }
          ]
        },
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );
      console.log('❌ Should have failed with missing descripcion');
    } catch (error) {
      if (error.response && error.response.status === 400) {
        console.log('✅ Correctly rejected missing descripcion');
      } else {
        throw error;
      }
    }

    console.log('\n🎉 All validation tests passed!');

  } catch (error) {
    console.error('❌ Validation test failed:', error.message);
    if (error.response) {
      console.error('📄 Response:', JSON.stringify(error.response.data, null, 2));
    }
  }
}

// Run tests
async function runAllTests() {
  console.log('🚀 Starting Donation Request Tests\n');
  console.log('⚠️  Make sure the API Gateway is running on port 3000');
  console.log('⚠️  Make sure Kafka is running and accessible\n');

  await testDonationRequests();
  await testValidation();
  
  console.log('\n✨ All tests completed!');
}

if (require.main === module) {
  runAllTests().catch(console.error);
}

module.exports = { testDonationRequests, testValidation };