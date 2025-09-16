// Debug test to check what's happening
const request = require('supertest');

// Try to load the app and see what happens
try {
  console.log('Loading app...');
  const app = require('./src/app');
  console.log('App loaded successfully');
  
  // Test basic endpoint
  request(app)
    .get('/')
    .end((err, res) => {
      if (err) {
        console.error('Request error:', err);
      } else {
        console.log('Response status:', res.status);
        console.log('Response body:', res.body);
      }
      process.exit(0);
    });
    
} catch (error) {
  console.error('Error loading app:', error);
  process.exit(1);
}