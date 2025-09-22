#!/usr/bin/env python3
"""
Script principal para generar configuraciones de testing desde datos SQL centralizados.

Este script coordina la extracción de datos desde la base de datos poblada por SQL
y genera automáticamente configuraciones de Postman, Swagger y Kafka testing.

Usage:
    python scripts/generate-testing-configs.py --all
    python scripts/generate-testing-configs.py --postman --swagger
    python scripts/generate-testing-configs.py --kafka --validate
    python scripts/generate-testing-configs.py --restore-backup 2024-01-15_10-30-00
"""

import argparse
import sys
import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Agregar el directorio de scripts al path para importar módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'sql-driven-testing'))

from orchestrator import TestingOrchestrator
from data_extractor import SQLDataExtractor, DatabaseConfig


def setup_logging(verbose: bool = False) -> logging.Logger:
    """Configura el sistema de logging"""
    level = logging.DEBUG if verbose else logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('logs/generate-testing-configs.log', mode='a')
        ]
    )
    
    return logging.getLogger(__name__)


def create_logs_directory():
    """Crea el directorio de logs si no existe"""
    logs_dir = Path('logs')
    logs_dir.mkdir(exist_ok=True)


def validate_database_connection(config: Dict[str, Any]) -> bool:
    """Valida que se pueda conectar a la base de datos"""
    try:
        from data_extractor import DatabaseConfig
        # Filter database config to only include supported parameters
        db_params = {
            'host': config['database']['host'],
            'port': config['database']['port'],
            'database': config['database']['database'],
            'user': config['database']['user'],
            'password': config['database']['password']
        }
        db_config = DatabaseConfig(**db_params)
        extractor = SQLDataExtractor(db_config)
        return extractor.test_connection()
    except Exception as e:
        logging.error(f"Error conectando a la base de datos: {e}")
        return False


def load_configuration(config_file: Optional[str] = None) -> Dict[str, Any]:
    """Carga la configuración desde archivo"""
    if config_file is None:
        config_file = os.path.join(os.path.dirname(__file__), 'sql-driven-testing', 'config.json')
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # Configuración por defecto si no existe archivo
        return {
            "database": {
                "host": os.getenv("DB_HOST", "localhost"),
                "port": int(os.getenv("DB_PORT", "3306")),
                "user": os.getenv("DB_USER", "root"),
                "password": os.getenv("DB_PASSWORD", ""),
                "database": os.getenv("DB_NAME", "sistema_ong")
            },
            "backup": {
                "enabled": True,
                "retention_days": 30,
                "directory": "backups/testing-configs"
            },
            "validation": {
                "enabled": True,
                "strict_mode": False
            }
        }


def print_generation_report(report: Dict[str, Any]):
    """Imprime el reporte de generación de forma legible"""
    print("\n" + "="*60)
    print("REPORTE DE GENERACIÓN DE CONFIGURACIONES")
    print("="*60)
    
    print(f"Timestamp: {report['timestamp']}")
    print(f"Configuraciones generadas: {', '.join(report['generated_configs'])}")
    
    if 'postman_collections' in report:
        print(f"\nColecciones Postman actualizadas: {len(report['postman_collections'])}")
        for collection in report['postman_collections']:
            print(f"  - {collection}")
    
    if 'swagger_examples' in report:
        print(f"\nEjemplos Swagger actualizados: {len(report['swagger_examples'])}")
        for example in report['swagger_examples']:
            print(f"  - {example}")
    
    if 'kafka_scenarios' in report:
        print(f"\nEscenarios Kafka generados: {len(report['kafka_scenarios'])}")
        for scenario in report['kafka_scenarios']:
            print(f"  - {scenario}")
    
    print(f"\nTotal de casos de prueba: {report.get('total_test_cases', 'N/A')}")
    print(f"Estado de validación: {report.get('validation_status', 'N/A')}")
    
    if 'backup_location' in report:
        print(f"Backup creado en: {report['backup_location']}")
    
    print("="*60)


def list_available_backups(backup_dir: str) -> list:
    """Lista los backups disponibles"""
    backup_path = Path(backup_dir)
    if not backup_path.exists():
        return []
    
    backups = []
    for backup_folder in backup_path.iterdir():
        if backup_folder.is_dir() and backup_folder.name.startswith('backup_'):
            timestamp = backup_folder.name.replace('backup_', '')
            backups.append({
                'timestamp': timestamp,
                'path': str(backup_folder),
                'size': sum(f.stat().st_size for f in backup_folder.rglob('*') if f.is_file())
            })
    
    return sorted(backups, key=lambda x: x['timestamp'], reverse=True)


