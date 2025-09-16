/**
 * Simple server test without full service initialization
 */

const express = require('express');
const cors = require('cors');
const helmet = require('helmet');

const app = express();
const PORT = 3001; // Use different port to avoid conflicts

// Basic middleware
app.use(helmet());
app.use(cors());
app.use(express.json());

// Import only the red routes for testing
const redRoutes = require('./src/routes/red');

// Mock authentication middleware for testing
const mockAuth = (req, res, next) => {
  req.usuario = {
    id: 1,
    nombreUsuario: 'voluntario_test',
    rol: 'VOLUNTARIO',
    nombre: 'Test',
    apellido: 'Volunteer',
    email: 'voluntario@test.com'
  };
  next();
};

// Apply mock auth to all red routes
app.use('/api/red', mockAuth, redRoutes);

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'OK', service: 'Test Server' });
});

// Start server
const server = app.listen(PORT, () => {
  console.log(`🧪 Test server running on port ${PORT}`);
  console.log(`🏥 Health check at http://localhost:${PORT}/health`);
  console.log(`🔗 Adhesion endpoint at http://localhost:${PORT}/api/red/eventos-externos/adhesion`);
});

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\n🛑 Shutting down test server...');
  server.close(() => {
    console.log('✅ Test server closed');
    process.exit(0);
  });
});

module.exports = app;