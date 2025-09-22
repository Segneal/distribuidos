#!/usr/bin/env python3
"""
Example Usage of Kafka Test Generator
Sistema ONG - SQL Driven Testing

This example demonstrates how to use the KafkaTestGenerator to create
inter-NGO communication test scenarios from extracted SQL data.
"""

import json
import os
from datetime import datetime, timedelta
from kafka_generator import KafkaTestGenerator

def create_sample_data():
    """Create sample data structure for demonstration"""
    return {
        'users': {
            'PRESIDENTE': [
                {
                    'id': 1, 'nombre_usuario': 'test_presidente', 'nombre': 'Juan', 'apellido': 'Presidente',
                    'email': 'presidente@test.com', 'telefono': '1111111111', 'rol': 'PRESIDENTE'
                }
            ],
            'VOCAL': [
                {
                    'id': 2, 'nombre_usuario': 'test_vocal', 'nombre': 'María', 'apellido': 'Vocal',
                    'email': 'vocal@test.com', 'telefono': '2222222222', 'rol': 'VOCAL'
                }
            ],
            'COORDINADOR': [
                {
                    'id': 3, 'nombre_usuario': 'test_coordinador', 'nombre': 'Carlos', 'apellido': 'Coordinador',
                    'email': 'coordinador@test.com', 'telefono': '3333333333', 'rol': 'COORDINADOR'
                }
            ],
            'VOLUNTARIO': [
                {
                    'id': 4, 'nombre_usuario': 'test_voluntario', 'nombre': 'Ana', 'apellido': 'Voluntario',
                    'email': 'voluntario@test.com', 'telefono': '4444444444', 'rol': 'VOLUNTARIO'
                }
            ]
        },
        'inventory': {
            'ALIMENTOS': {
                'high_stock': [
                    {'id': 101, 'categoria': 'ALIMENTOS', 'descripcion': 'Arroz 1kg - Stock Alto', 'cantidad': 100},
                    {'id': 105, 'categoria': 'ALIMENTOS', 'descripcion': 'Leche 1L - Para Transferencia', 'cantidad': 25}
                ],
                'medium_stock': [
                    {'id': 102, 'categoria': 'ALIMENTOS', 'descripcion': 'Fideos 500g', 'cantidad': 30}
                ],
                'low_stock': [
                    {'id': 103, 'categoria': 'ALIMENTOS', 'descripcion': 'Conservas', 'cantidad': 5}
                ],
                'zero_stock': [
                    {'id': 104, 'categoria': 'ALIMENTOS', 'descripcion': 'Cuadernos - Stock Cero', 'cantidad': 0}
                ],
                'all': [
                    {'id': 101, 'categoria': 'ALIMENTOS', 'descripcion': 'Arroz 1kg - Stock Alto', 'cantidad': 100},
                    {'id': 102, 'categoria': 'ALIMENTOS', 'descripcion': 'Fideos 500g', 'cantidad': 30},
                    {'id': 103, 'categoria': 'ALIMENTOS', 'descripcion': 'Conservas', 'cantidad': 5},
                    {'id': 104, 'categoria': 'ALIMENTOS', 'descripcion': 'Cuadernos - Stock Cero', 'cantidad': 0},
                    {'id': 105, 'categoria': 'ALIMENTOS', 'descripcion': 'Leche 1L - Para Transferencia', 'cantidad': 25}
                ]
            },
            'ROPA': {
                'high_stock': [
                    {'id': 106, 'categoria': 'ROPA', 'descripcion': 'Camisetas M', 'cantidad': 50}
                ],
                'medium_stock': [],
                'low_stock': [],
                'zero_stock': [],
                'all': [
                    {'id': 106, 'categoria': 'ROPA', 'descripcion': 'Camisetas M', 'cantidad': 50}
                ]
            }
        },
        'events': {
            'future': [
                {
                    'id': 201, 'nombre': 'Evento Test Futuro 1', 'descripcion': 'Evento para testing de participación',
                    'fecha_hora': (datetime.now() + timedelta(days=7)).isoformat(), 'participantes': [3, 4]
                },
                {
                    'id': 202, 'nombre': 'Evento Test Futuro 2', 'descripcion': 'Evento para testing de adhesión externa',
                    'fecha_hora': (datetime.now() + timedelta(days=14)).isoformat(), 'participantes': [4]
                }
            ],
            'past': [
                {
                    'id': 203, 'nombre': 'Evento Test Pasado', 'descripcion': 'Evento pasado para testing',
                    'fecha_hora': (datetime.now() - timedelta(days=7)).isoformat(), 'participantes': [4]
                }
            ],
            'current': [],
            'all': []
        },
        'network': {
            'external_requests': [
                {
                    'id_organizacion': 'ong-corazon-solidario', 'id_solicitud': 'sol-001',
                    'categoria': 'ALIMENTOS', 'descripcion': 'Arroz y fideos para familias necesitadas',
                    'activa': True, 'fecha_recepcion': datetime.now().isoformat()
                },
                {
                    'id_organizacion': 'ong-manos-unidas', 'id_solicitud': 'sol-002',
                    'categoria': 'ROPA', 'descripcion': 'Ropa de invierno para adultos',
                    'activa': True, 'fecha_recepcion': datetime.now().isoformat()
                }
            ],
            'external_offers': [
                {
                    'id_organizacion': 'ong-corazon-solidario', 'id_oferta': 'of-001',
                    'categoria': 'UTILES_ESCOLARES', 'descripcion': 'Útiles escolares variados',
                    'cantidad': 50, 'fecha_recepcion': datetime.now().isoformat()
                }
            ],
            'external_events': [
                {
                    'id_organizacion': 'ong-corazon-solidario', 'id_evento': 'ev-ext-001',
                    'nombre': 'Campaña de Invierno 2024', 'descripcion': 'Distribución de ropa de invierno',
                    'fecha_hora': (datetime.now() + timedelta(days=10)).isoformat(),
                    'activo': True, 'fecha_recepcion': datetime.now().isoformat()
                }
            ],
            'own_requests': [
                {
                    'id_solicitud': 'req-001', 'donaciones': [{'categoria': 'ALIMENTOS', 'descripcion': 'Arroz'}],
                    'usuario_creador': 'test_vocal', 'fecha_creacion': datetime.now().isoformat(),
                    'activa': True, 'fecha_baja': None, 'usuario_baja': None
                }
            ],
            'own_offers': [],
            'transfers_sent': [],
            'transfers_received': [],
            'event_adhesions': []
        }
    }