def restore_from_backup(backup_timestamp: str, config: Dict[str, Any]) -> bool:
    """Restaura configuraciones desde un backup específico"""
    backup_dir = config['backup']['directory']
    backup_path = Path(backup_dir) / f"backup_{backup_timestamp}"
    
    if not backup_path.exists():
        logging.error(f"Backup no encontrado: {backup_path}")
        return False
    
    try:
        orchestrator = TestingOrchestrator(config)
        success = orchestrator.restore_from_backup(str(backup_path))
        
        if success:
            logging.info(f"Configuraciones restauradas exitosamente desde {backup_timestamp}")
        else:
            logging.error("Error durante la restauración")
        
        return success
    
    except Exception as e:
        logging.error(f"Error restaurando backup: {e}")
        return False


def main():
    """Función principal del script"""
    parser = argparse.ArgumentParser(
        description="Genera configuraciones de testing desde datos SQL centralizados",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  %(prog)s --all                           # Genera todas las configuraciones
  %(prog)s --postman --swagger             # Solo Postman y Swagger
  %(prog)s --kafka --no-backup             # Solo Kafka sin backup
  %(prog)s --validate-only                 # Solo valida datos sin generar
  %(prog)s --list-backups                  # Lista backups disponibles
  %(prog)s --restore-backup 2024-01-15_10-30-00  # Restaura desde backup
        """
    )
    
    # Opciones de generación
    parser.add_argument('--all', action='store_true',
                       help='Genera todas las configuraciones (Postman, Swagger, Kafka)')
    parser.add_argument('--postman', action='store_true',
                       help='Genera colecciones Postman')
    parser.add_argument('--swagger', action='store_true',
                       help='Actualiza ejemplos Swagger')
    parser.add_argument('--kafka', action='store_true',
                       help='Genera escenarios Kafka inter-ONG')
    
    # Opciones de control
    parser.add_argument('--no-backup', action='store_true',
                       help='No crear backup antes de generar')
    parser.add_argument('--no-validate', action='store_true',
                       help='No validar datos extraídos')
    parser.add_argument('--validate-only', action='store_true',
                       help='Solo validar datos sin generar configuraciones')
    
    # Opciones de backup
    parser.add_argument('--list-backups', action='store_true',
                       help='Lista backups disponibles')
    parser.add_argument('--restore-backup', metavar='TIMESTAMP',
                       help='Restaura configuraciones desde backup específico')
    
    # Opciones de configuración
    parser.add_argument('--config', metavar='FILE',
                       help='Archivo de configuración personalizado')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Salida detallada')
    parser.add_argument('--dry-run', action='store_true',
                       help='Simula la ejecución sin hacer cambios')
    
    args = parser.parse_args()
    
    # Crear directorio de logs
    create_logs_directory()
    
    # Configurar logging
    logger = setup_logging(args.verbose)
    
    try:
        # Cargar configuración
        config = load_configuration(args.config)
        
        # Manejar comandos especiales
        if args.list_backups:
            backups = list_available_backups(config['backup']['directory'])
            if not backups:
                print("No hay backups disponibles")
                return 0
            
            print("Backups disponibles:")
            for backup in backups:
                size_mb = backup['size'] / (1024 * 1024)
                print(f"  {backup['timestamp']} ({size_mb:.1f} MB)")
            return 0
        
        if args.restore_backup:
            success = restore_from_backup(args.restore_backup, config)
            return 0 if success else 1
        
        # Validar conexión a base de datos (skip en dry-run)
        if not args.dry_run and not validate_database_connection(config):
            logger.error("No se puede conectar a la base de datos")
            return 1
        
        # Determinar qué generar
        generate_options = {
            'postman': args.all or args.postman,
            'swagger': args.all or args.swagger,
            'kafka': args.all or args.kafka,
            'backup': not args.no_backup,
            'validate': not args.no_validate
        }
        
        # Si no se especifica nada, generar todo
        if not any([args.all, args.postman, args.swagger, args.kafka, args.validate_only]):
            generate_options.update({'postman': True, 'swagger': True, 'kafka': True})
        
        # Crear orquestador
        orchestrator = TestingOrchestrator(args.config)
        
        if args.validate_only:
            logger.info("Validando datos extraídos únicamente")
            extracted_data = orchestrator.data_extractor.extract_test_data()
            orchestrator.validate_extracted_data(extracted_data)
            logger.info("Validación completada exitosamente")
            return 0
        
        if args.dry_run:
            logger.info("Modo dry-run: simulando generación")
            logger.info(f"Se generarían: {[k for k, v in generate_options.items() if v]}")
            return 0
        
        # Generar configuraciones
        logger.info("Iniciando generación de configuraciones de testing")
        report = orchestrator.generate_all_testing_configs(generate_options)
        
        # Mostrar reporte
        print_generation_report(report)
        
        # Guardar reporte en archivo
        report_file = f"logs/generation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Reporte guardado en: {report_file}")
        logger.info("Generación completada exitosamente")
        
        return 0
    
    except KeyboardInterrupt:
        logger.info("Operación cancelada por el usuario")
        return 1
    
    except Exception as e:
        logger.error(f"Error durante la ejecución: {e}")
        if args.verbose:
            import traceback
            logger.error(traceback.format_exc())
        return 1


if __name__ == '__main__':
    sys.exit(main())