# Database Schema - Sistema ONG

This directory contains the database schema and migration scripts for the Sistema ONG Backend.

## Files

- `migrate.sql` - Complete migration script that creates database and all tables
- `init/00-create-database.sql` - Creates the main database
- `init/01-create-tables.sql` - Creates all required tables with indexes
- `init/02-insert-sample-data.sql` - Inserts sample data for testing

## Database Structure

### Core Tables

#### usuarios
Stores user information with role-based access control.
- **Roles**: PRESIDENTE, VOCAL, COORDINADOR, VOLUNTARIO
- **Features**: Logical deletion, audit fields, unique constraints

#### donaciones
Manages donation inventory with categories.
- **Categories**: ROPA, ALIMENTOS, JUGUETES, UTILES_ESCOLARES
- **Features**: Stock control, logical deletion, audit fields

#### eventos
Manages solidarity events.
- **Features**: Future date validation, participant management, audit fields

#### evento_participantes
Many-to-many relationship between events and users.

#### donaciones_repartidas
Tracks donations distributed during events.

### Inter-NGO Network Tables

#### solicitudes_externas
Stores donation requests from other NGOs.

#### ofertas_externas
Stores donation offers from other NGOs.

#### eventos_externos
Stores external events from other NGOs.

## Migration Instructions

### Using Docker Compose
The database will be automatically initialized when using Docker Compose:

```bash
docker-compose up -d mysql
```

### Manual Migration
To manually run the migration:

```bash
# Connect to MySQL
mysql -u root -p

# Run the complete migration
source database/migrate.sql
```

### Development Setup
For development with sample data:

```bash
# Run all initialization scripts in order
mysql -u root -p < database/init/00-create-database.sql
mysql -u root -p < database/init/01-create-tables.sql
mysql -u root -p < database/init/02-insert-sample-data.sql
```

## Default Credentials

The migration creates a default admin user:
- **Username**: admin
- **Email**: admin@empujecomunitario.org
- **Password**: admin123 (change immediately in production)
- **Role**: PRESIDENTE

## Schema Validation

All tables include:
- Primary keys with AUTO_INCREMENT
- Appropriate indexes for performance
- Foreign key constraints for data integrity
- Check constraints for data validation
- Audit fields (created_at, created_by, updated_at, updated_by)

## Requirements Mapping

This schema satisfies the following requirements:
- **2.1**: User management with roles and audit
- **4.1**: Donation inventory with categories and stock control
- **5.1**: Event management with participants
- **7.1**: Inter-NGO network tables for collaboration