def main():
    """Main example function"""
    print("=== Kafka Test Generator Example ===\n")
    
    # 1. Create sample data (normally this would come from SQLDataExtractor)
    print("1. Creating sample data structure...")
    sample_data = create_sample_data()
    print(f"   - Users: {sum(len(users) for users in sample_data['users'].values())} across {len(sample_data['users'])} roles")
    print(f"   - Inventory: {len(sample_data['inventory'])} categories")
    print(f"   - Events: {len(sample_data['events']['future'])} future, {len(sample_data['events']['past'])} past")
    print(f"   - Network: {len(sample_data['network']['external_requests'])} external requests")
    
    # 2. Initialize Kafka generator
    print("\n2. Initializing Kafka Test Generator...")
    generator = KafkaTestGenerator(sample_data)
    print(f"   - Organization ID: {generator.organization_id}")
    print(f"   - Kafka topics configured: {len(generator.kafka_topics)}")
    
    # 3. Generate all scenarios
    print("\n3. Generating Kafka test scenarios...")
    scenarios = generator.generate_all_kafka_scenarios()
    
    total_scenarios = sum(len(topic_scenarios) for topic_scenarios in scenarios.values())
    print(f"   - Generated {total_scenarios} scenarios across {len(scenarios)} topics")
    
    # 4. Display scenario summary
    print("\n4. Scenario Summary by Topic:")
    for topic, topic_scenarios in scenarios.items():
        success_count = len([s for s in topic_scenarios if s.get('expected_external_response', True)])
        error_count = len(topic_scenarios) - success_count
        print(f"   - {topic}: {len(topic_scenarios)} scenarios ({success_count} success, {error_count} error)")
    
    # 5. Show example scenarios
    print("\n5. Example Scenarios:")
    
    # Show donation request example
    if 'solicitud_donaciones' in scenarios and scenarios['solicitud_donaciones']:
        scenario = scenarios['solicitud_donaciones'][0]
        print(f"\n   Donation Request Example:")
        print(f"   - Name: {scenario['scenario_name']}")
        print(f"   - Topic: {scenario['topic']}")
        print(f"   - Message Key: {scenario['message_key']}")
        print(f"   - Donations Requested: {len(scenario['message']['donaciones'])}")
        print(f"   - User: {scenario['message']['usuarioSolicitante']}")
        print(f"   - Pre-conditions: {len(scenario['pre_conditions'])}")
        print(f"   - Post-conditions: {len(scenario['post_conditions'])}")
    
    # Show transfer example
    if 'transferencia_donaciones' in scenarios and scenarios['transferencia_donaciones']:
        scenario = scenarios['transferencia_donaciones'][0]
        print(f"\n   Transfer Example:")
        print(f"   - Name: {scenario['scenario_name']}")
        print(f"   - Topic: {scenario['topic']}")
        print(f"   - Request ID: {scenario['message']['idSolicitud']}")
        print(f"   - Donations Transferred: {len(scenario['message']['donaciones'])}")
        print(f"   - Destination: {scenario['message']['organizacionDestino']}")
    
    # 6. Validate scenarios
    print("\n6. Validating scenarios...")
    errors = generator.validate_scenarios(scenarios)
    if errors:
        print(f"   - Found {len(errors)} validation errors:")
        for error in errors[:3]:  # Show first 3 errors
            print(f"     * {error}")
        if len(errors) > 3:
            print(f"     ... and {len(errors) - 3} more")
    else:
        print("   - All scenarios passed validation ✓")
    
    # 7. Generate summary
    print("\n7. Generating summary...")
    summary = generator.generate_kafka_test_summary(scenarios)
    print(f"   - Generation timestamp: {summary['generation_timestamp']}")
    print(f"   - Total scenarios: {summary['total_scenarios']}")
    print(f"   - Success scenarios: {summary['scenario_types']['success']}")
    print(f"   - Error scenarios: {summary['scenario_types']['error']}")
    
    # 8. Save scenarios to files
    print("\n8. Saving scenarios to files...")
    output_dir = generator.save_scenarios_to_files(scenarios, "example_kafka_output")
    print(f"   - Scenarios saved to: {output_dir}")
    
    # List generated files
    if os.path.exists(output_dir):
        files = [f for f in os.listdir(output_dir) if f.endswith('.json')]
        print(f"   - Generated files: {len(files)}")
        for file in files:
            filepath = os.path.join(output_dir, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"     * {file}: {data.get('total_scenarios', 0)} scenarios")
    
    print("\n=== Example completed successfully! ===")
    return scenarios

if __name__ == "__main__":
    scenarios = main()
    
    # Optional: Print one complete scenario for inspection
    print("\n=== Sample Complete Scenario ===")
    if scenarios and 'solicitud_donaciones' in scenarios:
        sample_scenario = scenarios['solicitud_donaciones'][0]
        print(json.dumps(sample_scenario, indent=2, ensure_ascii=False))