// Simple test script for Events endpoints
const axios = require('axios');

const BASE_URL = 'http://localhost:3000/api';

// Mock tokens for testing (these would be real JWT tokens in production)
const TOKENS = {
  presidente: 'mock-presidente-token',
  coordinador: 'mock-coordinador-token', 
  vocal: 'mock-vocal-token',
  voluntario: 'mock-voluntario-token'
};

async function testEventEndpoints() {
  console.log('🧪 Testing Events API Endpoints...\n');

  try {
    // Test 1: List events (should work for all authenticated users)
    console.log('1. Testing GET /api/eventos (List events)');
    try {
      const response = await axios.get(`${BASE_URL}/eventos`, {
        headers: { Authorization: `Bearer ${TOKENS.presidente}` }
      });
      console.log('✅ GET /api/eventos - Success:', response.status);
      console.log('   Response structure:', Object.keys(response.data));
    } catch (error) {
      console.log('❌ GET /api/eventos - Error:', error.response?.status, error.response?.data?.mensaje);
    }

    // Test 2: Get specific event
    console.log('\n2. Testing GET /api/eventos/:id (Get event by ID)');
    try {
      const response = await axios.get(`${BASE_URL}/eventos/1`, {
        headers: { Authorization: `Bearer ${TOKENS.presidente}` }
      });
      console.log('✅ GET /api/eventos/1 - Success:', response.status);
    } catch (error) {
      console.log('❌ GET /api/eventos/1 - Error:', error.response?.status, error.response?.data?.mensaje);
    }

    // Test 3: Create event as Presidente (should work)
    console.log('\n3. Testing POST /api/eventos (Create event as Presidente)');
    const eventData = {
      nombre: 'Evento de Prueba API',
      descripcion: 'Descripción del evento de prueba para verificar la API',
      fechaHora: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString() // Tomorrow
    };
    
    try {
      const response = await axios.post(`${BASE_URL}/eventos`, eventData, {
        headers: { 
          Authorization: `Bearer ${TOKENS.presidente}`,
          'Content-Type': 'application/json'
        }
      });
      console.log('✅ POST /api/eventos (Presidente) - Success:', response.status);
      console.log('   Created event ID:', response.data.evento?.id);
    } catch (error) {
      console.log('❌ POST /api/eventos (Presidente) - Error:', error.response?.status, error.response?.data?.mensaje);
    }

    // Test 4: Create event as Coordinador (should work)
    console.log('\n4. Testing POST /api/eventos (Create event as Coordinador)');
    try {
      const response = await axios.post(`${BASE_URL}/eventos`, eventData, {
        headers: { 
          Authorization: `Bearer ${TOKENS.coordinador}`,
          'Content-Type': 'application/json'
        }
      });
      console.log('✅ POST /api/eventos (Coordinador) - Success:', response.status);
    } catch (error) {
      console.log('❌ POST /api/eventos (Coordinador) - Error:', error.response?.status, error.response?.data?.mensaje);
    }

    // Test 5: Create event as Voluntario (should fail)
    console.log('\n5. Testing POST /api/eventos (Create event as Voluntario - should fail)');
    try {
      const response = await axios.post(`${BASE_URL}/eventos`, eventData, {
        headers: { 
          Authorization: `Bearer ${TOKENS.voluntario}`,
          'Content-Type': 'application/json'
        }
      });
      console.log('❌ POST /api/eventos (Voluntario) - Unexpected success:', response.status);
    } catch (error) {
      if (error.response?.status === 403) {
        console.log('✅ POST /api/eventos (Voluntario) - Correctly denied:', error.response.status);
      } else {
        console.log('❌ POST /api/eventos (Voluntario) - Unexpected error:', error.response?.status, error.response?.data?.mensaje);
      }
    }

    // Test 6: Update event as Presidente
    console.log('\n6. Testing PUT /api/eventos/:id (Update event as Presidente)');
    const updateData = {
      nombre: 'Evento Actualizado',
      descripcion: 'Descripción actualizada del evento'
    };
    
    try {
      const response = await axios.put(`${BASE_URL}/eventos/1`, updateData, {
        headers: { 
          Authorization: `Bearer ${TOKENS.presidente}`,
          'Content-Type': 'application/json'
        }
      });
      console.log('✅ PUT /api/eventos/1 (Presidente) - Success:', response.status);
    } catch (error) {
      console.log('❌ PUT /api/eventos/1 (Presidente) - Error:', error.response?.status, error.response?.data?.mensaje);
    }

    // Test 7: Add participant as Presidente
    console.log('\n7. Testing POST /api/eventos/:id/participantes (Add participant as Presidente)');
    const participantData = { usuarioId: 1 };
    
    try {
      const response = await axios.post(`${BASE_URL}/eventos/1/participantes`, participantData, {
        headers: { 
          Authorization: `Bearer ${TOKENS.presidente}`,
          'Content-Type': 'application/json'
        }
      });
      console.log('✅ POST /api/eventos/1/participantes (Presidente) - Success:', response.status);
    } catch (error) {
      console.log('❌ POST /api/eventos/1/participantes (Presidente) - Error:', error.response?.status, error.response?.data?.mensaje);
    }

    // Test 8: Voluntario self-assignment (should work if usuarioId matches their ID)
    console.log('\n8. Testing POST /api/eventos/:id/participantes (Voluntario self-assignment)');
    const selfAssignData = { usuarioId: 3 }; // Assuming voluntario has ID 3
    
    try {
      const response = await axios.post(`${BASE_URL}/eventos/1/participantes`, selfAssignData, {
        headers: { 
          Authorization: `Bearer ${TOKENS.voluntario}`,
          'Content-Type': 'application/json'
        }
      });
      console.log('✅ POST /api/eventos/1/participantes (Voluntario self) - Success:', response.status);
    } catch (error) {
      console.log('❌ POST /api/eventos/1/participantes (Voluntario self) - Error:', error.response?.status, error.response?.data?.mensaje);
    }

    // Test 9: Voluntario trying to assign someone else (should fail)
    console.log('\n9. Testing POST /api/eventos/:id/participantes (Voluntario assigning others - should fail)');
    const otherAssignData = { usuarioId: 1 }; // Different user ID
    
    try {
      const response = await axios.post(`${BASE_URL}/eventos/1/participantes`, otherAssignData, {
        headers: { 
          Authorization: `Bearer ${TOKENS.voluntario}`,
          'Content-Type': 'application/json'
        }
      });
      console.log('❌ POST /api/eventos/1/participantes (Voluntario other) - Unexpected success:', response.status);
    } catch (error) {
      if (error.response?.status === 403) {
        console.log('✅ POST /api/eventos/1/participantes (Voluntario other) - Correctly denied:', error.response.status);
      } else {
        console.log('❌ POST /api/eventos/1/participantes (Voluntario other) - Unexpected error:', error.response?.status, error.response?.data?.mensaje);
      }
    }

    // Test 10: Remove participant
    console.log('\n10. Testing DELETE /api/eventos/:id/participantes/:usuarioId (Remove participant)');
    try {
      const response = await axios.delete(`${BASE_URL}/eventos/1/participantes/1`, {
        headers: { Authorization: `Bearer ${TOKENS.presidente}` }
      });
      console.log('✅ DELETE /api/eventos/1/participantes/1 (Presidente) - Success:', response.status);
    } catch (error) {
      console.log('❌ DELETE /api/eventos/1/participantes/1 (Presidente) - Error:', error.response?.status, error.response?.data?.mensaje);
    }

    // Test 11: Delete event
    console.log('\n11. Testing DELETE /api/eventos/:id (Delete event)');
    try {
      const response = await axios.delete(`${BASE_URL}/eventos/1`, {
        headers: { Authorization: `Bearer ${TOKENS.presidente}` }
      });
      console.log('✅ DELETE /api/eventos/1 (Presidente) - Success:', response.status);
    } catch (error) {
      console.log('❌ DELETE /api/eventos/1 (Presidente) - Error:', error.response?.status, error.response?.data?.mensaje);
    }

    // Test 12: Test without authentication (should fail)
    console.log('\n12. Testing GET /api/eventos (No authentication - should fail)');
    try {
      const response = await axios.get(`${BASE_URL}/eventos`);
      console.log('❌ GET /api/eventos (No auth) - Unexpected success:', response.status);
    } catch (error) {
      if (error.response?.status === 401) {
        console.log('✅ GET /api/eventos (No auth) - Correctly denied:', error.response.status);
      } else {
        console.log('❌ GET /api/eventos (No auth) - Unexpected error:', error.response?.status);
      }
    }

    // Test 13: Test validation errors
    console.log('\n13. Testing POST /api/eventos (Invalid data - should fail validation)');
    const invalidData = {
      nombre: 'AB', // Too short
      descripcion: 'Short', // Too short
      fechaHora: 'invalid-date'
    };
    
    try {
      const response = await axios.post(`${BASE_URL}/eventos`, invalidData, {
        headers: { 
          Authorization: `Bearer ${TOKENS.presidente}`,
          'Content-Type': 'application/json'
        }
      });
      console.log('❌ POST /api/eventos (Invalid data) - Unexpected success:', response.status);
    } catch (error) {
      if (error.response?.status === 400) {
        console.log('✅ POST /api/eventos (Invalid data) - Correctly rejected:', error.response.status);
        console.log('   Validation errors:', error.response.data.detalles?.length || 0, 'errors found');
      } else {
        console.log('❌ POST /api/eventos (Invalid data) - Unexpected error:', error.response?.status, error.response?.data?.mensaje);
      }
    }

  } catch (error) {
    console.error('❌ Test suite error:', error.message);
  }

  console.log('\n🏁 Events API testing completed!');
  console.log('\n📝 Notes:');
  console.log('   - Some tests may show errors if the gRPC services are not running');
  console.log('   - 503 errors indicate service unavailable (expected in test environment)');
  console.log('   - 404 errors may indicate no test data exists');
  console.log('   - Authentication uses mock tokens (replace with real JWT in production)');
}

// Run the tests
if (require.main === module) {
  testEventEndpoints().catch(console.error);
}

module.exports = { testEventEndpoints };