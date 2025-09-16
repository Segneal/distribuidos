// Modern gRPC client for Inventory Service
const { grpc, protoDescriptors, grpcConfig, createCredentials } = require('../config/grpc');

class InventarioClient {
  constructor() {
    const { host, port, options } = grpcConfig.inventoryService;
    const credentials = createCredentials();
    
    this.client = new protoDescriptors.inventario.inventario.InventarioService(
      `${host}:${port}`,
      credentials,
      options
    );
    
    // Connection will be established when needed
    console.log(`Inventario Service client configured for ${host}:${port}`);
  }

  // Crear donación
  crearDonacion(request) {
    return new Promise((resolve, reject) => {
      this.client.CrearDonacion(request, (error, response) => {
        if (error) {
          reject(error);
        } else {
          resolve(response);
        }
      });
    });
  }

  // Obtener donación por ID
  obtenerDonacion(request) {
    return new Promise((resolve, reject) => {
      this.client.ObtenerDonacion(request, (error, response) => {
        if (error) {
          reject(error);
        } else {
          resolve(response);
        }
      });
    });
  }

  // Listar donaciones
  listarDonaciones(request) {
    return new Promise((resolve, reject) => {
      this.client.ListarDonaciones(request, (error, response) => {
        if (error) {
          reject(error);
        } else {
          resolve(response);
        }
      });
    });
  }

  // Actualizar donación
  actualizarDonacion(request) {
    return new Promise((resolve, reject) => {
      this.client.ActualizarDonacion(request, (error, response) => {
        if (error) {
          reject(error);
        } else {
          resolve(response);
        }
      });
    });
  }

  // Eliminar donación
  eliminarDonacion(request) {
    return new Promise((resolve, reject) => {
      this.client.EliminarDonacion(request, (error, response) => {
        if (error) {
          reject(error);
        } else {
          resolve(response);
        }
      });
    });
  }

  // Actualizar stock
  actualizarStock(request) {
    return new Promise((resolve, reject) => {
      this.client.ActualizarStock(request, (error, response) => {
        if (error) {
          reject(error);
        } else {
          resolve(response);
        }
      });
    });
  }

  // Validar stock
  validarStock(request) {
    return new Promise((resolve, reject) => {
      this.client.ValidarStock(request, (error, response) => {
        if (error) {
          reject(error);
        } else {
          resolve(response);
        }
      });
    });
  }
}

module.exports = InventarioClient;