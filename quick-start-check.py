#!/usr/bin/env python3
"""
Quick Start Verification Script
Verifica que todo esté funcionando correctamente para un nuevo usuario
"""
import requests
import subprocess
import sys
import time
import json

def print_header(text):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def print_step(step, text):
    """Print a formatted step"""
    print(f"\n{step}. {text}")

def check_docker():
    """Verify Docker is running"""
    print_step("1", "🐳 Verificando Docker...")
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   ✅ Docker instalado: {result.stdout.strip()}")
        else:
            print("   ❌ Docker no está instalado")
            return False
            
        # Check if Docker is running
        result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
        if result.returncode == 0:
            print("   ✅ Docker está corriendo")
            return True
        else:
            print("   ❌ Docker no está corriendo. Inicia Docker Desktop.")
            return False
    except FileNotFoundError:
        print("   ❌ Docker no está instalado")
        return False

def check_docker_compose():
    """Verify Docker Compose is available"""
    print_step("2", "🔧 Verificando Docker Compose...")
    try:
        result = subprocess.run(['docker-compose', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   ✅ Docker Compose disponible: {result.stdout.strip()}")
            return True
        else:
            print("   ❌ Docker Compose no está disponible")
            return False
    except FileNotFoundError:
        print("   ❌ Docker Compose no está instalado")
        return False

def check_containers():
    """Check if containers are running"""
    print_step("3", "📦 Verificando contenedores...")
    try:
        result = subprocess.run(['docker-compose', 'ps'], capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:  # Header + at least one container
                print("   ✅ Contenedores encontrados:")
                for line in lines[1:]:  # Skip header
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 2:
                            name = parts[0]
                            status = ' '.join(parts[4:]) if len(parts) > 4 else 'Unknown'
                            if 'Up' in status:
                                print(f"      ✅ {name}: {status}")
                            else:
                                print(f"      ❌ {name}: {status}")
                return True
            else:
                print("   ⚠️  No se encontraron contenedores corriendo")
                print("   💡 Ejecuta: scripts\\deploy.bat (Windows) o ./scripts/deploy.sh (Linux/Mac)")
                return False
        else:
            print("   ❌ Error al verificar contenedores")
            return False
    except FileNotFoundError:
        print("   ❌ docker-compose no está disponible")
        return False

def check_api_gateway():
    """Check if API Gateway is responding"""
    print_step("4", "🌐 Verificando API Gateway...")
    try:
        response = requests.get('http://localhost:3000/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ API Gateway funcionando")
            print(f"      Status: {data.get('status', 'Unknown')}")
            print(f"      Service: {data.get('service', 'Unknown')}")
            return True
        else:
            print(f"   ❌ API Gateway respondió con código: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("   ❌ No se puede conectar al API Gateway")
        print("   💡 Verifica que el contenedor api-gateway esté corriendo")
        return False
    except requests.exceptions.Timeout:
        print("   ⏰ Timeout al conectar con API Gateway")
        return False
    except Exception as e:
        print(f"   ❌ Error inesperado: {e}")
        return False

def check_swagger_docs():
    """Check if Swagger documentation is available"""
    print_step("5", "📚 Verificando documentación...")
    try:
        response = requests.get('http://localhost:3000/api-docs', timeout=5)
        if response.status_code == 200:
            print("   ✅ Documentación Swagger disponible")
            print("   🔗 http://localhost:3000/api-docs")
            return True
        else:
            print(f"   ❌ Documentación no disponible (código: {response.status_code})")
            return False
    except requests.exceptions.ConnectionError:
        print("   ❌ No se puede acceder a la documentación")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_login():
    """Test login with default credentials"""
    print_step("6", "🔐 Probando autenticación...")
    try:
        login_data = {
            "identificador": "admin@ong.com",
            "clave": "password123"
        }
        response = requests.post(
            'http://localhost:3000/api/auth/login',
            json=login_data,
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Login exitoso")
            print(f"      Usuario: {data.get('usuario', {}).get('email', 'Unknown')}")
            print(f"      Rol: {data.get('usuario', {}).get('rol', 'Unknown')}")
            return True
        else:
            print(f"   ❌ Login falló (código: {response.status_code})")
            if response.status_code == 401:
                print("   💡 Credenciales incorrectas o servicio de usuarios no disponible")
            return False
    except requests.exceptions.ConnectionError:
        print("   ❌ No se puede conectar para hacer login")
        return False
    except Exception as e:
        print(f"   ❌ Error en login: {e}")
        return False

def print_summary(checks_passed, total_checks):
    """Print final summary"""
    print_header("RESUMEN FINAL")
    
    percentage = (checks_passed / total_checks) * 100
    
    if checks_passed == total_checks:
        print("🎉 ¡PERFECTO! Todo está funcionando correctamente")
        print("\n✅ Tu sistema está listo para usar:")
        print("   🌐 API Principal: http://localhost:3000")
        print("   📚 Documentación: http://localhost:3000/api-docs")
        print("   🔐 Usuario: admin@ong.com")
        print("   🔑 Contraseña: password123")
        print("\n🚀 ¡Puedes empezar a desarrollar!")
        
    elif checks_passed >= total_checks * 0.8:
        print(f"⚠️  Sistema funcionando parcialmente ({checks_passed}/{total_checks} checks)")
        print("\n💡 Algunos servicios pueden necesitar más tiempo para iniciar")
        print("   Espera 1-2 minutos y vuelve a ejecutar este script")
        
    else:
        print(f"❌ Sistema con problemas ({checks_passed}/{total_checks} checks)")
        print("\n🔧 Pasos para solucionar:")
        print("   1. Verifica que Docker Desktop esté corriendo")
        print("   2. Ejecuta: docker-compose down -v")
        print("   3. Ejecuta: scripts\\deploy.bat (Windows) o ./scripts/deploy.sh (Linux/Mac)")
        print("   4. Espera 2-3 minutos y vuelve a probar")

def main():
    """Main function"""
    print_header("🚀 VERIFICACIÓN RÁPIDA - SISTEMA ONG BACKEND")
    print("Este script verifica que todo esté funcionando correctamente")
    
    checks = [
        ("Docker", check_docker),
        ("Docker Compose", check_docker_compose),
        ("Contenedores", check_containers),
        ("API Gateway", check_api_gateway),
        ("Documentación", check_swagger_docs),
        ("Autenticación", test_login)
    ]
    
    checks_passed = 0
    total_checks = len(checks)
    
    for name, check_func in checks:
        if check_func():
            checks_passed += 1
        else:
            # If a critical check fails, we might want to stop
            if name in ["Docker", "Docker Compose"]:
                print(f"\n❌ {name} es requerido para continuar")
                break
    
    print_summary(checks_passed, total_checks)
    
    return 0 if checks_passed == total_checks else 1

if __name__ == '__main__':
    sys.exit(main())