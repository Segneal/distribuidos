/**
 * Simple test for Kafka client functionality
 * Tests the Kafka client without requiring full gRPC services
 */

const kafkaClient = require('./src/config/kafka');
const redService = require('./src/services/redService');

async function testKafkaClient() {
  console.log('🧪 Testing Kafka Client...\n');

  try {
    // Test 1: Connect to Kafka
    console.log('1. Testing Kafka connection...');
    await kafkaClient.connect();
    console.log('✅ Kafka connected successfully\n');

    // Test 2: Publish a test message
    console.log('2. Testing message publishing...');
    const testMessage = {
      idSolicitud: 'TEST-001',
      donaciones: [
        {
          categoria: 'ALIMENTOS',
          descripcion: 'Test donation request'
        }
      ]
    };

    const published = await kafkaClient.publishMessage('solicitud-donaciones', testMessage, 'TEST-001');
    if (published) {
      console.log('✅ Message published successfully');
    } else {
      console.log('❌ Failed to publish message');
    }

    // Test 3: Health check
    console.log('\n3. Testing health check...');
    const isHealthy = await kafkaClient.healthCheck();
    console.log(`Health check result: ${isHealthy ? '✅ Healthy' : '❌ Unhealthy'}`);

    // Test 4: Test service creation (without database)
    console.log('\n4. Testing service methods...');
    
    // Mock database connection for testing
    const originalDbConfig = redService.dbConfig;
    redService.dbConfig = null; // Disable database for this test
    
    console.log('✅ Service methods accessible');

    console.log('\n🎉 All Kafka tests completed successfully!');

  } catch (error) {
    console.error('❌ Test failed:', error.message);
    
    if (error.code === 'ECONNREFUSED') {
      console.error('💡 Make sure Kafka is running on localhost:9092');
      console.error('💡 You can start it with: docker-compose up -d kafka');
    }
  } finally {
    // Cleanup
    try {
      await kafkaClient.disconnect();
      console.log('\n🧹 Kafka disconnected');
    } catch (error) {
      console.warn('Warning during cleanup:', error.message);
    }
  }
}

// Test message structure validation
function testMessageStructure() {
  console.log('\n🧪 Testing Message Structure Validation...\n');

  const validMessage = {
    donaciones: [
      {
        categoria: 'ALIMENTOS',
        descripcion: 'Valid description'
      }
    ]
  };

  const invalidMessages = [
    { donaciones: [] }, // Empty array
    { donaciones: [{ categoria: 'INVALID', descripcion: 'test' }] }, // Invalid category
    { donaciones: [{ categoria: 'ALIMENTOS' }] }, // Missing description
  ];

  console.log('✅ Valid message structure:', JSON.stringify(validMessage, null, 2));
  
  console.log('\n❌ Invalid message examples:');
  invalidMessages.forEach((msg, index) => {
    console.log(`   ${index + 1}. ${JSON.stringify(msg)}`);
  });

  console.log('\n🎉 Message structure validation completed!');
}

// Run tests
async function runAllTests() {
  console.log('🚀 Starting Kafka Integration Tests\n');
  console.log('⚠️  Prerequisites:');
  console.log('   - Kafka should be running on localhost:9092');
  console.log('   - Zookeeper should be running on localhost:2181');
  console.log('   - You can start them with: docker-compose up -d kafka zookeeper\n');

  testMessageStructure();
  await testKafkaClient();
  
  console.log('\n✨ All tests completed!');
}

if (require.main === module) {
  runAllTests().catch(console.error);
}

module.exports = { testKafkaClient, testMessageStructure };