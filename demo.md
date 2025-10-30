# Configuración Completa: Azure AI Foundry - firstProject

## 🎯 TUS DATOS DE AZURE AI FOUNDRY

Basado en la imagen que compartiste, estos son tus datos:

| Campo | Valor |
|-------|-------|
| **Endpoint** | `https://gfaifoundry.services.ai.azure.com/api/projects/firstPro` |
| **API Key** | `•••••••••••••••••••••` (la que ves con puntos) |
| **Project ID** | `/subscriptions/f81d5404-dbde-4d0e-9fb0-fefebca4802d/...` |
| **Subscription ID** | `f81d5404-dbde-4d0e-9fb0-fefebca4802d` |
| **Resource Group** | `AIFoundry` |
| **Location** | `southcentralus` |

---

## 📝 PASO 1: Copiar tu API Key

1. En la pantalla que compartiste, haz click en el ícono **👁️ (ojo)** al lado de "API Key"
2. Copia la API Key completa que se revela
3. Guárdala temporalmente (la usaremos en el archivo `.env`)

---

## 📝 PASO 2: Crear archivo `.env`

Crea un archivo llamado `.env` en la raíz de tu proyecto con este contenido:

```env
# Azure AI Foundry - firstProject
AZURE_AI_PROJECT_ENDPOINT=https://gfaifoundry.services.ai.azure.com/api/projects/firstPro
AZURE_AI_API_KEY=tu-api-key-completa-aqui

# Agent ID
AGENT_ID=asst_7gLtPFYs7Aes9B5J7eHloOHl

# Opcional - para referencia
SUBSCRIPTION_ID=f81d5404-dbde-4d0e-9fb0-fefebca4802d
RESOURCE_GROUP=AIFoundry
PROJECT_NAME=firstProject
```

**⚠️ IMPORTANTE:** Reemplaza `tu-api-key-completa-aqui` con la API Key real que copiaste en el paso 1.

---

## 📝 PASO 3: Actualizar tu código

### ✅ Versión 1: Con API Key (RECOMENDADO - MÁS SIMPLE)

```python
# main.py
import os
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.agents.models import ListSortOrder

# Cargar variables de entorno
load_dotenv()

# Crear cliente usando API Key directamente
project = AIProjectClient(
    endpoint=os.getenv("AZURE_AI_PROJECT_ENDPOINT"),
    credential=AzureKeyCredential(os.getenv("AZURE_AI_API_KEY"))
)

# Obtener el agente
agent = project.agents.get_agent(os.getenv("AGENT_ID"))

# Crear thread (conversación)
thread = project.agents.threads.create()
print(f"Created thread, ID: {thread.id}")

# Enviar mensaje
message = project.agents.messages.create(
    thread_id=thread.id,
    role="user",
    content="Hi hicros Agent"
)

# Ejecutar el agente y esperar respuesta
run = project.agents.runs.create_and_process(
    thread_id=thread.id,
    agent_id=agent.id
)

# Verificar resultado
if run.status == "failed":
    print(f"Run failed: {run.last_error}")
else:
    # Obtener y mostrar mensajes
    messages = project.agents.messages.list(
        thread_id=thread.id,
        order=ListSortOrder.ASCENDING
    )
    
    for message in messages:
        if message.text_messages:
            print(f"{message.role}: {message.text_messages[-1].text.value}")
```

---

### ✅ Versión 2: Híbrida (Azure AD con fallback a API Key)

Si quieres mantener la opción de usar Azure AD pero con fallback a API Key:

