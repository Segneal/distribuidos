// Working API Gateway main application file
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

// Basic middleware
app.use(helmet());
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Request logging
app.use((req, res, next) => {
  console.log(`${new Date().toISOString()} - ${req.method} ${req.path}`);
  next();
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ 
    status: 'OK', 
    service: 'API Gateway', 
    timestamp: new Date().toISOString(),
    version: '1.0.0',
    environment: process.env.NODE_ENV || 'development'
  });
});

// Root endpoint
app.get('/', (req, res) => {
  res.json({
    message: 'Sistema ONG API Gateway',
    version: '1.0.0',
    documentation: '/api-docs',
    health: '/health',
    endpoints: {
      auth: '/api/auth',
      usuarios: '/api/usuarios',
      inventario: '/api/inventario',
      eventos: '/api/eventos',
      red: '/api/red'
    }
  });
});

// API routes placeholder
app.get('/api', (req, res) => {
  res.json({
    message: 'Sistema ONG API',
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

// Auth routes placeholder
app.post('/api/auth/login', (req, res) => {
  res.status(501).json({ mensaje: 'Endpoint no implementado aún' });
});

app.get('/api/auth/perfil', (req, res) => {
  res.status(501).json({ mensaje: 'Endpoint no implementado aún' });
});

// Users routes placeholder
app.get('/api/usuarios', (req, res) => {
  res.status(501).json({ mensaje: 'Endpoint no implementado aún' });
});

app.post('/api/usuarios', (req, res) => {
  res.status(501).json({ mensaje: 'Endpoint no implementado aún' });
});

// Inventory routes placeholder
app.get('/api/inventario', (req, res) => {
  res.status(501).json({ mensaje: 'Endpoint no implementado aún' });
});

app.post('/api/inventario', (req, res) => {
  res.status(501).json({ mensaje: 'Endpoint no implementado aún' });
});

// Events routes placeholder
app.get('/api/eventos', (req, res) => {
  res.status(501).json({ mensaje: 'Endpoint no implementado aún' });
});

app.post('/api/eventos', (req, res) => {
  res.status(501).json({ mensaje: 'Endpoint no implementado aún' });
});

// Basic Swagger docs placeholder
app.get('/api-docs', (req, res) => {
  res.send(`
    <!DOCTYPE html>
    <html>
    <head>
      <title>Sistema ONG API Documentation</title>
    </head>
    <body>
      <h1>Sistema ONG API Documentation</h1>
      <p>API documentation will be available here.</p>
      <div id="swagger-ui"></div>
    </body>
    </html>
  `);
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error('Error:', err);
  res.status(err.status || 500).json({
    error: 'Internal Server Error',
    mensaje: 'Ha ocurrido un error interno del servidor'
  });
});

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({ 
    error: 'Not Found',
    mensaje: 'Ruta no encontrada',
    path: req.originalUrl
  });
});

if (require.main === module) {
  app.listen(PORT, () => {
    console.log(`🚀 API Gateway running on port ${PORT}`);
    console.log(`📚 Documentation available at http://localhost:${PORT}/api-docs`);
    console.log(`🏥 Health check at http://localhost:${PORT}/health`);
    console.log(`🌍 Environment: ${process.env.NODE_ENV || 'development'}`);
  });
}

module.exports = app;