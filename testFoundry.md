# Solución: Azure AI Foundry - Problema de Autenticación

## 🔍 Análisis de tu Código

### ✅ Lo que está CORRECTO en tu código:

```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import ListSortOrder

project = AIProjectClient(
    credential=DefaultAzureCredential(),
    endpoint="https://gf1aifoundry.services.ai.azure.com/api/projects/firstProject"
)

agent = project.agents.get_agent('asst_7gLtPFYs7Aes9B5J7eHloOHl')
```

**Estás usando el método correcto para Azure AI Foundry** ✅

---

## ⚠️ EL PROBLEMA: DefaultAzureCredential

Tu código usa `DefaultAzureCredential()` que intenta autenticarse con **Azure AD** (no con API Key).

### ¿Por qué puede fallar?

`DefaultAzureCredential()` busca credenciales en este orden:
1. Variables de entorno
2. Managed Identity
3. Azure CLI (lo que tienes)
4. Azure PowerShell
5. Interactive browser

**Si tu Azure CLI está autenticado PERO:**
- ❌ No tienes permisos suficientes en el proyecto
- ❌ La suscripción no es la correcta
- ❌ El rol asignado no es adecuado
- ❌ El token expiró

**Entonces la autenticación falla.**

---

## 🎯 SOLUCIONES (3 opciones)

### ✅ SOLUCIÓN 1: Usar API Key (Más Simple - RECOMENDADO)

En lugar de `DefaultAzureCredential()`, usa directamente el API Key del proyecto:

```python
# archivo: main.py
import os
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import ListSortOrder

load_dotenv()

# CAMBIO: Usar connection string o API key
project = AIProjectClient.from_connection_string(
    conn_str=os.getenv("AZURE_AI_PROJECT_CONNECTION_STRING")
)

# O alternativamente, si tienes API key separada:
# from azure.core.credentials import AzureKeyCredential
# project = AIProjectClient(
#     endpoint="https://gf1aifoundry.services.ai.azure.com/api/projects/firstProject",
#     credential=AzureKeyCredential(os.getenv("AZURE_AI_API_KEY"))
# )

agent = project.agents.get_agent('asst_7gLtPFYs7Aes9B5J7eHloOHl')

thread = project.agents.threads.create()
print(f"Created thread, ID: {thread.id}")

message = project.agents.messages.create(
    thread_id=thread.id,
    role="user",
    content="Hi hicros Agent"
)

run = project.agents.runs.create_and_process(
    thread_id=thread.id,
    agent_id=agent.id
)

if run.status == "failed":
    print(f"Run failed: {run.last_error}")
else:
    messages = project.agents.messages.list(
        thread_id=thread.id, 
        order=ListSortOrder.ASCENDING
    )
    
    for message in messages:
        if message.text_messages:
            print(f"{message.role}: {message.text_messages[-1].text.value}")
```

**Archivo `.env`:**
```env
AZURE_AI_PROJECT_CONNECTION_STRING=tu-connection-string-aqui
```

---

### ✅ SOLUCIÓN 2: Arreglar Azure CLI Authentication

Si prefieres seguir usando `DefaultAzureCredential()`, verifica:

#### Paso 1: Verificar autenticación de Azure CLI

```bash
# Ver cuenta actual
az account show

# Ver todas las suscripciones disponibles
az account list --output table

# Cambiar a la suscripción correcta
az account set --subscription "tu-subscription-id"

# Verificar que cambió
az account show
```

#### Paso 2: Verificar permisos en el proyecto

```bash
# Ver tus roles en el resource group
az role assignment list \
  --assignee $(az account show --query user.name -o tsv) \
  --resource-group tu-resource-group \
  --output table
```

**Roles necesarios:**
- `Cognitive Services User` (mínimo)
- `Cognitive Services Contributor` (recomendado)
- O `Contributor` en el resource group

#### Paso 3: Asignar rol si falta

```bash
# Obtener tu user principal name
USER_PRINCIPAL=$(az account show --query user.name -o tsv)

# Asignar rol
az role assignment create \
  --assignee $USER_PRINCIPAL \
  --role "Cognitive Services Contributor" \
  --scope "/subscriptions/TU-SUBSCRIPTION-ID/resourceGroups/TU-RG/providers/Microsoft.CognitiveServices/accounts/TU-RECURSO"
```

#### Paso 4: Refrescar token

```bash
# Cerrar sesión y volver a entrar
az logout
az login

# Refrescar token específicamente para Cognitive Services
az account get-access-token --resource https://cognitiveservices.azure.com
```

---

### ✅ SOLUCIÓN 3: Híbrido con fallback

Código robusto que intenta Azure AD primero, luego API Key:

