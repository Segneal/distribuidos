/**
 * Simple test for offers functionality without gRPC dependencies
 * Tests the route structure and validation logic
 */

const express = require('express');
const request = require('supertest');
const { body, validationResult } = require('express-validator');

// Create a simple test app with just the validation logic
const app = express();
app.use(express.json());

// Mock middleware for testing
const mockAuth = (req, res, next) => {
  req.usuario = { nombreUsuario: 'test_user', rol: 'PRESIDENTE' };
  next();
};

const mockAuthorization = (roles) => (req, res, next) => {
  if (roles.includes(req.usuario.rol)) {
    next();
  } else {
    res.status(403).json({ mensaje: 'No autorizado' });
  }
};

// Mock redService
const mockRedService = {
  createDonationOffer: async (donaciones, usuario) => {
    return {
      success: true,
      idOferta: 'OFE-TEST-123',
      mensaje: 'Oferta de donaciones publicada exitosamente',
      donaciones
    };
  },
  getExternalDonationOffers: async () => {
    return [
      {
        idOrganizacion: 'ong-externa-1',
        idOferta: 'OFE-EXT-001',
        fechaRecepcion: '2024-01-15T10:00:00Z',
        donaciones: [
          {
            categoria: 'ALIMENTOS',
            descripcion: 'Arroz blanco 1kg',
            cantidad: 10
          }
        ]
      }
    ];
  }
};

// Test routes
app.post('/api/red/ofertas-donaciones',
  mockAuth,
  mockAuthorization(['PRESIDENTE', 'VOCAL', 'COORDINADOR']),
  [
    body('donaciones')
      .isArray({ min: 1 })
      .withMessage('Debe incluir al menos una donación'),
    body('donaciones.*.categoria')
      .isIn(['ROPA', 'ALIMENTOS', 'JUGUETES', 'UTILES_ESCOLARES'])
      .withMessage('Categoría inválida'),
    body('donaciones.*.descripcion')
      .notEmpty()
      .withMessage('La descripción es requerida')
      .isLength({ max: 500 })
      .withMessage('La descripción no puede exceder 500 caracteres'),
    body('donaciones.*.cantidad')
      .isInt({ min: 1 })
      .withMessage('La cantidad debe ser un número entero mayor a 0')
  ],
  async (req, res) => {
    try {
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        return res.status(400).json({
          success: false,
          mensaje: 'Datos de entrada inválidos',
          errores: errors.array()
        });
      }

      const { donaciones } = req.body;
      const usuarioCreador = req.usuario.nombreUsuario;

      const resultado = await mockRedService.createDonationOffer(donaciones, usuarioCreador);
      
      res.status(201).json(resultado);
      
    } catch (error) {
      res.status(500).json({
        success: false,
        mensaje: 'Error interno del servidor'
      });
    }
  }
);

app.get('/api/red/ofertas-donaciones', 
  mockAuth,
  async (req, res) => {
    try {
      const ofertas = await mockRedService.getExternalDonationOffers();
      
      res.json({
        success: true,
        data: ofertas,
        total: ofertas.length
      });
      
    } catch (error) {
      res.status(500).json({
        success: false,
        mensaje: 'Error interno del servidor'
      });
    }
  }
);

// Run tests
async function runTests() {
  console.log('🧪 Ejecutando pruebas simples de ofertas...\n');

  try {
    // Test 1: Create offer successfully
    console.log('1. Probando creación de oferta exitosa...');
    const createResponse = await request(app)
      .post('/api/red/ofertas-donaciones')
      .send({
        donaciones: [
          {
            categoria: 'ALIMENTOS',
            descripcion: 'Arroz blanco 1kg',
            cantidad: 5
          },
          {
            categoria: 'ROPA',
            descripcion: 'Camisetas talle M',
            cantidad: 3
          }
        ]
      });

    if (createResponse.status === 201 && createResponse.body.success) {
      console.log('✅ Creación de oferta exitosa');
      console.log(`   ID Oferta: ${createResponse.body.idOferta}`);
      console.log(`   Donaciones: ${createResponse.body.donaciones.length}`);
    } else {
      console.log('❌ Error en creación de oferta:', createResponse.body);
    }

    // Test 2: Validation - empty donaciones
    console.log('\n2. Probando validación - donaciones vacías...');
    const emptyResponse = await request(app)
      .post('/api/red/ofertas-donaciones')
      .send({ donaciones: [] });

    if (emptyResponse.status === 400) {
      console.log('✅ Validación correcta - donaciones vacías rechazadas');
    } else {
      console.log('❌ Validación fallida:', emptyResponse.body);
    }

    // Test 3: Validation - invalid categoria
    console.log('\n3. Probando validación - categoría inválida...');
    const invalidCategoryResponse = await request(app)
      .post('/api/red/ofertas-donaciones')
      .send({
        donaciones: [{
          categoria: 'CATEGORIA_INVALIDA',
          descripcion: 'Test',
          cantidad: 1
        }]
      });

    if (invalidCategoryResponse.status === 400) {
      console.log('✅ Validación correcta - categoría inválida rechazada');
    } else {
      console.log('❌ Validación fallida:', invalidCategoryResponse.body);
    }

    // Test 4: Validation - invalid cantidad
    console.log('\n4. Probando validación - cantidad inválida...');
    const invalidQuantityResponse = await request(app)
      .post('/api/red/ofertas-donaciones')
      .send({
        donaciones: [{
          categoria: 'ALIMENTOS',
          descripcion: 'Test',
          cantidad: 0
        }]
      });

    if (invalidQuantityResponse.status === 400) {
      console.log('✅ Validación correcta - cantidad inválida rechazada');
    } else {
      console.log('❌ Validación fallida:', invalidQuantityResponse.body);
    }

    // Test 5: Get external offers
    console.log('\n5. Probando obtención de ofertas externas...');
    const getResponse = await request(app)
      .get('/api/red/ofertas-donaciones');

    if (getResponse.status === 200 && getResponse.body.success) {
      console.log('✅ Obtención de ofertas exitosa');
      console.log(`   Total ofertas: ${getResponse.body.total}`);
      if (getResponse.body.data.length > 0) {
        const oferta = getResponse.body.data[0];
        console.log(`   Primera oferta: ${oferta.idOrganizacion} - ${oferta.idOferta}`);
      }
    } else {
      console.log('❌ Error obteniendo ofertas:', getResponse.body);
    }

    console.log('\n✅ Todas las pruebas simples completadas');

  } catch (error) {
    console.error('❌ Error ejecutando pruebas:', error.message);
  }
}

// Execute tests
runTests();