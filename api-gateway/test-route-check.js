/**
 * Simple test to check if the adhesion route is properly defined
 */

const express = require('express');

// Create a test app
const app = express();
app.use(express.json());

// Mock middleware
const mockAuth = (req, res, next) => {
  req.usuario = { id: 1, rol: 'VOLUNTARIO' };
  next();
};

try {
  // Try to load the red routes
  const redRoutes = require('./src/routes/red');
  
  console.log('✅ Red routes loaded successfully');
  
  // Mount the routes with mock auth
  app.use('/api/red', mockAuth, redRoutes);
  
  console.log('✅ Routes mounted successfully');
  
  // Check if the route exists by examining the router stack
  const router = redRoutes;
  const routes = [];
  
  function extractRoutes(middleware, path = '') {
    if (middleware.route) {
      routes.push({
        path: path + middleware.route.path,
        methods: Object.keys(middleware.route.methods)
      });
    } else if (middleware.name === 'router') {
      middleware.handle.stack.forEach(handler => {
        extractRoutes(handler, path);
      });
    }
  }
  
  if (router.stack) {
    router.stack.forEach(layer => {
      extractRoutes(layer);
    });
  }
  
  console.log('\n📋 Found routes:');
  routes.forEach(route => {
    console.log(`   ${route.methods.join(', ').toUpperCase()} ${route.path}`);
  });
  
  // Check specifically for the adhesion route
  const adhesionRoute = routes.find(route => 
    route.path.includes('adhesion') && route.methods.includes('post')
  );
  
  if (adhesionRoute) {
    console.log('\n✅ Adhesion route found:', adhesionRoute.path);
  } else {
    console.log('\n❌ Adhesion route not found');
  }
  
  console.log('\n🎉 Route check completed successfully');
  
} catch (error) {
  console.error('❌ Error loading routes:', error.message);
  console.error('Stack trace:', error.stack);
}