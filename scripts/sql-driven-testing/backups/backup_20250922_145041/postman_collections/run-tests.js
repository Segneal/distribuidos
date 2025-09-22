#!/usr/bin/env node

/**
 * Script para ejecutar todas las colecciones de Postman del Sistema ONG
 * 
 * Uso:
 *   node run-tests.js [--collection=nombre] [--environment=env] [--verbose]
 * 
 * Ejemplos:
 *   node run-tests.js                                    # Ejecuta todas las colecciones
 *   node run-tests.js --collection=01-Autenticacion     # Ejecuta solo autenticación
 *   node run-tests.js --verbose                         # Salida detallada
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Configuración
const CONFIG = {
  baseUrl: 'http://localhost:3000',
  environment: 'Sistema-ONG-Environment.postman_environment.json',
  collections: [
    '01-Autenticacion.postman_collection.json',
    '02-Usuarios.postman_collection.json',
    '03-Inventario.postman_collection.json',
    '04-Eventos.postman_collection.json',
    '05-Red-ONGs.postman_collection.json'
  ],
  timeout: 30000,
  delay: 1000
};

// Parsear argumentos de línea de comandos
const args = process.argv.slice(2);
const options = {
  collection: null,
  environment: CONFIG.environment,
  verbose: false
};

args.forEach(arg => {
  if (arg.startsWith('--collection=')) {
    options.collection = arg.split('=')[1];
  } else if (arg.startsWith('--environment=')) {
    options.environment = arg.split('=')[1];
  } else if (arg === '--verbose') {
    options.verbose = true;
  }
});

// Función para verificar si Newman está instalado
function checkNewman() {
  try {
    execSync('newman --version', { stdio: 'pipe' });
    return true;
  } catch (error) {
    return false;
  }
}

// Función para instalar Newman
function installNewman() {
  console.log('📦 Instalando Newman...');
  try {
    execSync('npm install -g newman', { stdio: 'inherit' });
    console.log('✅ Newman instalado correctamente');
  } catch (error) {
    console.error('❌ Error instalando Newman:', error.message);
    process.exit(1);
  }
}

// Función para verificar si el servidor está corriendo
function checkServer() {
  console.log('🔍 Verificando servidor...');
  try {
    const { execSync } = require('child_process');
    execSync(`curl -f ${CONFIG.baseUrl}/health`, { stdio: 'pipe' });
    console.log('✅ Servidor disponible');
    return true;
  } catch (error) {
    console.log('⚠️  Servidor no disponible en', CONFIG.baseUrl);
    console.log('   Asegúrese de que el API Gateway esté corriendo');
    return false;
  }
}

// Función para ejecutar una colección
function runCollection(collectionFile, environmentFile) {
  const collectionPath = path.join(__dirname, collectionFile);
  const environmentPath = path.join(__dirname, environmentFile);
  
  if (!fs.existsSync(collectionPath)) {
    console.error(`❌ Colección no encontrada: ${collectionFile}`);
    return false;
  }
  
  if (!fs.existsSync(environmentPath)) {
    console.error(`❌ Environment no encontrado: ${environmentFile}`);
    return false;
  }
  
  console.log(`\n🧪 Ejecutando: ${collectionFile}`);
  console.log('─'.repeat(50));
  
  try {
    const cmd = [
      'newman run',
      `"${collectionPath}"`,
      `-e "${environmentPath}"`,
      `--timeout-request ${CONFIG.timeout}`,
      `--delay-request ${CONFIG.delay}`,
      '--color on',
      '--reporter cli,json',
      '--reporter-json-export results.json'
    ].join(' ');
    
    const output = execSync(cmd, { 
      stdio: options.verbose ? 'inherit' : 'pipe',
      encoding: 'utf8'
    });
    
    if (!options.verbose) {
      // Parsear resultados JSON para mostrar resumen
      if (fs.existsSync('results.json')) {
        const results = JSON.parse(fs.readFileSync('results.json', 'utf8'));
        const stats = results.run.stats;
        
        console.log(`✅ Tests: ${stats.tests.total}`);
        console.log(`✅ Passed: ${stats.tests.passed}`);
        if (stats.tests.failed > 0) {
          console.log(`❌ Failed: ${stats.tests.failed}`);
        }
        console.log(`📊 Assertions: ${stats.assertions.total} (${stats.assertions.passed} passed)`);
        
        // Limpiar archivo temporal
        fs.unlinkSync('results.json');
      }
    }
    
    return true;
  } catch (error) {
    console.error(`❌ Error ejecutando ${collectionFile}:`, error.message);
    return false;
  }
}

// Función principal
function main() {
  console.log('🚀 Sistema ONG - Test Runner');
  console.log('═'.repeat(50));
  
  // Verificar Newman
  if (!checkNewman()) {
    console.log('⚠️  Newman no está instalado');
    installNewman();
  }
  
  // Verificar servidor (opcional)
  checkServer();
  
  // Determinar qué colecciones ejecutar
  let collectionsToRun = CONFIG.collections;
  if (options.collection) {
    const collectionFile = options.collection.endsWith('.json') 
      ? options.collection 
      : `${options.collection}.postman_collection.json`;
    
    if (CONFIG.collections.includes(collectionFile)) {
      collectionsToRun = [collectionFile];
    } else {
      console.error(`❌ Colección no encontrada: ${options.collection}`);
      console.log('Colecciones disponibles:');
      CONFIG.collections.forEach(c => console.log(`  - ${c}`));
      process.exit(1);
    }
  }
  
  // Ejecutar colecciones
  let totalSuccess = 0;
  let totalFailed = 0;
  
  for (const collection of collectionsToRun) {
    const success = runCollection(collection, options.environment);
    if (success) {
      totalSuccess++;
    } else {
      totalFailed++;
    }
  }
  
  // Resumen final
  console.log('\n📊 Resumen Final');
  console.log('═'.repeat(50));
  console.log(`✅ Colecciones exitosas: ${totalSuccess}`);
  console.log(`❌ Colecciones fallidas: ${totalFailed}`);
  
  if (totalFailed > 0) {
    console.log('\n💡 Consejos para resolver errores:');
    console.log('  - Verifique que el servidor esté corriendo');
    console.log('  - Verifique que la base de datos esté disponible');
    console.log('  - Ejecute primero la colección de Autenticación');
    console.log('  - Revise los logs del servidor para más detalles');
    process.exit(1);
  } else {
    console.log('\n🎉 ¡Todos los tests pasaron correctamente!');
    process.exit(0);
  }
}

// Ejecutar si es llamado directamente
if (require.main === module) {
  main();
}

module.exports = { runCollection, checkNewman, checkServer };