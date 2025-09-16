// Simple test for login endpoint
const axios = require('axios');

async function testLogin() {
  try {
    console.log('🔧 Probando login...');
    
    const response = await axios.post('http://localhost:3000/api/auth/login', {
      identificador: 'admin@ong.com',
      clave: 'password123'
    }, {
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    console.log('✅ Login exitoso!');
    console.log('Token:', response.data.token);
    console.log('Usuario:', response.data.usuario);
    
  } catch (error) {
    console.error('❌ Error en login:');
    if (error.response) {
      console.error('Status:', error.response.status);
      console.error('Data:', error.response.data);
    } else if (error.request) {
      console.error('No response received:', error.message);
    } else {
      console.error('Error:', error.message);
    }
  }
}

testLogin();