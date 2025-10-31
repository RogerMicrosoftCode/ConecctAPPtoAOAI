# solucion_final_apikey.py
"""
Script para diagnosticar y solucionar problemas con la API Key de Azure AI Foundry.
Ya confirmamos que API Keys están habilitadas, así que el problema es la configuración.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.core.credentials import AzureKeyCredential

print("="*70)
print("DIAGNÓSTICO COMPLETO - Azure AI Foundry API Key")
print("="*70)

# 1. Verificar que .env existe
print("\n1️⃣ VERIFICANDO ARCHIVO .ENV:")
env_file = Path('.env')
if env_file.exists():
    print(f"   ✅ Archivo .env encontrado en: {env_file.absolute()}")
    print(f"   Tamaño: {env_file.stat().st_size} bytes")
    
    # Leer contenido (para debug)
    with open(env_file, 'r') as f:
        lines = f.readlines()
    print(f"   Número de líneas: {len(lines)}")
else:
    print(f"   ❌ Archivo .env NO EXISTE")
    print(f"   Debe estar en: {Path('.').absolute()}")
    print("\n   SOLUCIÓN:")
    print("   1. Crea un archivo llamado '.env' en este directorio")
    print("   2. Agrega las siguientes líneas:")
    print("      AZURE_AI_PROJECT_ENDPOINT=https://gfaifoundry.services.ai.azure.com/api/projects/firstPro")
    print("      AZURE_AI_API_KEY=tu-api-key-aqui")
    print("      AGENT_ID=asst_7gLtPFYs7Aes9B5J7eHloOHl")
    exit(1)

# 2. Cargar variables de entorno
print("\n2️⃣ CARGANDO VARIABLES DE ENTORNO:")
load_dotenv(override=True)  # override=True para forzar recarga

# 3. Verificar cada variable
print("\n3️⃣ VERIFICANDO VARIABLES CARGADAS:")

endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
api_key = os.getenv("AZURE_AI_API_KEY")
agent_id = os.getenv("AGENT_ID")

# Verificar endpoint
print("\n   📍 AZURE_AI_PROJECT_ENDPOINT:")
if endpoint:
    print(f"      ✅ Configurado: {endpoint}")
    if endpoint != "https://gfaifoundry.services.ai.azure.com/api/projects/firstPro":
        print(f"      ⚠️ ADVERTENCIA: No coincide con el esperado")
        print(f"      Esperado: https://gfaifoundry.services.ai.azure.com/api/projects/firstPro")
else:
    print(f"      ❌ NO CONFIGURADO")

# Verificar API Key
print("\n   🔑 AZURE_AI_API_KEY:")
if api_key:
    print(f"      ✅ Configurada")
    print(f"      Longitud: {len(api_key)} caracteres")
    print(f"      Primeros 15 caracteres: {api_key[:15]}...")
    print(f"      Últimos 10 caracteres: ...{api_key[-10:]}")
    
    # Verificaciones de formato
    problemas = []
    
    if ' ' in api_key:
        problemas.append("Contiene ESPACIOS")
    if '\n' in api_key or '\r' in api_key:
        problemas.append("Contiene SALTOS DE LÍNEA")
    if api_key.startswith('"') or api_key.startswith("'"):
        problemas.append("Comienza con COMILLAS")
    if api_key.endswith('"') or api_key.endswith("'"):
        problemas.append("Termina con COMILLAS")
    if len(api_key) < 20:
        problemas.append("Demasiado CORTA (probablemente incompleta)")
    
    if problemas:
        print(f"\n      🔴 PROBLEMAS DETECTADOS:")
        for problema in problemas:
            print(f"         ❌ {problema}")
        print(f"\n      SOLUCIÓN:")
        print(f"      1. Abre el archivo .env")
        print(f"      2. En la línea de AZURE_AI_API_KEY:")
        print(f"         - NO debe haber espacios alrededor del =")
        print(f"         - NO debe haber comillas")
        print(f"         - La key debe estar en UNA sola línea")
        print(f"      3. Formato correcto:")
        print(f"         AZURE_AI_API_KEY=abc123def456ghi789...")
else:
    print(f"      ❌ NO CONFIGURADA")
    print(f"\n      SOLUCIÓN:")
    print(f"      1. Ve a: https://ai.azure.com")
    print(f"      2. Selecciona proyecto 'firstProject'")
    print(f"      3. Settings → Endpoints and keys")
    print(f"      4. Click en el ícono del ojo para revelar la API Key")
    print(f"      5. Copia TODA la key y pégala en el .env")

# Verificar Agent ID
print("\n   🤖 AGENT_ID:")
if agent_id:
    print(f"      ✅ Configurado: {agent_id}")
    if agent_id != "asst_7gLtPFYs7Aes9B5J7eHloOHl":
        print(f"      ⚠️ ADVERTENCIA: No coincide con el esperado")
else:
    print(f"      ❌ NO CONFIGURADO")

# 4. Test de conexión
print("\n4️⃣ TEST DE CONEXIÓN:")

if not all([endpoint, api_key, agent_id]):
    print("   ❌ No se puede probar conexión - faltan variables")
    print("\n" + "="*70)
    print("CONFIGURACIÓN INCOMPLETA")
    print("="*70)
    exit(1)

try:
    print(f"   Intentando conectar al endpoint...")
    
    credential = AzureKeyCredential(api_key)
    project = AIProjectClient(
        endpoint=endpoint,
        credential=credential
    )
    
    print(f"   Cliente creado, probando operación...")
    
    # Test: listar agentes
    agents = project.agents.list_agents(max_results=1)
    
    print(f"\n   ✅✅✅ CONEXIÓN EXITOSA ✅✅✅")
    print(f"\n   Tu configuración funciona correctamente!")
    
    # Test: obtener el agente específico
    print(f"\n5️⃣ VERIFICANDO TU AGENTE:")
    try:
        agent = project.agents.get_agent(agent_id)
        print(f"   ✅ Agente obtenido exitosamente")
        print(f"   ID: {agent.id}")
        if hasattr(agent, 'name'):
            print(f"   Nombre: {agent.name}")
        if hasattr(agent, 'model'):
            print(f"   Modelo: {agent.model}")
    except Exception as e:
        print(f"   ❌ Error al obtener el agente: {str(e)[:100]}")
        print(f"\n   Listando agentes disponibles:")
        all_agents = project.agents.list_agents()
        for ag in all_agents:
            print(f"      - {ag.id}")
    
    print("\n" + "="*70)
    print("✅✅✅ TODO CONFIGURADO CORRECTAMENTE ✅✅✅")
    print("="*70)
    print("\nAhora ejecuta tu código: python new_test.py")
    
except Exception as e:
    print(f"\n   ❌ ERROR AL CONECTAR:")
    error_msg = str(e)
    print(f"   {error_msg[:300]}")
    
    print(f"\n💡 DIAGNÓSTICO DEL ERROR:")
    error_lower = error_msg.lower()
    
    if "401" in error_msg or "unauthorized" in error_lower or "authentication" in error_lower:
        print(f"\n   PROBLEMA: API Key inválida o incorrecta")
        print(f"\n   SOLUCIONES POSIBLES:")
        print(f"   1. La API Key en el .env está MAL COPIADA")
        print(f"      - Ve a https://ai.azure.com")
        print(f"      - firstProject → Settings → Endpoints and keys")
        print(f"      - Click en el ojo 👁️ para revelar la key")
        print(f"      - Selecciona TODO y copia")
        print(f"      - Pégala en el .env (reemplazando la actual)")
        print(f"\n   2. La API Key está EXPIRADA o fue REGENERADA")
        print(f"      - En el portal, regenera la key")
        print(f"      - Copia la nueva key al .env")
        print(f"\n   3. Verifica el ENDPOINT")
        print(f"      - Endpoint actual en .env: {endpoint}")
        print(f"      - Debe ser: https://gfaifoundry.services.ai.azure.com/api/projects/firstPro")
        
    elif "404" in error_msg or "not found" in error_lower:
        print(f"\n   PROBLEMA: Endpoint o recurso no encontrado")
        print(f"\n   SOLUCIONES:")
        print(f"   1. Verifica el endpoint en el .env")
        print(f"   2. Verifica que el proyecto 'firstPro' existe")
        
    elif "timeout" in error_lower or "connection" in error_lower:
        print(f"\n   PROBLEMA: Error de red")
        print(f"\n   SOLUCIONES:")
        print(f"   1. Verifica tu conexión a internet")
        print(f"   2. Desactiva VPN temporalmente")
        print(f"   3. Verifica firewall")
    
    else:
        print(f"\n   PROBLEMA: Error desconocido")
        print(f"\n   SOLUCIONES:")
        print(f"   1. Regenera la API Key en el portal")
        print(f"   2. Verifica todas las variables en el .env")
    
    print("\n" + "="*70)
    print("CONFIGURACIÓN CON ERRORES")
    print("="*70)