```python
# main_robusto.py
import os
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ClientAuthenticationError

load_dotenv()

def crear_cliente_con_fallback():
    """Intenta Azure AD, si falla usa API Key"""
    
    endpoint = "https://gf1aifoundry.services.ai.azure.com/api/projects/firstProject"
    
    # Intento 1: Azure AD con DefaultAzureCredential
    try:
        print("🔐 Intentando autenticación con Azure AD (DefaultAzureCredential)...")
        credential = DefaultAzureCredential()
        project = AIProjectClient(
            credential=credential,
            endpoint=endpoint
        )
        
        # Test de conexión
        project.agents.list_agents(max_results=1)
        print("✅ Autenticación exitosa con Azure AD")
        return project
        
    except ClientAuthenticationError as e:
        print(f"⚠️ Azure AD falló: {e}")
        print("🔄 Intentando con API Key...")
        
    except Exception as e:
        print(f"⚠️ Error con Azure AD: {e}")
        print("🔄 Intentando con API Key...")
    
    # Intento 2: Connection String
    try:
        conn_str = os.getenv("AZURE_AI_PROJECT_CONNECTION_STRING")
        if conn_str:
            project = AIProjectClient.from_connection_string(conn_str=conn_str)
            print("✅ Autenticación exitosa con Connection String")
            return project
    except Exception as e:
        print(f"⚠️ Connection String falló: {e}")
    
    # Intento 3: API Key
    try:
        api_key = os.getenv("AZURE_AI_API_KEY")
        if api_key:
            credential = AzureKeyCredential(api_key)
            project = AIProjectClient(
                credential=credential,
                endpoint=endpoint
            )
            print("✅ Autenticación exitosa con API Key")
            return project
    except Exception as e:
        print(f"❌ API Key falló: {e}")
    
    raise Exception("❌ No se pudo autenticar con ningún método")

# Usar
try:
    project = crear_cliente_con_fallback()
    
    agent = project.agents.get_agent('asst_7gLtPFYs7Aes9B5J7eHloOHl')
    thread = project.agents.threads.create()
    
    message = project.agents.messages.create(
        thread_id=thread.id,
        role="user",
        content="Hi hicros Agent"
    )
    
    run = project.agents.runs.create_and_process(
        thread_id=thread.id,
        agent_id=agent.id
    )
    
    if run.status == "failed":
        print(f"❌ Run failed: {run.last_error}")
    else:
        messages = project.agents.messages.list(thread_id=thread.id)
        for msg in messages:
            if msg.text_messages:
                print(f"{msg.role}: {msg.text_messages[-1].text.value}")
                
except Exception as e:
    print(f"❌ Error: {e}")
```

---

## 🔑 Cómo Obtener tu Connection String

### Opción A: Desde el Portal de Azure AI Foundry

