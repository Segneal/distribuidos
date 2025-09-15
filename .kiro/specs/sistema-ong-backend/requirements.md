# Documento de Requerimientos - Sistema ONG Backend

## Introducción

El sistema backend para la ONG "Empuje Comunitario" es una plataforma distribuida que gestiona usuarios, inventario de donaciones y eventos solidarios. El sistema utiliza arquitectura de microservicios con gRPC para comunicación interna y un API Gateway REST para la interfaz web. Además, integra comunicación entre ONGs mediante colas de mensajes Kafka para colaboración interorganizacional.

## Requerimientos

### Requerimiento 1 - Gestión de Roles y Autenticación

**Historia de Usuario:** Como administrador del sistema, quiero que existan diferentes roles de usuario con permisos específicos, para que cada miembro de la ONG tenga acceso solo a las funcionalidades correspondientes a su rol.

#### Criterios de Aceptación

1. CUANDO el sistema se inicialice ENTONCES DEBERÁ definir cuatro roles: Presidente, Vocal, Coordinador y Voluntario
2. CUANDO un usuario tenga rol Presidente ENTONCES DEBERÁ tener acceso a todas las funcionalidades del sistema
3. CUANDO un usuario tenga rol Vocal ENTONCES DEBERÁ tener acceso solo al inventario de donaciones
4. CUANDO un usuario tenga rol Coordinador ENTONCES DEBERÁ tener acceso a la gestión de eventos solidarios
5. CUANDO un usuario tenga rol Voluntario ENTONCES DEBERÁ tener acceso solo a consulta y participación en eventos solidarios
6. CUANDO un usuario intente acceder a una funcionalidad ENTONCES el sistema DEBERÁ validar que su rol tenga los permisos necesarios

### Requerimiento 2 - Gestión de Usuarios (ABM)

**Historia de Usuario:** Como Presidente de la ONG, quiero gestionar los usuarios del sistema (alta, baja, modificación), para mantener actualizada la información de los miembros de la organización.

#### Criterios de Aceptación

1. CUANDO se cree un usuario ENTONCES DEBERÁ incluir: id, nombreUsuario (único), nombre, apellido, telefono, email (único), rol y estado activo/inactivo
2. CUANDO se dé de alta un usuario ENTONCES el sistema DEBERÁ generar una clave aleatoria y enviarla por email
3. CUANDO se almacene la clave ENTONCES DEBERÁ estar encriptada en la base de datos
4. CUANDO se modifique un usuario ENTONCES DEBERÁ permitir cambiar todos los campos excepto la clave
5. CUANDO se dé de baja un usuario ENTONCES DEBERÁ aplicar baja lógica marcándolo como inactivo
6. CUANDO se listen usuarios ENTONCES DEBERÁ mostrar todos los campos excepto id y clave

### Requerimiento 3 - Sistema de Autenticación

**Historia de Usuario:** Como usuario del sistema, quiero autenticarme con mis credenciales, para acceder a las funcionalidades según mi rol.

#### Criterios de Aceptación

1. CUANDO un usuario intente hacer login ENTONCES DEBERÁ poder usar nombreUsuario o email como identificador
2. CUANDO las credenciales sean incorrectas ENTONCES el sistema DEBERÁ mostrar mensaje específico del error
3. CUANDO el usuario no exista ENTONCES el sistema DEBERÁ mostrar "Usuario/email inexistente"
4. CUANDO la contraseña sea incorrecta ENTONCES el sistema DEBERÁ mostrar "Credenciales incorrectas"
5. CUANDO el usuario esté inactivo ENTONCES el sistema DEBERÁ denegar el acceso
6. CUANDO el login sea exitoso ENTONCES el sistema DEBERÁ generar un token de sesión

### Requerimiento 4 - Inventario de Donaciones

**Historia de Usuario:** Como Vocal o Presidente, quiero gestionar el inventario de donaciones, para mantener un registro actualizado de los recursos disponibles de la ONG.

#### Criterios de Aceptación

1. CUANDO se registre una donación ENTONCES DEBERÁ incluir: id, categoria (ROPA, ALIMENTOS, JUGUETES, UTILES_ESCOLARES), descripcion, cantidad, eliminado y campos de auditoría
2. CUANDO se cree o modifique una donación ENTONCES el sistema DEBERÁ registrar fechaHoraAlta/modificacion y usuarioAlta/modificacion
3. CUANDO se modifique una donación ENTONCES DEBERÁ permitir cambiar solo descripcion y cantidad
4. CUANDO la cantidad sea negativa ENTONCES el sistema DEBERÁ rechazar la operación
5. CUANDO se dé de baja una donación ENTONCES DEBERÁ aplicar baja lógica con confirmación
6. CUANDO se liste el inventario ENTONCES DEBERÁ mostrar solo elementos no eliminados

