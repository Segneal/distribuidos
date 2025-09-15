# Product Overview

## Sistema ONG Backend - "Empuje Comunitario"

A distributed backend platform for NGO management that handles users, donation inventory, and solidarity events. The system enables collaboration between NGOs through a messaging network for resource sharing and event coordination.

### Core Features
- **User Management**: Role-based access control (Presidente, Vocal, Coordinador, Voluntario)
- **Donation Inventory**: Track and manage donations by category (ROPA, ALIMENTOS, JUGUETES, UTILES_ESCOLARES)
- **Event Management**: Create and manage solidarity events with participant assignment
- **Inter-NGO Network**: Request, offer, and transfer donations between organizations
- **External Event Participation**: Allow volunteers to join events from other NGOs

### Key Business Rules
- All operations require proper role-based authorization
- Audit trails are mandatory for all critical operations
- Logical deletion is preferred over physical deletion
- Future events only (no past event creation)
- Stock validation for donation transfers