1. Ve a [ai.azure.com](https://ai.azure.com)
2. Selecciona tu proyecto **"firstProject"**
3. Click en **Settings** (⚙️) en el menú lateral
4. Ve a la sección **"Project connection string"**
5. Click en **"Copy"** para copiar el connection string completo

**El connection string se verá así:**
```
Endpoint=https://gf1aifoundry.services.ai.azure.com/api/projects/firstProject;SubscriptionId=xxx-xxx;ResourceGroup=tu-rg;ProjectName=firstProject
```

### Opción B: Desde Azure CLI

```bash
# Listar proyectos de AI Foundry
az ml workspace list --output table

# Obtener detalles del proyecto
az ml workspace show \
  --name firstProject \
  --resource-group tu-resource-group
```

---

## 🔧 Script de Diagnóstico

Ejecuta este script para diagnosticar tu problema:

```python
# diagnostico_foundry.py
import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.core.credentials import AzureKeyCredential

load_dotenv()

print("=" * 70)
print("DIAGNÓSTICO AZURE AI FOUNDRY")
print("=" * 70)

endpoint = "https://gf1aifoundry.services.ai.azure.com/api/projects/firstProject"

# Test 1: Azure CLI
print("\n1️⃣ VERIFICANDO AZURE CLI:")
try:
    import subprocess
    result = subprocess.run(
        ['az', 'account', 'show'],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print("   ✅ Azure CLI autenticado")
        import json
        account = json.loads(result.stdout)
        print(f"   Usuario: {account.get('user', {}).get('name', 'N/A')}")
        print(f"   Subscription: {account.get('name', 'N/A')}")
    else:
        print("   ❌ Azure CLI NO autenticado")
        print("   Ejecuta: az login")
except FileNotFoundError:
    print("   ❌ Azure CLI no instalado")
except Exception as e:
    print(f"   ⚠️ Error: {e}")

# Test 2: DefaultAzureCredential
print("\n2️⃣ PROBANDO DefaultAzureCredential:")
try:
    credential = DefaultAzureCredential()
    project = AIProjectClient(
        credential=credential,
        endpoint=endpoint
    )
    # Intentar una operación simple
    agents = project.agents.list_agents(max_results=1)
    print("   ✅ DefaultAzureCredential funciona correctamente")
except Exception as e:
    print(f"   ❌ DefaultAzureCredential falló:")
    print(f"   {str(e)[:200]}")
    
    # Análisis del error
    error_str = str(e).lower()
    if "authentication" in error_str or "unauthorized" in error_str:
        print("\n   💡 PROBLEMA: Falta autenticación o permisos")
        print("   SOLUCIONES:")
        print("   - Ejecuta: az login")
        print("   - Verifica que tienes rol 'Cognitive Services User' o superior")
        print("   - Usa API Key en lugar de Azure AD (ver Solución 1)")
    elif "not found" in error_str:
        print("\n   💡 PROBLEMA: Proyecto o recurso no encontrado")
        print("   SOLUCIONES:")
        print("   - Verifica que el endpoint es correcto")
        print("   - Verifica que el proyecto existe")

# Test 3: Variables de entorno
print("\n3️⃣ VERIFICANDO VARIABLES DE ENTORNO:")
conn_str = os.getenv("AZURE_AI_PROJECT_CONNECTION_STRING")
api_key = os.getenv("AZURE_AI_API_KEY")

if conn_str:
    print(f"   ✅ AZURE_AI_PROJECT_CONNECTION_STRING configurada")
    print(f"   Primeros caracteres: {conn_str[:50]}...")
else:
    print(f"   ❌ AZURE_AI_PROJECT_CONNECTION_STRING NO configurada")

if api_key:
    print(f"   ✅ AZURE_AI_API_KEY configurada")
    print(f"   Primeros caracteres: {api_key[:10]}...")
else:
    print(f"   ❌ AZURE_AI_API_KEY NO configurada")

# Test 4: Connection String
if conn_str:
    print("\n4️⃣ PROBANDO Connection String:")
    try:
        project = AIProjectClient.from_connection_string(conn_str=conn_str)
        agents = project.agents.list_agents(max_results=1)
        print("   ✅ Connection String funciona correctamente")
    except Exception as e:
        print(f"   ❌ Connection String falló:")
        print(f"   {str(e)[:200]}")

# Test 5: API Key
if api_key:
    print("\n5️⃣ PROBANDO API Key:")
    try:
        credential = AzureKeyCredential(api_key)
        project = AIProjectClient(
            credential=credential,
            endpoint=endpoint
        )
        agents = project.agents.list_agents(max_results=1)
        print("   ✅ API Key funciona correctamente")
    except Exception as e:
        print(f"   ❌ API Key falló:")
        print(f"   {str(e)[:200]}")

# Test 6: Verificar agente
print("\n6️⃣ VERIFICANDO AGENTE:")
agent_id = 'asst_7gLtPFYs7Aes9B5J7eHloOHl'
print(f"   Agent ID: {agent_id}")

# Intentar listar todos los agentes disponibles
try:
    # Usar el método que funcionó
    if conn_str:
        project = AIProjectClient.from_connection_string(conn_str=conn_str)
    else:
        credential = DefaultAzureCredential()
        project = AIProjectClient(credential=credential, endpoint=endpoint)
    
    print("\n   Agentes disponibles en el proyecto:")
    agents = project.agents.list_agents()
    for agent in agents:
        print(f"   - ID: {agent.id}")
        print(f"     Nombre: {agent.name if hasattr(agent, 'name') else 'N/A'}")
        print(f"     Modelo: {agent.model if hasattr(agent, 'model') else 'N/A'}")
        if agent.id == agent_id:
            print(f"     ✅ Este es tu agente!")
except Exception as e:
    print(f"   ⚠️ No se pudieron listar agentes: {e}")

print("\n" + "=" * 70)
print("RECOMENDACIÓN FINAL:")
print("=" * 70)

if conn_str:
    print("✅ Usa Connection String (ya lo tienes configurado)")
    print("   Cambia tu código para usar:")
    print("   project = AIProjectClient.from_connection_string(conn_str=...)")
elif api_key:
    print("✅ Usa API Key (ya lo tienes configurado)")
    print("   Cambia tu código para usar:")
    print("   project = AIProjectClient(credential=AzureKeyCredential(...), endpoint=...)")
else:
    print("⚠️ Configura Connection String o API Key")
    print("   1. Ve a ai.azure.com")
    print("   2. Selecciona tu proyecto 'firstProject'")
    print("   3. Settings → Connection String")
    print("   4. Copia y pega en tu archivo .env")
```

---

## 📋 Checklist de Solución

Sigue estos pasos en orden:

### ✅ Paso 1: Obtener Connection String
- [ ] Ir a [ai.azure.com](https://ai.azure.com)
- [ ] Seleccionar proyecto "firstProject"
- [ ] Settings → Connection String
- [ ] Copiar el connection string completo

### ✅ Paso 2: Configurar archivo .env
- [ ] Crear archivo `.env` en la raíz del proyecto
- [ ] Agregar: `AZURE_AI_PROJECT_CONNECTION_STRING=tu-connection-string`
- [ ] Guardar archivo

### ✅ Paso 3: Actualizar código
- [ ] Cambiar `DefaultAzureCredential()` por `from_connection_string()`
- [ ] Agregar `load_dotenv()` al inicio
- [ ] Verificar que importaste `python-dotenv`

### ✅ Paso 4: Ejecutar diagnóstico
- [ ] Ejecutar `python diagnostico_foundry.py`
- [ ] Verificar que connection string funciona
- [ ] Verificar que el agente existe

### ✅ Paso 5: Probar código actualizado
- [ ] Ejecutar tu código modificado
- [ ] Verificar que se crea el thread
- [ ] Verificar que obtienes respuesta del agente

---

## 📁 Estructura Final de Archivos

```
tu-proyecto/
├── .env                    # Variables secretas (NO subir a git)
├── .gitignore             # Incluir .env aquí
├── requirements.txt       # Dependencias
├── main.py               # Tu código principal
└── diagnostico_foundry.py # Script de diagnóstico
```

**`.env`:**
```env
AZURE_AI_PROJECT_CONNECTION_STRING=Endpoint=https://gf1aifoundry.services.ai.azure.com/api/projects/firstProject;SubscriptionId=xxx;ResourceGroup=xxx;ProjectName=firstProject
```

**`.gitignore`:**
```
.env
__pycache__/
*.pyc
```

**`requirements.txt`:**
```txt
azure-ai-projects
azure-identity
python-dotenv
```

---

## 🚀 Código Final Recomendado

```python
# main.py - VERSIÓN FINAL RECOMENDADA
import os
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import ListSortOrder

# Cargar variables de entorno
load_dotenv()

def main():
    # Crear cliente con connection string (MÁS SIMPLE Y CONFIABLE)
    project = AIProjectClient.from_connection_string(
        conn_str=os.getenv("AZURE_AI_PROJECT_CONNECTION_STRING")
    )
    
    # Obtener el agente
    agent_id = 'asst_7gLtPFYs7Aes9B5J7eHloOHl'
    agent = project.agents.get_agent(agent_id)
    print(f"✅ Agente obtenido: {agent.id}")
    
    # Crear thread
    thread = project.agents.threads.create()
    print(f"✅ Thread creado: {thread.id}")
    
    # Enviar mensaje
    message = project.agents.messages.create(
        thread_id=thread.id,
        role="user",
        content="Hi hicros Agent"
    )
    print(f"✅ Mensaje enviado")
    
    # Ejecutar agente
    run = project.agents.runs.create_and_process(
        thread_id=thread.id,
        agent_id=agent.id
    )
    
    # Verificar resultado
    if run.status == "failed":
        print(f"❌ Ejecución falló: {run.last_error}")
    elif run.status == "completed":
        print(f"✅ Ejecución completada")
        
        # Obtener mensajes
        messages = project.agents.messages.list(
            thread_id=thread.id,
            order=ListSortOrder.ASCENDING
        )
        
        # Mostrar conversación
        print("\n📝 CONVERSACIÓN:")
        print("-" * 50)
        for msg in messages:
            if msg.text_messages:
                content = msg.text_messages[-1].text.value
                print(f"{msg.role.upper()}: {content}")
                print("-" * 50)
    else:
        print(f"⚠️ Estado: {run.status}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Ejecuta 'python diagnostico_foundry.py' para más información")
```

---

## ✨ Resumen Ejecutivo

### 🎯 TU PROBLEMA:
Usas `DefaultAzureCredential()` que depende de Azure CLI, pero puede tener problemas de permisos o autenticación.

### 💡 SOLUCIÓN MÁS SIMPLE:
Cambia a usar **Connection String** en lugar de `DefaultAzureCredential()`:

**ANTES (tu código actual):**
```python
project = AIProjectClient(
    credential=DefaultAzureCredential(),
    endpoint="https://gf1aifoundry.services.ai.azure.com/api/projects/firstProject"
)
```

**DESPUÉS (código recomendado):**
```python
project = AIProjectClient.from_connection_string(
    conn_str=os.getenv("AZURE_AI_PROJECT_CONNECTION_STRING")
)
```

### 📝 PASOS SIGUIENTES:
1. Obtén tu connection string desde [ai.azure.com](https://ai.azure.com)
2. Agrégalo a tu archivo `.env`
3. Actualiza tu código con la versión recomendada
4. Ejecuta y listo ✅

---

**¿Necesitas ayuda con algún paso específico?** 🚀
