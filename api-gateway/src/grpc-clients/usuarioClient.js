// Modern gRPC client for User Service
const { grpc, protoDescriptors, grpcConfig, createCredentials } = require('../config/grpc');

class UsuarioClient {
  constructor() {
    const { host, port, options } = grpcConfig.userService;
    const credentials = createCredentials();
    
    this.client = new protoDescriptors.usuario.usuario.UsuarioService(
      `${host}:${port}`,
      credentials,
      options
    );
    
    // Connection will be established when needed
    console.log(`Usuario Service client configured for ${host}:${port}`);
  }

  // Crear usuario
  crearUsuario(request) {
    return new Promise((resolve, reject) => {
      this.client.CrearUsuario(request, (error, response) => {
        if (error) {
          reject(error);
        } else {
          resolve(response);
        }
      });
    });
  }

  // Obtener usuario por ID
  obtenerUsuario(request) {
    return new Promise((resolve, reject) => {
      this.client.ObtenerUsuario(request, (error, response) => {
        if (error) {
          reject(error);
        } else {
          resolve(response);
        }
      });
    });
  }

  // Listar usuarios
  listarUsuarios(request) {
    return new Promise((resolve, reject) => {
      this.client.ListarUsuarios(request, (error, response) => {
        if (error) {
          reject(error);
        } else {
          resolve(response);
        }
      });
    });
  }

  // Actualizar usuario
  actualizarUsuario(request) {
    return new Promise((resolve, reject) => {
      this.client.ActualizarUsuario(request, (error, response) => {
        if (error) {
          reject(error);
        } else {
          resolve(response);
        }
      });
    });
  }

  // Eliminar usuario
  eliminarUsuario(request) {
    return new Promise((resolve, reject) => {
      this.client.EliminarUsuario(request, (error, response) => {
        if (error) {
          reject(error);
        } else {
          resolve(response);
        }
      });
    });
  }

  // Autenticar usuario
  autenticarUsuario(request) {
    return new Promise((resolve, reject) => {
      this.client.AutenticarUsuario(request, (error, response) => {
        if (error) {
          reject(error);
        } else {
          resolve(response);
        }
      });
    });
  }

  // Validar token
  validarToken(request) {
    return new Promise((resolve, reject) => {
      this.client.ValidarToken(request, (error, response) => {
        if (error) {
          reject(error);
        } else {
          resolve(response);
        }
      });
    });
  }
}

module.exports = UsuarioClient;