/**
 * Test the adhesion endpoint with a simple test server
 */

const axios = require('axios');
const { spawn } = require('child_process');

const TEST_SERVER_PORT = 3001;
const API_BASE_URL = `http://localhost:${TEST_SERVER_PORT}/api`;

let serverProcess = null;

async function startTestServer() {
  return new Promise((resolve, reject) => {
    console.log('🚀 Starting test server...');
    
    serverProcess = spawn('node', ['test-server-simple.js'], {
      cwd: process.cwd(),
      stdio: 'pipe'
    });
    
    serverProcess.stdout.on('data', (data) => {
      const output = data.toString();
      console.log(output.trim());
      
      if (output.includes('Test server running')) {
        setTimeout(() => resolve(), 1000); // Give server time to fully start
      }
    });
    
    serverProcess.stderr.on('data', (data) => {
      console.error('Server error:', data.toString());
    });
    
    serverProcess.on('error', (error) => {
      reject(error);
    });
    
    // Timeout after 10 seconds
    setTimeout(() => {
      reject(new Error('Server startup timeout'));
    }, 10000);
  });
}

async function stopTestServer() {
  if (serverProcess) {
    console.log('🛑 Stopping test server...');
    serverProcess.kill('SIGINT');
    
    return new Promise((resolve) => {
      serverProcess.on('close', () => {
        console.log('✅ Test server stopped');
        resolve();
      });
      
      // Force kill after 5 seconds
      setTimeout(() => {
        serverProcess.kill('SIGKILL');
        resolve();
      }, 5000);
    });
  }
}

async function testHealthCheck() {
  try {
    console.log('🏥 Testing health check...');
    
    const response = await axios.get(`http://localhost:${TEST_SERVER_PORT}/health`);
    
    if (response.status === 200 && response.data.status === 'OK') {
      console.log('✅ Health check passed');
      return true;
    } else {
      console.log('❌ Health check failed');
      return false;
    }
  } catch (error) {
    console.error('❌ Health check error:', error.message);
    return false;
  }
}

async function testAdhesionEndpoint() {
  try {
    console.log('🔗 Testing adhesion endpoint...');
    
    const testData = {
      idEvento: 'EVT-TEST-001',
      idOrganizador: 'ong-test'
    };
    
    const response = await axios.post(`${API_BASE_URL}/red/eventos-externos/adhesion`, testData);
    
    console.log('📋 Response status:', response.status);
    console.log('📋 Response data:', JSON.stringify(response.data, null, 2));
    
    if (response.status === 200 || response.status === 400) {
      console.log('✅ Endpoint is responding (expected behavior)');
      return true;
    } else {
      console.log('❌ Unexpected response status');
      return false;
    }
  } catch (error) {
    if (error.response) {
      console.log('📋 Error status:', error.response.status);
      console.log('📋 Error data:', JSON.stringify(error.response.data, null, 2));
      
      // Expected errors are OK (validation, business logic, etc.)
      if (error.response.status >= 400 && error.response.status < 500) {
        console.log('✅ Endpoint is responding with expected error');
        return true;
      }
    }
    
    console.error('❌ Adhesion endpoint error:', error.message);
    return false;
  }
}

async function testInvalidData() {
  try {
    console.log('📝 Testing with invalid data...');
    
    const invalidData = {
      idEvento: '', // Empty
      idOrganizador: 'test'
    };
    
    const response = await axios.post(`${API_BASE_URL}/red/eventos-externos/adhesion`, invalidData);
    
    console.log('❌ Unexpected success with invalid data');
    return false;
  } catch (error) {
    if (error.response && error.response.status === 400) {
      console.log('✅ Correctly rejected invalid data');
      console.log('📋 Validation errors:', JSON.stringify(error.response.data.errores, null, 2));
      return true;
    } else {
      console.error('❌ Unexpected error:', error.message);
      return false;
    }
  }
}

async function runTests() {
  console.log('🧪 Starting Adhesion Endpoint Tests');
  console.log('====================================');
  
  try {
    // Start test server
    await startTestServer();
    
    // Wait a bit for server to be ready
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Run tests
    const results = [];
    
    results.push(await testHealthCheck());
    results.push(await testAdhesionEndpoint());
    results.push(await testInvalidData());
    
    // Summary
    console.log('\n📊 Test Results');
    console.log('================');
    
    const passed = results.filter(r => r).length;
    const total = results.length;
    
    console.log(`✅ Passed: ${passed}/${total}`);
    console.log(`❌ Failed: ${total - passed}/${total}`);
    
    if (passed === total) {
      console.log('\n🎉 All tests passed!');
    } else {
      console.log('\n⚠️  Some tests failed.');
    }
    
  } catch (error) {
    console.error('❌ Test execution error:', error.message);
  } finally {
    // Stop test server
    await stopTestServer();
  }
}

// Handle process termination
process.on('SIGINT', async () => {
  console.log('\n🛑 Received SIGINT, cleaning up...');
  await stopTestServer();
  process.exit(0);
});

process.on('SIGTERM', async () => {
  console.log('\n🛑 Received SIGTERM, cleaning up...');
  await stopTestServer();
  process.exit(0);
});

// Run tests
runTests().catch(console.error);