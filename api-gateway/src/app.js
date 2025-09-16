// API Gateway main application file
const express = require('express');
const swaggerUi = require('swagger-ui-express');
require('dotenv').config();

// Import middleware
const {
  corsMiddleware,
  securityMiddleware,
  rateLimiters,
  handleGrpcError,
  handleGeneralError,
  handleNotFound,
  requestLogger
} = require('./middleware');

// Import routes
const apiRoutes = require('./routes/index');

// Import swagger configuration
const swaggerSpecs = require('./config/swagger');

// Import services
const redService = require('./services/redService');

const app = express();
const PORT = process.env.PORT || 3000;

// Security middleware
app.use(securityMiddleware);

// Rate limiting
app.use('/api/auth/login', rateLimiters.auth);
app.use('/api', rateLimiters.api);
app.use(rateLimiters.general);

// CORS middleware
app.use(corsMiddleware);

// Body parsing middleware
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Request logging middleware
app.use(requestLogger);

// Swagger documentation
app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerSpecs, {
  explorer: true,
  customCss: '.swagger-ui .topbar { display: none }',
  customSiteTitle: 'Sistema ONG API Documentation'
}));

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

// API routes
app.use('/api', apiRoutes);

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

// Error handling middleware
app.use(handleGrpcError);
app.use(handleGeneralError);

// 404 handler
app.use('*', handleNotFound);

// Graceful shutdown
const gracefulShutdown = async (signal) => {
  console.log(`${signal} received, shutting down gracefully`);
  
  try {
    const kafkaClient = require('./config/kafka');
    await kafkaClient.disconnect();
    console.log('✅ Kafka disconnected');
  } catch (error) {
    console.error('❌ Error during shutdown:', error);
  }
  
  process.exit(0);
};

process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
process.on('SIGINT', () => gracefulShutdown('SIGINT'));

if (require.main === module) {
  // Initialize services
  const initializeServices = async () => {
    try {
      await redService.init();
      console.log('✅ Services initialized successfully');
    } catch (error) {
      console.error('❌ Error initializing services:', error);
      process.exit(1);
    }
  };

  app.listen(PORT, async () => {
    console.log(`🚀 API Gateway running on port ${PORT}`);
    console.log(`📚 Documentation available at http://localhost:${PORT}/api-docs`);
    console.log(`🏥 Health check at http://localhost:${PORT}/health`);
    console.log(`🌍 Environment: ${process.env.NODE_ENV || 'development'}`);
    
    // Initialize services after server starts
    await initializeServices();
  });
}

module.exports = app;