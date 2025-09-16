// Simple test script for inventory endpoints
const express = require('express');
const app = require('./src/app');

const PORT = process.env.PORT || 3001;

// Start test server
const server = app.listen(PORT, () => {
  console.log(`Test server running on port ${PORT}`);
  console.log('Testing inventory endpoints...');
  
  // Test endpoints
  testEndpoints();
});

async function testEndpoints() {
  const axios = require('axios');
  const baseURL = `http://localhost:${PORT}`;
  
  console.log('\n=== Testing Inventory Endpoints ===\n');
  
  try {
    // Test 1: GET /api/inventario without auth (should return 401)
    console.log('1. Testing GET /api/inventario without authentication...');
    try {
      await axios.get(`${baseURL}/api/inventario`);
    } catch (error) {
      if (error.response && error.response.status === 401) {
        console.log('✅ Correctly returned 401 Unauthorized');
      } else {
        console.log('❌ Unexpected response:', error.response?.status);
      }
    }
    
    // Test 2: POST /api/inventario without auth (should return 401)
    console.log('\n2. Testing POST /api/inventario without authentication...');
    try {
      await axios.post(`${baseURL}/api/inventario`, {
        categoria: 'ROPA',
        descripcion: 'Test donation',
        cantidad: 5
      });
    } catch (error) {
      if (error.response && error.response.status === 401) {
        console.log('✅ Correctly returned 401 Unauthorized');
      } else {
        console.log('❌ Unexpected response:', error.response?.status);
      }
    }
    
    // Test 3: PUT /api/inventario/1 without auth (should return 401)
    console.log('\n3. Testing PUT /api/inventario/1 without authentication...');
    try {
      await axios.put(`${baseURL}/api/inventario/1`, {
        descripcion: 'Updated description',
        cantidad: 10
      });
    } catch (error) {
      if (error.response && error.response.status === 401) {
        console.log('✅ Correctly returned 401 Unauthorized');
      } else {
        console.log('❌ Unexpected response:', error.response?.status);
      }
    }
    
    // Test 4: DELETE /api/inventario/1 without auth (should return 401)
    console.log('\n4. Testing DELETE /api/inventario/1 without authentication...');
    try {
      await axios.delete(`${baseURL}/api/inventario/1`);
    } catch (error) {
      if (error.response && error.response.status === 401) {
        console.log('✅ Correctly returned 401 Unauthorized');
      } else {
        console.log('❌ Unexpected response:', error.response?.status);
      }
    }
    
    // Test 5: GET /api/inventario/1 without auth (should return 401)
    console.log('\n5. Testing GET /api/inventario/1 without authentication...');
    try {
      await axios.get(`${baseURL}/api/inventario/1`);
    } catch (error) {
      if (error.response && error.response.status === 401) {
        console.log('✅ Correctly returned 401 Unauthorized');
      } else {
        console.log('❌ Unexpected response:', error.response?.status);
      }
    }
    
    // Test 6: Invalid ID format
    console.log('\n6. Testing GET /api/inventario/invalid-id without authentication...');
    try {
      await axios.get(`${baseURL}/api/inventario/invalid-id`);
    } catch (error) {
      if (error.response && error.response.status === 401) {
        console.log('✅ Authentication check happens before validation (401)');
      } else {
        console.log('❌ Unexpected response:', error.response?.status);
      }
    }
    
    // Test 7: Invalid POST data
    console.log('\n7. Testing POST /api/inventario with invalid data...');
    try {
      await axios.post(`${baseURL}/api/inventario`, {
        categoria: 'INVALID_CATEGORY',
        descripcion: 'Test',
        cantidad: 'not-a-number'
      });
    } catch (error) {
      if (error.response && error.response.status === 401) {
        console.log('✅ Authentication check happens before validation (401)');
      } else {
        console.log('❌ Unexpected response:', error.response?.status);
      }
    }
    
    console.log('\n=== All endpoint structure tests completed ===');
    console.log('Note: Tests with authentication would require valid JWT tokens and running gRPC services');
    
  } catch (error) {
    console.error('Test error:', error.message);
  } finally {
    server.close();
    process.exit(0);
  }
}