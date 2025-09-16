#!/usr/bin/env python3
"""
Health check script for Sistema ONG Backend services
"""
import requests
import grpc
import sys
import time
from concurrent.futures import ThreadPoolExecutor

def check_api_gateway():
    """Check API Gateway health"""
    try:
        response = requests.get('http://localhost:3000/health', timeout=5)
        return response.status_code == 200
    except:
        return False

def check_grpc_service(host, port):
    """Check gRPC service health"""
    try:
        channel = grpc.insecure_channel(f'{host}:{port}')
        # Simple connection test
        grpc.channel_ready_future(channel).result(timeout=5)
        channel.close()
        return True
    except:
        return False

def check_mysql():
    """Check MySQL connection"""
    try:
        import mysql.connector
        conn = mysql.connector.connect(
            host='localhost',
            port=3308,
            user='ong_user',
            password='ong_password',
            database='ong_sistema'
        )
        conn.close()
        return True
    except:
        return False

def check_kafka():
    """Check Kafka connection"""
    try:
        from kafka import KafkaProducer
        producer = KafkaProducer(
            bootstrap_servers=['localhost:9092'],
            request_timeout_ms=5000
        )
        producer.close()
        return True
    except:
        return False

def main():
    """Main health check function"""
    print("🏥 Sistema ONG Backend - Health Check")
    print("=" * 50)
    
    services = [
        ("MySQL Database", check_mysql),
        ("Kafka Message Broker", check_kafka),
        ("User Service (gRPC)", lambda: check_grpc_service('localhost', 50051)),
        ("Inventory Service (gRPC)", lambda: check_grpc_service('localhost', 50052)),
        ("Events Service (gRPC)", lambda: check_grpc_service('localhost', 50053)),
        ("API Gateway (REST)", check_api_gateway),
    ]
    
    all_healthy = True
    
    for service_name, check_func in services:
        print(f"Checking {service_name}...", end=" ")
        if check_func():
            print("✅ HEALTHY")
        else:
            print("❌ UNHEALTHY")
            all_healthy = False
    
    print("=" * 50)
    if all_healthy:
        print("🎉 All services are healthy!")
        sys.exit(0)
    else:
        print("⚠️  Some services are unhealthy. Check logs for details.")
        sys.exit(1)

if __name__ == '__main__':
    main()