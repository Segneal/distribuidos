#!/usr/bin/env python3
"""
Script to check the deployment status of all services
"""
import requests
import time
import sys

def check_service_health():
    """Check the health of all services"""
    services = {
        'API Gateway': 'http://localhost:3000/health',
        'User Service (via API Gateway)': 'http://localhost:3000/api/usuarios/health',
    }
    
    print("🔍 Verificando estado de los servicios...")
    print("=" * 50)
    
    all_healthy = True
    
    for service_name, url in services.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {service_name}: OK")
            else:
                print(f"❌ {service_name}: HTTP {response.status_code}")
                all_healthy = False
        except requests.exceptions.ConnectionError:
            print(f"🔄 {service_name}: No disponible (conexión rechazada)")
            all_healthy = False
        except requests.exceptions.Timeout:
            print(f"⏰ {service_name}: Timeout")
            all_healthy = False
        except Exception as e:
            print(f"❌ {service_name}: Error - {e}")
            all_healthy = False
    
    print("=" * 50)
    
    if all_healthy:
        print("🎉 ¡Todos los servicios están funcionando correctamente!")
        return True
    else:
        print("⚠️  Algunos servicios no están disponibles")
        return False

def main():
    """Main function"""
    print("🚀 Sistema ONG Backend - Verificación de Despliegue")
    print("=" * 60)
    
    # Wait a bit for services to start
    print("⏳ Esperando que los servicios se inicialicen...")
    time.sleep(5)
    
    success = check_service_health()
    
    if success:
        print("\n🎯 El sistema está listo para usar!")
        print("📖 Puedes acceder a la documentación en: http://localhost:3000/api-docs")
    else:
        print("\n🔧 Algunos servicios necesitan más tiempo o tienen problemas")
        print("💡 Ejecuta 'docker-compose logs <service-name>' para ver los detalles")
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())