### Requerimiento 5 - Eventos Solidarios

**Historia de Usuario:** Como Coordinador o Presidente, quiero gestionar eventos solidarios, para organizar las actividades de la ONG y asignar participantes.

#### Criterios de Aceptación

1. CUANDO se cree un evento ENTONCES DEBERÁ incluir: id, nombre, descripcion, fechaHora y lista de miembros participantes
2. CUANDO se establezca la fecha del evento ENTONCES DEBERÁ ser a futuro, no se permiten eventos pasados
3. CUANDO se modifique un evento futuro ENTONCES DEBERÁ permitir cambiar nombre, fechaHora y participantes
4. CUANDO se modifique un evento pasado ENTONCES DEBERÁ permitir solo registrar donaciones repartidas
5. CUANDO se registren donaciones repartidas ENTONCES el sistema DEBERÁ descontar del inventario y registrar auditoría
6. CUANDO se dé de baja un evento ENTONCES DEBERÁ ser solo eventos futuros con eliminación física
7. CUANDO se asignen miembros ENTONCES DEBERÁ permitir solo usuarios activos

### Requerimiento 6 - Participación en Eventos

**Historia de Usuario:** Como Voluntario, quiero participar en eventos solidarios, para contribuir con las actividades de la ONG.

#### Criterios de Aceptación

1. CUANDO un Voluntario consulte eventos ENTONCES DEBERÁ ver todos los eventos futuros disponibles
2. CUANDO un Voluntario se asigne a un evento ENTONCES DEBERÁ poder agregarse solo a sí mismo
3. CUANDO un Voluntario se desasigne ENTONCES DEBERÁ poder quitarse solo a sí mismo
4. CUANDO se dé de baja un miembro ENTONCES el sistema DEBERÁ quitarlo automáticamente de eventos futuros

### Requerimiento 7 - Solicitud de Donaciones (Red de ONGs)

**Historia de Usuario:** Como miembro de la red de ONGs, quiero solicitar donaciones a otras organizaciones, para obtener recursos necesarios para nuestras actividades.

#### Criterios de Aceptación

1. CUANDO se publique una solicitud ENTONCES DEBERÁ enviar mensaje al topic "/solicitud-donaciones" con idOrganizacion, idSolicitud y lista de donaciones
2. CUANDO se reciba una solicitud externa ENTONCES el sistema DEBERÁ almacenarla para consulta interna
3. CUANDO se procesen solicitudes ENTONCES DEBERÁ cotejar con bajas de solicitudes para descartarlas
4. CUANDO se especifique una donación solicitada ENTONCES DEBERÁ incluir categoria y descripcion

### Requerimiento 8 - Transferencia de Donaciones

**Historia de Usuario:** Como organización donante, quiero transferir donaciones a organizaciones solicitantes, para colaborar con otras ONGs de la red.

#### Criterios de Aceptación

1. CUANDO se transfiera una donación ENTONCES DEBERÁ publicar en topic "/transferencia-donaciones/idOrganizacionSolicitante"
2. CUANDO se envíe transferencia ENTONCES DEBERÁ incluir idSolicitud, idOrganizacionDonante y lista con categoria, descripcion y cantidad
3. CUANDO se realice transferencia ENTONCES el sistema DEBERÁ descontar del inventario propio
4. CUANDO se reciba transferencia ENTONCES el sistema DEBERÁ sumar al inventario propio
5. CUANDO no haya stock suficiente ENTONCES el sistema DEBERÁ rechazar la transferencia

### Requerimiento 9 - Oferta de Donaciones

**Historia de Usuario:** Como organización, quiero ofrecer donaciones disponibles, para que otras ONGs puedan conocer qué recursos tenemos disponibles.

#### Criterios de Aceptación

1. CUANDO se publique una oferta ENTONCES DEBERÁ enviar al topic "/oferta-donaciones" con idOferta, idOrganizacion y lista de donaciones
2. CUANDO se reciban ofertas externas ENTONCES el sistema DEBERÁ almacenarlas para consulta
3. CUANDO se liste una oferta ENTONCES DEBERÁ incluir categoria, descripcion y cantidad disponible

### Requerimiento 10 - Baja de Solicitudes

**Historia de Usuario:** Como organización solicitante, quiero dar de baja solicitudes de donaciones, para notificar a la red que ya no necesito esos recursos.

#### Criterios de Aceptación

