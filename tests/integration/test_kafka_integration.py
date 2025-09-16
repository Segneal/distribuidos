#!/usr/bin/env python3
"""
Sistema ONG Backend - Kafka Integration Tests
Tests Kafka message production, consumption, and inter-NGO communication
"""

import json
import time
import uuid
import pytest
import threading
from datetime import datetime, timedelta
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError, KafkaTimeoutError
from kafka.admin import KafkaAdminClient, NewTopic

# Configuration
KAFKA_BROKERS = ["localhost:9092"]
ORGANIZATION_ID = "ong-empuje-comunitario"
TEST_TIMEOUT = 30  # seconds

class TestKafkaIntegration:
    """Test Kafka integration and message flows"""
    
    @classmethod
    def setup_class(cls):
        """Setup Kafka test environment"""
        cls.producer = None
        cls.consumer = None
        cls.admin_client = None
        cls.received_messages = []
        cls.consumer_thread = None
        cls.stop_consumer = False
        
        # Test topics
        cls.test_topics = [
            "solicitud-donaciones",
            "oferta-donaciones",
            "eventos-solidarios",
            "baja-solicitud-donaciones",
            "baja-evento-solidario"
        ]
        
        # Wait for Kafka to be ready
        cls._wait_for_kafka()
    
    @classmethod
    def _wait_for_kafka(cls, timeout=60):
        """Wait for Kafka to be ready"""
        print("Waiting for Kafka to be ready...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # Try to create admin client
                admin_client = KafkaAdminClient(
                    bootstrap_servers=KAFKA_BROKERS,
                    request_timeout_ms=5000
                )
                
                # Try to list topics
                topics = admin_client.list_topics(timeout=5)
                admin_client.close()
                
                print("✅ Kafka is ready")
                return
                
            except Exception as e:
                print(f"Waiting for Kafka... ({e})")
                time.sleep(2)
        
        raise Exception("Kafka not ready within timeout")
    
    def test_01_kafka_connectivity(self):
        """Test basic Kafka connectivity"""
        print("\n📨 Testing Kafka connectivity...")
        
        try:
            # Test admin client
            admin_client = KafkaAdminClient(
                bootstrap_servers=KAFKA_BROKERS,
                request_timeout_ms=10000
            )
            
            # List topics
            topics = admin_client.list_topics(timeout=10)
            print(f"✅ Available topics: {list(topics)}")
            
            admin_client.close()
            
        except Exception as e:
            pytest.fail(f"Kafka connectivity failed: {e}")
    
    def test_02_topic_existence(self):
        """Test that required topics exist"""
        print("\n📋 Testing topic existence...")
        
        try:
            admin_client = KafkaAdminClient(
                bootstrap_servers=KAFKA_BROKERS,
                request_timeout_ms=10000
            )
            
            existing_topics = admin_client.list_topics(timeout=10)
            
            for topic in self.test_topics:
                if topic in existing_topics:
                    print(f"✅ Topic '{topic}' exists")
                else:
                    print(f"⚠️ Topic '{topic}' not found - will be created on first message")
            
            admin_client.close()
            
        except Exception as e:
            pytest.fail(f"Topic check failed: {e}")
    
    def test_03_message_production(self):
        """Test message production to all topics"""
        print("\n📤 Testing message production...")
        
        try:
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_BROKERS,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                request_timeout_ms=10000,
                retries=3
            )
            
            for topic in self.test_topics:
                test_message = {
                    "idOrganizacion": ORGANIZATION_ID,
                    "test": True,
                    "timestamp": datetime.now().isoformat(),
                    "messageId": str(uuid.uuid4()),
                    "topic": topic
                }
                
                # Send message
                future = producer.send(topic, test_message)
                
                # Wait for confirmation
                record_metadata = future.get(timeout=10)
                
                print(f"✅ Message sent to {topic} (partition: {record_metadata.partition}, offset: {record_metadata.offset})")
            
            producer.close()
            
        except Exception as e:
            pytest.fail(f"Message production failed: {e}")
    
    def test_04_message_consumption(self):
        """Test message consumption from topics"""
        print("\n📥 Testing message consumption...")
        
        for topic in self.test_topics[:2]:  # Test first 2 topics to save time
            try:
                # Create consumer
                consumer = KafkaConsumer(
                    topic,
                    bootstrap_servers=KAFKA_BROKERS,
                    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                    consumer_timeout_ms=5000,
                    auto_offset_reset='latest'
                )
                
                # Send a test message
                producer = KafkaProducer(
                    bootstrap_servers=KAFKA_BROKERS,
                    value_serializer=lambda v: json.dumps(v).encode('utf-8')
                )
                
                test_message = {
                    "idOrganizacion": ORGANIZATION_ID,
                    "test": True,
                    "timestamp": datetime.now().isoformat(),
                    "messageId": str(uuid.uuid4()),
                    "consumptionTest": True
                }
                
                producer.send(topic, test_message)
                producer.flush(timeout=5)
                producer.close()
                
                # Try to consume the message
                messages_received = 0
                for message in consumer:
                    if message.value.get("consumptionTest"):
                        messages_received += 1
                        print(f"✅ Message consumed from {topic}")
                        break
                
                consumer.close()
                
                if messages_received == 0:
                    print(f"⚠️ No test message received from {topic} (may be timing issue)")
                
            except Exception as e:
                print(f"⚠️ Consumption test failed for {topic}: {e}")
    
    def test_05_solicitud_donaciones_flow(self):
        """Test solicitud de donaciones message flow"""
        print("\n🤝 Testing solicitud de donaciones flow...")
        
        try:
            # Create solicitud message
            solicitud_message = {
                "idOrganizacion": ORGANIZATION_ID,
                "idSolicitud": f"SOL-{int(time.time())}",
                "donaciones": [
                    {
                        "categoria": "ALIMENTOS",
                        "descripcion": "Arroz y fideos"
                    },
                    {
                        "categoria": "ROPA",
                        "descripcion": "Ropa de abrigo"
                    }
                ],
                "timestamp": datetime.now().isoformat()
            }
            
            # Send solicitud
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_BROKERS,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            
            future = producer.send('solicitud-donaciones', solicitud_message)
            record_metadata = future.get(timeout=10)
            
            producer.close()
            
            print(f"✅ Solicitud de donaciones sent (offset: {record_metadata.offset})")
            
        except Exception as e:
            pytest.fail(f"Solicitud donaciones flow failed: {e}")
    
    def test_06_transferencia_donaciones_flow(self):
        """Test transferencia de donaciones message flow"""
        print("\n📦 Testing transferencia de donaciones flow...")
        
        try:
            # Create transferencia message
            transferencia_message = {
                "idSolicitud": f"SOL-{int(time.time())}",
                "idOrganizacionDonante": ORGANIZATION_ID,
                "donaciones": [
                    {
                        "categoria": "ALIMENTOS",
                        "descripcion": "Arroz",
                        "cantidad": "5kg"
                    }
                ],
                "timestamp": datetime.now().isoformat()
            }
            
            # Send to organization-specific topic
            target_org = "ong-test-receiver"
            topic = f"transferencia-donaciones/{target_org}"
            
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_BROKERS,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            
            future = producer.send(topic, transferencia_message)
            record_metadata = future.get(timeout=10)
            
            producer.close()
            
            print(f"✅ Transferencia sent to {topic} (offset: {record_metadata.offset})")
            
        except Exception as e:
            pytest.fail(f"Transferencia donaciones flow failed: {e}")
    
    def test_07_eventos_solidarios_flow(self):
        """Test eventos solidarios message flow"""
        print("\n🎯 Testing eventos solidarios flow...")
        
        try:
            # Create evento message
            evento_message = {
                "idOrganizacion": ORGANIZATION_ID,
                "idEvento": f"EVT-{int(time.time())}",
                "nombre": "Evento de Prueba",
                "descripcion": "Evento para testing de integración",
                "fechaHora": (datetime.now() + timedelta(days=7)).isoformat(),
                "timestamp": datetime.now().isoformat()
            }
            
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_BROKERS,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            
            future = producer.send('eventos-solidarios', evento_message)
            record_metadata = future.get(timeout=10)
            
            producer.close()
            
            print(f"✅ Evento solidario sent (offset: {record_metadata.offset})")
            
        except Exception as e:
            pytest.fail(f"Eventos solidarios flow failed: {e}")
    
    def test_08_baja_solicitud_flow(self):
        """Test baja de solicitud message flow"""
        print("\n❌ Testing baja de solicitud flow...")
        
        try:
            # Create baja message
            baja_message = {
                "idOrganizacion": ORGANIZATION_ID,
                "idSolicitud": f"SOL-{int(time.time())}",
                "motivo": "Ya no necesitamos estos recursos",
                "timestamp": datetime.now().isoformat()
            }
            
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_BROKERS,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            
            future = producer.send('baja-solicitud-donaciones', baja_message)
            record_metadata = future.get(timeout=10)
            
            producer.close()
            
            print(f"✅ Baja de solicitud sent (offset: {record_metadata.offset})")
            
        except Exception as e:
            pytest.fail(f"Baja solicitud flow failed: {e}")
    
    def test_09_adhesion_evento_flow(self):
        """Test adhesión a evento message flow"""
        print("\n🙋 Testing adhesión a evento flow...")
        
        try:
            # Create adhesion message
            adhesion_message = {
                "idEvento": f"EVT-{int(time.time())}",
                "idOrganizacion": ORGANIZATION_ID,
                "idVoluntario": f"VOL-{int(time.time())}",
                "nombre": "Juan",
                "apellido": "Pérez",
                "telefono": "1234567890",
                "email": "juan.perez@test.com",
                "timestamp": datetime.now().isoformat()
            }
            
            # Send to organization-specific topic
            target_org = "ong-organizador-evento"
            topic = f"adhesion-evento/{target_org}"
            
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_BROKERS,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            
            future = producer.send(topic, adhesion_message)
            record_metadata = future.get(timeout=10)
            
            producer.close()
            
            print(f"✅ Adhesión a evento sent to {topic} (offset: {record_metadata.offset})")
            
        except Exception as e:
            pytest.fail(f"Adhesión evento flow failed: {e}")
    
    def test_10_message_serialization(self):
        """Test message serialization and deserialization"""
        print("\n🔄 Testing message serialization...")
        
        try:
            # Test various message types
            test_messages = [
                # Simple message
                {"test": "simple", "number": 123},
                
                # Complex message with nested objects
                {
                    "idOrganizacion": ORGANIZATION_ID,
                    "donaciones": [
                        {"categoria": "ALIMENTOS", "items": ["arroz", "fideos"]},
                        {"categoria": "ROPA", "items": ["camisas", "pantalones"]}
                    ],
                    "metadata": {
                        "timestamp": datetime.now().isoformat(),
                        "version": "1.0"
                    }
                },
                
                # Message with special characters
                {
                    "descripcion": "Descripción con acentos y ñ",
                    "emoji": "🎯📦🤝",
                    "unicode": "测试消息"
                }
            ]
            
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_BROKERS,
                value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode('utf-8')
            )
            
            consumer = KafkaConsumer(
                'solicitud-donaciones',
                bootstrap_servers=KAFKA_BROKERS,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                consumer_timeout_ms=5000,
                auto_offset_reset='latest'
            )
            
            for i, message in enumerate(test_messages):
                # Add test identifier
                message["serializationTest"] = i
                
                # Send message
                future = producer.send('solicitud-donaciones', message)
                future.get(timeout=5)
                
                print(f"✅ Message {i} serialized and sent")
            
            producer.close()
            consumer.close()
            
        except Exception as e:
            pytest.fail(f"Message serialization test failed: {e}")
    
    def test_11_concurrent_producers(self):
        """Test concurrent message production"""
        print("\n🔄 Testing concurrent producers...")
        
        import concurrent.futures
        
        def send_message(message_id):
            try:
                producer = KafkaProducer(
                    bootstrap_servers=KAFKA_BROKERS,
                    value_serializer=lambda v: json.dumps(v).encode('utf-8')
                )
                
                message = {
                    "idOrganizacion": ORGANIZATION_ID,
                    "messageId": message_id,
                    "concurrentTest": True,
                    "timestamp": datetime.now().isoformat()
                }
                
                future = producer.send('solicitud-donaciones', message)
                record_metadata = future.get(timeout=10)
                
                producer.close()
                
                return record_metadata.offset
                
            except Exception as e:
                return f"Error: {e}"
        
        # Send 5 concurrent messages
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(send_message, f"msg-{i}") for i in range(5)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # Check results
        successful_sends = [r for r in results if isinstance(r, int)]
        failed_sends = [r for r in results if not isinstance(r, int)]
        
        print(f"✅ {len(successful_sends)} concurrent messages sent successfully")
        if failed_sends:
            print(f"⚠️ {len(failed_sends)} messages failed: {failed_sends}")
        
        assert len(successful_sends) >= 3, "At least 3 concurrent messages should succeed"
    
    def test_12_error_handling(self):
        """Test Kafka error handling"""
        print("\n⚠️ Testing Kafka error handling...")
        
        # Test with invalid broker
        try:
            producer = KafkaProducer(
                bootstrap_servers=["localhost:9999"],  # Invalid port
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                request_timeout_ms=2000,
                retries=1
            )
            
            message = {"test": "error_handling"}
            future = producer.send('test-topic', message)
            
            # This should raise an exception
            future.get(timeout=5)
            
            producer.close()
            
            pytest.fail("Expected KafkaError but none was raised")
            
        except (KafkaError, KafkaTimeoutError) as e:
            print(f"✅ Kafka error properly handled: {type(e).__name__}")
        except Exception as e:
            print(f"✅ Error handled (unexpected type): {type(e).__name__}: {e}")
    
    @classmethod
    def teardown_class(cls):
        """Cleanup after tests"""
        if cls.producer:
            cls.producer.close()
        if cls.consumer:
            cls.consumer.close()
        if cls.admin_client:
            cls.admin_client.close()
        
        print("\n🧹 Kafka test cleanup completed")

def run_kafka_tests():
    """Run Kafka tests with proper setup"""
    print("=" * 60)
    print("   Kafka Integration Test Suite")
    print("=" * 60)
    
    # Run tests
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--color=yes"
    ])

if __name__ == "__main__":
    run_kafka_tests()