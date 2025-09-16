// Simple test server to verify basic functionality
const express = require('express');
const app = express();
const PORT = 3001;

app.use(express.json());

app.get('/', (req, res) => {
  res.json({
    message: 'Sistema ONG API Gateway',
    version: '1.0.0',
    endpoints: {
      auth: '/api/auth',
      usuarios: '/api/usuarios',
      inventario: '/api/inventario',
      eventos: '/api/eventos',
      red: '/api/red'
    }
  });
});

app.get('/health', (req, res) => {
  res.json({ 
    status: 'OK', 
    service: 'API Gateway', 
    timestamp: new Date().toISOString(),
    version: '1.0.0'
  });
});

app.get('/api', (req, res) => {
  res.json({
    endpoints: {
      auth: '/api/auth',
      usuarios: '/api/usuarios',
      inventario: '/api/inventario',
      eventos: '/api/eventos',
      red: '/api/red'
    }
  });
});

app.use('*', (req, res) => {
  res.status(404).json({ 
    error: 'Not Found',
    mensaje: 'Ruta no encontrada',
    path: req.originalUrl
  });
});

app.listen(PORT, () => {
  console.log(`Test server running on port ${PORT}`);
});

module.exports = app;