1. CUANDO se dé de baja una solicitud ENTONCES DEBERÁ publicar en topic "/baja-solicitud-donaciones" con idOrganizacion e idSolicitud
2. CUANDO se procese una baja ENTONCES el sistema DEBERÁ actualizar el estado de solicitudes externas correspondientes

### Requerimiento 11 - Publicación de Eventos Externos

**Historia de Usuario:** Como organización, quiero publicar eventos solidarios, para que voluntarios de otras ONGs puedan participar en nuestras actividades.

#### Criterios de Aceptación

1. CUANDO se publique un evento ENTONCES DEBERÁ enviar al topic "/eventos-solidarios" con idOrganizacion, idEvento, nombre, descripcion y fechaHora
2. CUANDO se reciban eventos externos ENTONCES el sistema DEBERÁ descartar eventos propios y almacenar solo externos
3. CUANDO se procesen eventos ENTONCES DEBERÁ verificar que estén vigentes y no dados de baja
4. CUANDO se listen eventos externos ENTONCES DEBERÁ mostrar en pantalla específica para consulta

### Requerimiento 12 - Baja de Eventos Externos

**Historia de Usuario:** Como organización, quiero notificar la baja de eventos, para que otras ONGs sepan que el evento fue cancelado.

#### Criterios de Aceptación

1. CUANDO se dé de baja un evento ENTONCES DEBERÁ publicar en topic "/baja-evento-solidario" con idOrganizacion e idEvento
2. CUANDO se procese una baja de evento ENTONCES el sistema DEBERÁ actualizar el estado de eventos externos correspondientes

### Requerimiento 13 - Adhesión a Eventos Externos

**Historia de Usuario:** Como Voluntario, quiero adherirme a eventos de otras organizaciones, para participar en actividades de la red de ONGs.

#### Criterios de Aceptación

1. CUANDO un voluntario se adhiera ENTONCES DEBERÁ publicar en topic "/adhesion-evento/id-organizador" 
2. CUANDO se envíe adhesión ENTONCES DEBERÁ incluir idEvento, idOrganizacion, idVoluntario, nombre, apellido, telefono y email
3. CUANDO se confirme adhesión ENTONCES el sistema DEBERÁ registrar la participación del voluntario

### Requerimiento 14 - Arquitectura de Microservicios

**Historia de Usuario:** Como desarrollador del sistema, quiero una arquitectura distribuida con microservicios, para garantizar escalabilidad y mantenibilidad del sistema.

#### Criterios de Aceptación

1. CUANDO se implemente la arquitectura ENTONCES DEBERÁ incluir API Gateway en Node.js con Express
2. CUANDO se desarrollen servicios ENTONCES DEBERÁ usar Python con gRPC para comunicación entre servicios
3. CUANDO se definan servicios ENTONCES DEBERÁ separar: gestión de usuarios, inventario de donaciones y eventos solidarios
4. CUANDO se integre Kafka ENTONCES DEBERÁ usar Docker para el despliegue de brokers
5. CUANDO se documenten APIs ENTONCES DEBERÁ usar Swagger para documentación
6. CUANDO se prueben servicios ENTONCES DEBERÁ incluir testing con Postman y pruebas unitarias

### Requerimiento 15 - Seguridad y Auditoría

**Historia de Usuario:** Como administrador del sistema, quiero que todas las operaciones críticas queden registradas, para mantener trazabilidad y seguridad.

#### Criterios de Aceptación

1. CUANDO se realice cualquier operación ENTONCES el sistema DEBERÁ registrar usuario, fecha y hora
2. CUANDO se encripten contraseñas ENTONCES DEBERÁ usar algoritmo seguro (bcrypt o similar)
3. CUANDO se generen tokens ENTONCES DEBERÁ tener tiempo de expiración configurable
4. CUANDO se acceda a endpoints ENTONCES DEBERÁ validar autenticación y autorización
5. CUANDO se registren auditorías ENTONCES DEBERÁ incluir operación realizada y datos modificados

### Requerimiento 16 - Documentación de Módulos

**Historia de Usuario:** Como desarrollador del sistema, quiero que cada módulo tenga documentación clara, para facilitar el mantenimiento y comprensión del código.

#### Criterios de Aceptación

1. CUANDO se desarrolle un módulo ENTONCES DEBERÁ incluir un archivo README.md en su directorio raíz
2. CUANDO se escriba la documentación ENTONCES DEBERÁ explicar qué hace el módulo
3. CUANDO se documente la instalación ENTONCES DEBERÁ incluir pasos detallados de cómo configurar el módulo
4. CUANDO se documente el uso ENTONCES DEBERÁ incluir ejemplos de cómo utilizar el módulo
5. CUANDO se actualice el módulo ENTONCES DEBERÁ actualizarse la documentación correspondiente