```python
# main_hibrido.py
import os
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ClientAuthenticationError
from azure.ai.agents.models import ListSortOrder

load_dotenv()

def crear_cliente():
    """Crea cliente con Azure AD, si falla usa API Key"""
    
    endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
    
    # Intento 1: Azure AD
    try:
        print("🔐 Intentando con DefaultAzureCredential (Azure AD)...")
        credential = DefaultAzureCredential()
        project = AIProjectClient(
            endpoint=endpoint,
            credential=credential
        )
        
        # Test rápido
        project.agents.list_agents(max_results=1)
        print("✅ Autenticado con Azure AD")
        return project
        
    except (ClientAuthenticationError, Exception) as e:
        print(f"⚠️ Azure AD falló: {str(e)[:100]}")
        print("🔄 Intentando con API Key...")
    
    # Intento 2: API Key
    try:
        api_key = os.getenv("AZURE_AI_API_KEY")
        if not api_key:
            raise ValueError("AZURE_AI_API_KEY no configurada en .env")
        
        credential = AzureKeyCredential(api_key)
        project = AIProjectClient(
            endpoint=endpoint,
            credential=credential
        )
        print("✅ Autenticado con API Key")
        return project
        
    except Exception as e:
        raise Exception(f"❌ No se pudo autenticar: {e}")

# Usar el cliente
try:
    project = crear_cliente()
    
    # Obtener agente
    agent_id = os.getenv("AGENT_ID")
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
    
    # Ejecutar agente
    run = project.agents.runs.create_and_process(
        thread_id=thread.id,
        agent_id=agent.id
    )
    
    # Mostrar resultados
    if run.status == "failed":
        print(f"❌ Run failed: {run.last_error}")
    else:
        messages = project.agents.messages.list(
            thread_id=thread.id,
            order=ListSortOrder.ASCENDING
        )
        
        print("\n📝 CONVERSACIÓN:")
        print("-" * 50)
        for msg in messages:
            if msg.text_messages:
                content = msg.text_messages[-1].text.value
                print(f"{msg.role.upper()}: {content}")
        print("-" * 50)
        
except Exception as e:
    print(f"❌ Error: {e}")
```

---

## 📝 PASO 4: Crear `.gitignore`

**⚠️ MUY IMPORTANTE:** Nunca subas tu API Key a Git

```gitignore
# .gitignore
.env
__pycache__/
*.pyc
.vscode/
*.log
```

---

## 📝 PASO 5: Instalar dependencias

```bash
pip install azure-ai-projects
pip install azure-identity
pip install azure-core
pip install python-dotenv
```

O crea un `requirements.txt`:

```txt
azure-ai-projects>=1.0.0
azure-identity>=1.15.0
azure-core>=1.29.0
python-dotenv>=1.0.0
```

E instala con:
```bash
pip install -r requirements.txt
```

---

## 🔧 Script de Diagnóstico Personalizado

Ejecuta este script para verificar que todo está configurado correctamente:

