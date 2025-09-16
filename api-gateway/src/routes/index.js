// Main routes index
const express = require('express');
const router = express.Router();

// Import route modules
const authRoutes = require('./auth');
const usuariosRoutes = require('./usuarios');
const inventarioRoutes = require('./inventario');
const eventosRoutes = require('./eventos');
const redRoutes = require('./red');

// Health check
router.get('/health', (req, res) => {
  res.json({ 
    status: 'OK', 
    service: 'API Gateway', 
    timestamp: new Date().toISOString(),
    version: '1.0.0'
  });
});

// API routes
router.use('/auth', authRoutes);
router.use('/usuarios', usuariosRoutes);
router.use('/inventario', inventarioRoutes);
router.use('/eventos', eventosRoutes);
router.use('/red', redRoutes);

// API info endpoint
router.get('/', (req, res) => {
  res.json({
    message: 'Sistema ONG API Gateway',
    version: '1.0.0',
    documentation: '/api-docs',
    endpoints: {
      auth: '/api/auth',
      usuarios: '/api/usuarios',
      inventario: '/api/inventario',
      eventos: '/api/eventos',
      red: '/api/red'
    }
  });
});

module.exports = router;