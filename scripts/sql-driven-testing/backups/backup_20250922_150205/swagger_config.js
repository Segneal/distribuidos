// Swagger configuration
const swaggerJsdoc = require('swagger-jsdoc');

const options = {
  definition: {
    openapi: '3.0.0',
    info: {
      title: 'Sistema ONG API',
      version: '1.0.0',
      description: `
        API Gateway para el Sistema de Gestión de ONG "Empuje Comunitario"
        
        ## Características principales:
        - **Gestión de Usuarios**: Control de acceso basado en roles (Presidente, Vocal, Coordinador, Voluntario)
        - **Inventario de Donaciones**: Gestión completa de donaciones por categorías
        - **Eventos Solidarios**: Organización y participación en eventos
        - **Red de ONGs**: Colaboración entre organizaciones mediante Kafka
        
        ## Autenticación:
        La API utiliza tokens JWT para autenticación. Incluya el token en el header Authorization:
        \`Authorization: Bearer <token>\`
        
        ## Roles y Permisos:
        - **PRESIDENTE**: Acceso completo a todas las funcionalidades
        - **VOCAL**: Gestión de inventario de donaciones
        - **COORDINADOR**: Gestión de eventos solidarios
        - **VOLUNTARIO**: Consulta y participación en eventos
      `,
      contact: {
        name: 'Sistema ONG Team',
        email: 'admin@ong.com'
      },
      license: {
        name: 'MIT',
        url: 'https://opensource.org/licenses/MIT'
      }
    },
    tags: [
      {
        name: 'Autenticación',
        description: 'Endpoints para login, logout y gestión de sesiones'
      },
      {
        name: 'Usuarios',
        description: 'Gestión de usuarios del sistema (solo Presidente)'
      },
      {
        name: 'Inventario',
        description: 'Gestión de donaciones e inventario (Presidente, Vocal)'
      },
      {
        name: 'Eventos',
        description: 'Gestión de eventos solidarios y participantes'
      },
      {
        name: 'Red de ONGs',
        description: 'Colaboración entre organizaciones (solicitudes, ofertas, transferencias)'
      }
    ],
    servers: [
      {
        url: process.env.API_BASE_URL || 'http://localhost:3000',
        description: 'Servidor de desarrollo'
      }
    ],
    components: {
      securitySchemes: {
        bearerAuth: {
          type: 'http',
          scheme: 'bearer',
          bearerFormat: 'JWT'
        }
      },
      schemas: {
        Usuario: {
          type: 'object',
          properties: {
            id: { 
              type: 'integer',
              description: 'ID único del usuario',
              example: 1
            },
            nombreUsuario: { 
              type: 'string',
              description: 'Nombre de usuario único',
              example: 'admin_ong'
            },
            nombre: { 
              type: 'string',
              description: 'Nombre del usuario',
              example: 'Juan'
            },
            apellido: { 
              type: 'string',
              description: 'Apellido del usuario',
              example: 'Pérez'
            },
            telefono: { 
              type: 'string',
              description: 'Número de teléfono',
              example: '+54 11 1234-5678'
            },
            email: { 
              type: 'string', 
              format: 'email',
              description: 'Correo electrónico único',
              example: 'juan.perez@ong.com'
            },
            rol: { 
              type: 'string', 
              enum: ['PRESIDENTE', 'VOCAL', 'COORDINADOR', 'VOLUNTARIO'],
              description: 'Rol del usuario en la organización',
              example: 'PRESIDENTE'
            },
            activo: { 
              type: 'boolean',
              description: 'Estado del usuario (activo/inactivo)',
              example: true
            },
            fechaHoraAlta: {
              type: 'string',
              format: 'date-time',
              description: 'Fecha y hora de creación',
              example: '2024-01-15T10:30:00Z'
            },
            usuarioAlta: {
              type: 'string',
              description: 'Usuario que creó el registro',
              example: 'admin_ong'
            },
            fechaHoraModificacion: {
              type: 'string',
              format: 'date-time',
              description: 'Fecha y hora de última modificación',
              example: '2024-01-20T14:45:00Z'
            },
            usuarioModificacion: {
              type: 'string',
              description: 'Usuario que modificó el registro',
              example: 'admin_ong'
            }
          },
          required: ['nombreUsuario', 'nombre', 'apellido', 'email', 'rol']
        },
        Donacion: {
          type: 'object',
          properties: {
            id: { 
              type: 'integer',
              description: 'ID único de la donación',
              example: 1
            },
            categoria: { 
              type: 'string', 
              enum: ['ROPA', 'ALIMENTOS', 'JUGUETES', 'UTILES_ESCOLARES'],
              description: 'Categoría de la donación',
              example: 'ALIMENTOS'
            },
            descripcion: { 
              type: 'string',
              description: 'Descripción detallada de la donación',
              example: 'Puré de tomates en lata'
            },
            cantidad: { 
              type: 'integer', 
              minimum: 0,
              description: 'Cantidad disponible',
              example: 50
            },
            eliminado: { 
              type: 'boolean',
              description: 'Estado de eliminación lógica',
              example: false
            },
            fechaHoraAlta: {
              type: 'string',
              format: 'date-time',
              description: 'Fecha y hora de creación',
              example: '2024-01-15T10:30:00Z'
            },
            usuarioAlta: {
              type: 'string',
              description: 'Usuario que creó el registro',
              example: 'vocal_ong'
            },
            fechaHoraModificacion: {
              type: 'string',
              format: 'date-time',
              description: 'Fecha y hora de última modificación',
              example: '2024-01-20T14:45:00Z'
            },
            usuarioModificacion: {
              type: 'string',
              description: 'Usuario que modificó el registro',
              example: 'vocal_ong'
            }
          },
          required: ['categoria', 'descripcion', 'cantidad']
        },
        Evento: {
          type: 'object',
          properties: {
            id: { 
              type: 'integer',
              description: 'ID único del evento',
              example: 1
            },
            nombre: { 
              type: 'string',
              description: 'Nombre del evento',
              example: 'Entrega de alimentos en Villa 31'
            },
            descripcion: { 
              type: 'string',
              description: 'Descripción detallada del evento',
              example: 'Evento solidario para entregar alimentos a familias necesitadas'
            },
            fechaHora: { 
              type: 'string', 
              format: 'date-time',
              description: 'Fecha y hora del evento (debe ser futura)',
              example: '2024-02-15T14:00:00Z'
            },
            participantesIds: { 
              type: 'array', 
              items: { type: 'integer' },
              description: 'IDs de usuarios participantes',
              example: [1, 2, 3]
            },
            donacionesRepartidas: {
              type: 'array',
              items: {
                type: 'object',
                properties: {
                  donacionId: { type: 'integer', example: 1 },
                  cantidadRepartida: { type: 'integer', example: 10 },
                  usuarioRegistro: { type: 'string', example: 'coordinador_ong' },
                  fechaHoraRegistro: { type: 'string', format: 'date-time', example: '2024-02-15T16:00:00Z' }
                }
              },
              description: 'Donaciones repartidas en el evento'
            }
          },
          required: ['nombre', 'descripcion', 'fechaHora']
        },
        SolicitudDonacion: {
          type: 'object',
          properties: {
            idOrganizacion: {
              type: 'string',
              description: 'ID de la organización solicitante',
              example: 'ong-empuje-comunitario'
            },
            idSolicitud: {
              type: 'string',
              description: 'ID único de la solicitud',
              example: 'SOL-2024-001'
            },
            donaciones: {
              type: 'array',
              items: {
                type: 'object',
                properties: {
                  categoria: {
                    type: 'string',
                    enum: ['ROPA', 'ALIMENTOS', 'JUGUETES', 'UTILES_ESCOLARES'],
                    example: 'ALIMENTOS'
                  },
                  descripcion: {
                    type: 'string',
                    example: 'Puré de tomates'
                  }
                }
              }
            },
            activa: {
              type: 'boolean',
              description: 'Estado de la solicitud',
              example: true
            },
            fechaRecepcion: {
              type: 'string',
              format: 'date-time',
              description: 'Fecha de recepción de la solicitud',
              example: '2024-01-15T10:30:00Z'
            }
          }
        },
        OfertaDonacion: {
          type: 'object',
          properties: {
            idOrganizacion: {
              type: 'string',
              description: 'ID de la organización oferente',
              example: 'ong-hermanos-unidos'
            },
            idOferta: {
              type: 'string',
              description: 'ID único de la oferta',
              example: 'OF-2024-001'
            },
            donaciones: {
              type: 'array',
              items: {
                type: 'object',
                properties: {
                  categoria: {
                    type: 'string',
                    enum: ['ROPA', 'ALIMENTOS', 'JUGUETES', 'UTILES_ESCOLARES'],
                    example: 'ROPA'
                  },
                  descripcion: {
                    type: 'string',
                    example: 'Ropa de abrigo para niños'
                  },
                  cantidad: {
                    type: 'integer',
                    example: 25
                  }
                }
              }
            },
            fechaRecepcion: {
              type: 'string',
              format: 'date-time',
              description: 'Fecha de recepción de la oferta',
              example: '2024-01-15T10:30:00Z'
            }
          }
        },
        EventoExterno: {
          type: 'object',
          properties: {
            idOrganizacion: {
              type: 'string',
              description: 'ID de la organización organizadora',
              example: 'ong-corazones-solidarios'
            },
            idEvento: {
              type: 'string',
              description: 'ID único del evento',
              example: 'EV-2024-001'
            },
            nombre: {
              type: 'string',
              description: 'Nombre del evento',
              example: 'Jornada de vacunación'
            },
            descripcion: {
              type: 'string',
              description: 'Descripción del evento',
              example: 'Jornada gratuita de vacunación para niños'
            },
            fechaHora: {
              type: 'string',
              format: 'date-time',
              description: 'Fecha y hora del evento',
              example: '2024-02-20T09:00:00Z'
            },
            activo: {
              type: 'boolean',
              description: 'Estado del evento',
              example: true
            },
            fechaRecepcion: {
              type: 'string',
              format: 'date-time',
              description: 'Fecha de recepción del evento',
              example: '2024-01-15T10:30:00Z'
            }
          }
        },
        LoginRequest: {
          type: 'object',
          required: ['identificador', 'clave'],
          properties: {
            identificador: {
              type: 'string',
              description: 'Nombre de usuario o email',
              example: 'admin_ong'
            },
            clave: {
              type: 'string',
              description: 'Contraseña del usuario',
              example: 'password123'
            }
          }
        },
        LoginResponse: {
          type: 'object',
          properties: {
            mensaje: {
              type: 'string',
              example: 'Login exitoso'
            },
            token: {
              type: 'string',
              description: 'Token JWT para autenticación',
              example: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
            },
            usuario: {
              $ref: '#/components/schemas/Usuario'
            }
          }
        },
        Error: {
          type: 'object',
          properties: {
            error: { 
              type: 'string',
              description: 'Tipo de error',
              example: 'Bad Request'
            },
            mensaje: { 
              type: 'string',
              description: 'Mensaje descriptivo del error',
              example: 'Datos de entrada inválidos'
            },
            codigo: { 
              type: 'string',
              description: 'Código interno del error',
              example: 'INVALID_INPUT'
            }
          }
        },
        ValidationError: {
          type: 'object',
          properties: {
            success: {
              type: 'boolean',
              example: false
            },
            mensaje: {
              type: 'string',
              example: 'Datos de entrada inválidos'
            },
            errores: {
              type: 'array',
              items: {
                type: 'object',
                properties: {
                  field: { type: 'string', example: 'email' },
                  message: { type: 'string', example: 'Email inválido' }
                }
              }
            }
          }
        }
      },
      examples: {
        UsuarioEjemplo: {
          summary: 'Usuario Presidente',
          value: {
            id: 1,
            nombreUsuario: 'admin_ong',
            nombre: 'Juan',
            apellido: 'Pérez',
            telefono: '+54 11 1234-5678',
            email: 'juan.perez@ong.com',
            rol: 'PRESIDENTE',
            activo: true,
            fechaHoraAlta: '2024-01-15T10:30:00Z',
            usuarioAlta: 'sistema',
            fechaHoraModificacion: '2024-01-20T14:45:00Z',
            usuarioModificacion: 'admin_ong'
          }
        },
        DonacionEjemplo: {
          summary: 'Donación de Alimentos',
          value: {
            id: 1,
            categoria: 'ALIMENTOS',
            descripcion: 'Puré de tomates en lata - 400g',
            cantidad: 50,
            eliminado: false,
            fechaHoraAlta: '2024-01-15T10:30:00Z',
            usuarioAlta: 'vocal_ong',
            fechaHoraModificacion: '2024-01-20T14:45:00Z',
            usuarioModificacion: 'vocal_ong'
          }
        },
        EventoEjemplo: {
          summary: 'Evento Solidario',
          value: {
            id: 1,
            nombre: 'Entrega de alimentos en Villa 31',
            descripcion: 'Evento solidario para entregar alimentos a familias necesitadas del barrio',
            fechaHora: '2024-02-15T14:00:00Z',
            participantesIds: [1, 2, 3],
            donacionesRepartidas: [
              {
                donacionId: 1,
                cantidadRepartida: 10,
                usuarioRegistro: 'coordinador_ong',
                fechaHoraRegistro: '2024-02-15T16:00:00Z'
              }
            ]
          }
        },
        LoginEjemplo: {
          summary: 'Login exitoso',
          value: {
            mensaje: 'Login exitoso',
            token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwibm9tYnJlVXN1YXJpbyI6ImFkbWluX29uZyIsInJvbCI6IlBSRVNJREVOVEUiLCJpYXQiOjE2NDA5OTUyMDAsImV4cCI6MTY0MTA4MTYwMH0.example',
            usuario: {
              id: 1,
              nombreUsuario: 'admin_ong',
              nombre: 'Juan',
              apellido: 'Pérez',
              email: 'juan.perez@ong.com',
              rol: 'PRESIDENTE',
              activo: true
            }
          }
        },
        ErrorEjemplo: {
          summary: 'Error de validación',
          value: {
            error: 'Bad Request',
            mensaje: 'Datos de entrada inválidos',
            codigo: 'INVALID_INPUT'
          }
        }
      }
    },
    security: [
      {
        bearerAuth: []
      }
    ]
  },
  apis: ['./src/routes/*.js'] // Paths to files containing OpenAPI definitions
};

const specs = swaggerJsdoc(options);

module.exports = specs;