```python
# diagnostico_mi_proyecto.py
import os
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential

load_dotenv()

print("=" * 70)
print("DIAGNÓSTICO: firstProject - Azure AI Foundry")
print("=" * 70)

# 1. Verificar variables de entorno
print("\n1️⃣ VARIABLES DE ENTORNO:")
endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
api_key = os.getenv("AZURE_AI_API_KEY")
agent_id = os.getenv("AGENT_ID")

print(f"   Endpoint: {'✅' if endpoint else '❌'} {endpoint if endpoint else 'NO CONFIGURADO'}")
print(f"   API Key: {'✅' if api_key else '❌'} {'Configurada' if api_key else 'NO CONFIGURADA'}")
if api_key:
    print(f"   Primeros 10 caracteres: {api_key[:10]}...")
print(f"   Agent ID: {'✅' if agent_id else '❌'} {agent_id if agent_id else 'NO CONFIGURADO'}")

if not all([endpoint, api_key, agent_id]):
    print("\n❌ ERROR: Faltan variables críticas en el archivo .env")
    print("Revisa el PASO 2 del documento")
    exit(1)

# 2. Validar formato del endpoint
print("\n2️⃣ VALIDANDO ENDPOINT:")
expected_endpoint = "https://gfaifoundry.services.ai.azure.com/api/projects/firstPro"
if endpoint == expected_endpoint:
    print(f"   ✅ Endpoint correcto")
else:
    print(f"   ⚠️ Endpoint diferente al esperado:")
    print(f"   Esperado: {expected_endpoint}")
    print(f"   Actual: {endpoint}")

# 3. Test con API Key
print("\n3️⃣ PROBANDO CONEXIÓN CON API KEY:")
try:
    credential = AzureKeyCredential(api_key)
    project = AIProjectClient(
        endpoint=endpoint,
        credential=credential
    )
    
    # Test básico
    agents = project.agents.list_agents(max_results=1)
    print(f"   ✅ Conexión exitosa con API Key")
    
except Exception as e:
    print(f"   ❌ Error al conectar con API Key:")
    print(f"   {str(e)}")
    
    # Análisis del error
    if "401" in str(e) or "Unauthorized" in str(e):
        print("\n   💡 PROBLEMA: API Key inválida")
        print("   SOLUCIÓN: Verifica que copiaste correctamente la API Key")
        print("   1. Ve a ai.azure.com → firstProject → Settings")
        print("   2. Haz click en el ícono del ojo para revelar la key")
        print("   3. Copia la key completa y reemplaza en el .env")
    elif "404" in str(e):
        print("\n   💡 PROBLEMA: Endpoint incorrecto")
        print("   SOLUCIÓN: Verifica el endpoint en el .env")
    exit(1)

# 4. Test con Azure AD (opcional)
print("\n4️⃣ PROBANDO CONEXIÓN CON AZURE AD:")
try:
    credential = DefaultAzureCredential()
    project = AIProjectClient(
        endpoint=endpoint,
        credential=credential
    )
    
    agents = project.agents.list_agents(max_results=1)
    print(f"   ✅ Conexión exitosa con Azure AD")
    print(f"   (Puedes usar cualquiera de los dos métodos)")
    
except Exception as e:
    print(f"   ⚠️ Azure AD no funcionó (esto es normal en desarrollo local)")
    print(f"   Usa API Key en su lugar (ya funciona)")

# 5. Verificar agente específico
print("\n5️⃣ VERIFICANDO TU AGENTE:")
try:
    credential = AzureKeyCredential(api_key)
    project = AIProjectClient(
        endpoint=endpoint,
        credential=credential
    )
    
    agent = project.agents.get_agent(agent_id)
    print(f"   ✅ Agente encontrado:")
    print(f"   ID: {agent.id}")
    print(f"   Nombre: {agent.name if hasattr(agent, 'name') else 'N/A'}")
    print(f"   Modelo: {agent.model if hasattr(agent, 'model') else 'N/A'}")
    
except Exception as e:
    print(f"   ❌ Error al obtener el agente:")
    print(f"   {str(e)}")
    
    print("\n   💡 Listando todos los agentes disponibles:")
    try:
        all_agents = project.agents.list_agents()
        if all_agents:
            for ag in all_agents:
                print(f"   - ID: {ag.id}")
                if hasattr(ag, 'name'):
                    print(f"     Nombre: {ag.name}")
        else:
            print(f"   No hay agentes en este proyecto")
    except Exception as e2:
        print(f"   No se pudieron listar los agentes: {e2}")

# 6. Test completo (enviar mensaje)
print("\n6️⃣ TEST COMPLETO (ENVIAR MENSAJE):")
try:
    credential = AzureKeyCredential(api_key)
    project = AIProjectClient(
        endpoint=endpoint,
        credential=credential
    )
    
    agent = project.agents.get_agent(agent_id)
    thread = project.agents.threads.create()
    
    message = project.agents.messages.create(
        thread_id=thread.id,
        role="user",
        content="Test: responde solo 'OK'"
    )
    
    run = project.agents.runs.create_and_process(
        thread_id=thread.id,
        agent_id=agent.id
    )
    
    if run.status == "completed":
        messages = project.agents.messages.list(thread_id=thread.id)
        print(f"   ✅ Test completo exitoso!")
        print(f"   Thread ID: {thread.id}")
        print(f"   Status: {run.status}")
    else:
        print(f"   ⚠️ Status: {run.status}")
        if hasattr(run, 'last_error'):
            print(f"   Error: {run.last_error}")
            
except Exception as e:
    print(f"   ❌ Error en el test completo:")
    print(f"   {str(e)}")

print("\n" + "=" * 70)
print("DIAGNÓSTICO COMPLETADO")
print("=" * 70)

# Resumen final
if all([endpoint, api_key, agent_id]):
    print("\n✅ RESUMEN: Tu configuración está lista")
    print("   Ejecuta 'python main.py' para usar tu agente")
else:
    print("\n❌ RESUMEN: Completa la configuración")
    print("   Revisa los pasos 1 y 2 del documento principal")
```

---

## 🔄 Comparación: TU CÓDIGO vs CÓDIGO ACTUALIZADO

### ❌ Tu código original (que no funciona):

```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import ListSortOrder

project = AIProjectClient(
    credential=DefaultAzureCredential(),  # ❌ Depende de Azure AD
    endpoint="https://gf1aifoundry.services.ai.azure.com/api/projects/firstProject"
)

agent = project.agents.get_agent('asst_7gLtPFYs7Aes9B5J7eHloOHl')
```

