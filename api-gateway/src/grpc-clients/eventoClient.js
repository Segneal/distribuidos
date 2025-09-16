// Modern gRPC client for Events Service
const { grpc, protoDescriptors, grpcConfig, createCredentials } = require('../config/grpc');

class EventoClient {
  constructor() {
    const { host, port, options } = grpcConfig.eventsService;
    const credentials = createCredentials();
    
    this.client = new protoDescriptors.evento.evento.EventoService(
      `${host}:${port}`,
      credentials,
      options
    );
    
    // Connection will be established when needed
    console.log(`Evento Service client configured for ${host}:${port}`);
  }

  // Crear evento
  crearEvento(request) {
    return new Promise((resolve, reject) => {
      this.client.CrearEvento(request, (error, response) => {
        if (error) {
          reject(error);
        } else {
          resolve(response);
        }
      });
    });
  }

  // Obtener evento por ID
  obtenerEvento(request) {
    return new Promise((resolve, reject) => {
      this.client.ObtenerEvento(request, (error, response) => {
        if (error) {
          reject(error);
        } else {
          resolve(response);
        }
      });
    });
  }

  // Listar eventos
  listarEventos(request) {
    return new Promise((resolve, reject) => {
      this.client.ListarEventos(request, (error, response) => {
        if (error) {
          reject(error);
        } else {
          resolve(response);
        }
      });
    });
  }

  // Actualizar evento
  actualizarEvento(request) {
    return new Promise((resolve, reject) => {
      this.client.ActualizarEvento(request, (error, response) => {
        if (error) {
          reject(error);
        } else {
          resolve(response);
        }
      });
    });
  }

  // Eliminar evento
  eliminarEvento(request) {
    return new Promise((resolve, reject) => {
      this.client.EliminarEvento(request, (error, response) => {
        if (error) {
          reject(error);
        } else {
          resolve(response);
        }
      });
    });
  }

  // Agregar participante
  agregarParticipante(request) {
    return new Promise((resolve, reject) => {
      this.client.AgregarParticipante(request, (error, response) => {
        if (error) {
          reject(error);
        } else {
          resolve(response);
        }
      });
    });
  }

  // Quitar participante
  quitarParticipante(request) {
    return new Promise((resolve, reject) => {
      this.client.QuitarParticipante(request, (error, response) => {
        if (error) {
          reject(error);
        } else {
          resolve(response);
        }
      });
    });
  }

  // Registrar donaciones repartidas
  registrarDonacionesRepartidas(request) {
    return new Promise((resolve, reject) => {
      this.client.RegistrarDonacionesRepartidas(request, (error, response) => {
        if (error) {
          reject(error);
        } else {
          resolve(response);
        }
      });
    });
  }

  // Listar eventos externos
  listarEventosExternos(request) {
    return new Promise((resolve, reject) => {
      this.client.ListarEventosExternos(request, (error, response) => {
        if (error) {
          reject(error);
        } else {
          resolve(response);
        }
      });
    });
  }
}

module.exports = EventoClient;