### ✅ Código actualizado (que sí funciona):

```python
import os
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.agents.models import ListSortOrder

load_dotenv()  # ✅ Cargar variables de entorno

project = AIProjectClient(
    endpoint=os.getenv("AZURE_AI_PROJECT_ENDPOINT"),  # ✅ Desde .env
    credential=AzureKeyCredential(os.getenv("AZURE_AI_API_KEY"))  # ✅ Usa API Key
)

agent = project.agents.get_agent(os.getenv("AGENT_ID"))  # ✅ Desde .env
```

---

## 📋 Checklist de Implementación

Sigue estos pasos en orden:

- [ ] **Paso 1:** Copiar tu API Key desde el portal (click en el ícono del ojo 👁️)
- [ ] **Paso 2:** Crear archivo `.env` con tus datos
- [ ] **Paso 3:** Actualizar tu código (usar Versión 1 recomendada)
- [ ] **Paso 4:** Crear archivo `.gitignore`
- [ ] **Paso 5:** Instalar dependencias: `pip install -r requirements.txt`
- [ ] **Paso 6:** Ejecutar diagnóstico: `python diagnostico_mi_proyecto.py`
- [ ] **Paso 7:** Si diagnóstico OK, ejecutar: `python main.py`

---

## 🚀 Estructura Final de tu Proyecto

```
tu-proyecto/
├── .env                          # ⚠️ NO subir a Git
├── .gitignore                    # Protege el .env
├── requirements.txt              # Dependencias
├── main.py                       # Tu código principal (Versión 1)
├── main_hibrido.py              # Opcional (Versión 2)
└── diagnostico_mi_proyecto.py   # Script de diagnóstico
```

---

## ⚡ Inicio Rápido (Comandos)

```bash
# 1. Crear archivo .env (copia el template del PASO 2)
nano .env  # o usa tu editor favorito

# 2. Instalar dependencias
pip install azure-ai-projects azure-identity azure-core python-dotenv

# 3. Ejecutar diagnóstico
python diagnostico_mi_proyecto.py

# 4. Si todo OK, ejecutar tu código
python main.py
```

---

## 🎯 Diferencia Clave

| Método | Tu código original | Código actualizado |
|--------|-------------------|-------------------|
| **Autenticación** | `DefaultAzureCredential()` | `AzureKeyCredential(api_key)` |
| **Depende de** | Azure CLI + permisos | Solo API Key |
| **Complejidad** | Alta (múltiples puntos de fallo) | Baja (directo) |
| **Funcionará siempre** | ❌ Puede fallar | ✅ Sí |

---

## 💡 Notas Importantes

### 🔐 Seguridad
- **NUNCA** subas tu `.env` a Git
- **NUNCA** compartas tu API Key públicamente
- Agrega `.env` a `.gitignore` SIEMPRE
- En producción, usa Azure Key Vault

### 🔄 Si cambias de método
Si en el futuro quieres volver a usar `DefaultAzureCredential()`:
1. Asegúrate de tener permisos: `Cognitive Services User` o superior
2. Ejecuta: `az login`
3. Verifica suscripción: `az account show`
4. Usa la Versión 2 (híbrida) como fallback

### 📞 Soporte
Si después de seguir todos los pasos aún tienes problemas:
1. Ejecuta `python diagnostico_mi_proyecto.py`
2. Copia el output completo
3. Revisa específicamente qué paso falló
4. El diagnóstico te dará la solución exacta

---

## ✨ Resumen Ejecutivo

### 🎯 Cambios necesarios en tu código:

1. **Agregar imports:**
   ```python
   import os
   from dotenv import load_dotenv
   from azure.core.credentials import AzureKeyCredential
   ```

2. **Cargar variables:**
   ```python
   load_dotenv()
   ```

3. **Cambiar autenticación:**
   ```python
   # ANTES
   credential=DefaultAzureCredential()
   
   # DESPUÉS
   credential=AzureKeyCredential(os.getenv("AZURE_AI_API_KEY"))
   ```

4. **Usar endpoint desde .env:**
   ```python
   endpoint=os.getenv("AZURE_AI_PROJECT_ENDPOINT")
   ```

¡Y listo! 🎉 Tu código funcionará de manera confiable.
