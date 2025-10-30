# ConecctAPPtoAOAI
Como Conectar y Revisar datos de coneccion de app de Python to  Azure Open AI


# Guía de Troubleshooting: Conexión Python + LangChain + Azure OpenAI

## 📋 Tabla de Contenidos
- [Introducción](#introducción)
- [Prerequisitos](#prerequisitos)
- [Escenarios Comunes de Fallo](#escenarios-comunes-de-fallo)
- [Configuración Correcta](#configuración-correcta)
- [Validación Paso a Paso](#validación-paso-a-paso)
- [Ejemplos de Código](#ejemplos-de-código)
- [Solución de Problemas Específicos](#solución-de-problemas-específicos)
- [Checklist Final](#checklist-final)

---

## Introducción

Esta guía te ayudará a diagnosticar y resolver problemas de conexión entre tu código Python con LangChain y el servicio Azure OpenAI.

---

## Prerequisitos

### ✅ Variables de Entorno Necesarias

```bash
AZURE_OPENAI_ENDPOINT=https://tu-recurso.openai.azure.com/
AZURE_OPENAI_API_KEY=tu-api-key-aqui
AZURE_OPENAI_DEPLOYMENT_NAME=nombre-de-tu-deployment
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

### ✅ Paquetes Python Requeridos

```bash
pip install langchain-openai
pip install openai>=1.0.0
pip install python-dotenv
pip install azure-identity  # Si usas autenticación con Azure AD
```

---

## Escenarios Comunes de Fallo

### 🔴 Escenario 1: Error de Autenticación (401 Unauthorized)

**Causas posibles:**
- API Key incorrecta o expirada
- Formato incorrecto del endpoint
- Credenciales de Azure CLI no sincronizadas con el código
- Uso de API Key cuando se requiere Azure AD o viceversa

**Validación:**
```bash
# Verificar que estás autenticado en Azure CLI
az account show

# Verificar acceso al recurso de Azure OpenAI
az cognitiveservices account show --name tu-recurso-openai --resource-group tu-resource-group
```

---

### 🔴 Escenario 2: Error 404 - Resource Not Found

**Causas posibles:**
- Nombre del deployment incorrecto
- Endpoint mal formado
- El deployment no existe o fue eliminado
- Version de API incorrecta

**Validación:**
```bash
# Listar todos los deployments disponibles
az cognitiveservices account deployment list \
  --name tu-recurso-openai \
  --resource-group tu-resource-group
```

---

### 🔴 Escenario 3: Error de Red / Timeout

**Causas posibles:**
- Firewall o reglas de red en Azure OpenAI
- Proxy corporativo bloqueando la conexión
- VPN requerida pero no activa
- IP no autorizada en las reglas de red del recurso

**Validación:**
```python
import requests

# Test básico de conectividad
endpoint = "https://tu-recurso.openai.azure.com/"
try:
    response = requests.get(endpoint, timeout=10)
    print(f"Status: {response.status_code}")
except Exception as e:
    print(f"Error de conexión: {e}")
```

---

### 🔴 Escenario 4: Error en Variables de Entorno

**Causas posibles:**
- Archivo `.env` no se está cargando
- Variables no exportadas en el entorno
- Nombres de variables incorrectos
- Espacios o caracteres ocultos en los valores

**Validación:**
```python
import os
from dotenv import load_dotenv

load_dotenv()

# Verificar que las variables se cargaron
print(f"Endpoint: {os.getenv('AZURE_OPENAI_ENDPOINT')}")
print(f"Key existe: {bool(os.getenv('AZURE_OPENAI_API_KEY'))}")
print(f"Deployment: {os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')}")
```

---

### 🔴 Escenario 5: Configuración Incorrecta de LangChain

**Causas posibles:**
- Uso de la clase incorrecta (AzureOpenAI vs AzureChatOpenAI)
- Parámetros incorrectos o faltantes
- Versión incompatible de langchain-openai
- Modelo no compatible con el tipo de deployment

---

## Configuración Correcta

### 📁 Estructura de Archivos

```
tu-proyecto/
├── .env
├── .gitignore
├── requirements.txt
└── main.py
```

### 📄 Archivo `.env`

```env
# IMPORTANTE: No compartir este archivo ni subirlo a git
AZURE_OPENAI_ENDPOINT=https://tu-recurso.openai.azure.com/
AZURE_OPENAI_API_KEY=tu-clave-api-de-64-caracteres
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

### 📄 Archivo `.gitignore`

```gitignore
.env
__pycache__/
*.pyc
venv/
.vscode/
```

### 📄 Archivo `requirements.txt`

```txt
langchain-openai>=0.0.5
openai>=1.0.0
python-dotenv>=1.0.0
azure-identity>=1.15.0
```

---

## Validación Paso a Paso

### Paso 1: Verificar Recurso de Azure OpenAI

```bash
# Verificar que el recurso existe y está activo
az cognitiveservices account show \
  --name tu-recurso-openai \
  --resource-group tu-resource-group \
  --query "{name:name, location:location, provisioningState:properties.provisioningState}"
```

### Paso 2: Obtener el Endpoint Correcto

```bash
# Obtener el endpoint del recurso
az cognitiveservices account show \
  --name tu-recurso-openai \
  --resource-group tu-resource-group \
  --query "properties.endpoint" -o tsv
```

**Formato correcto del endpoint:**
```
https://tu-recurso.openai.azure.com/
```

⚠️ **IMPORTANTE:** El endpoint debe terminar en `/`

### Paso 3: Obtener o Regenerar API Key

```bash
# Obtener las claves del recurso
az cognitiveservices account keys list \
  --name tu-recurso-openai \
  --resource-group tu-resource-group
```

### Paso 4: Verificar Deployments Disponibles

```bash
# Listar todos los deployments y sus modelos
az cognitiveservices account deployment list \
  --name tu-recurso-openai \
  --resource-group tu-resource-group \
  --query "[].{name:name, model:properties.model.name, version:properties.model.version}"
```

### Paso 5: Verificar Reglas de Red

```bash
# Verificar configuración de red del recurso
az cognitiveservices account show \
  --name tu-recurso-openai \
  --resource-group tu-resource-group \
  --query "properties.networkAcls"
```

**Si está configurado con reglas de red:**
- Agregar tu IP pública a las reglas permitidas
- O configurar para permitir todas las redes (solo para desarrollo)

```bash
# Agregar tu IP a las reglas permitidas
az cognitiveservices account network-rule add \
  --name tu-recurso-openai \
  --resource-group tu-resource-group \
  --ip-address $(curl -s ifconfig.me)
```

---

## Ejemplos de Código

### ✅ Ejemplo 1: Configuración Básica con API Key

```python
# main.py
import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI

# Cargar variables de entorno
load_dotenv()

# Configuración del cliente
llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    temperature=0.7,
    max_tokens=800
)

# Test de conexión
try:
    response = llm.invoke("Di 'Hola' si la conexión funciona")
    print(f"✅ Conexión exitosa!")
    print(f"Respuesta: {response.content}")
except Exception as e:
    print(f"❌ Error: {e}")
```

### ✅ Ejemplo 2: Con Azure AD Authentication (sin API Key)

```python
# main.py
import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from langchain_openai import AzureChatOpenAI

load_dotenv()

# Obtener token de Azure AD
token_provider = get_bearer_token_provider(
    DefaultAzureCredential(),
    "https://cognitiveservices.azure.com/.default"
)

llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    azure_ad_token_provider=token_provider,  # En lugar de api_key
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    temperature=0.7
)

try:
    response = llm.invoke("Prueba de conexión con Azure AD")
    print(f"✅ Conexión exitosa con Azure AD!")
    print(f"Respuesta: {response.content}")
except Exception as e:
    print(f"❌ Error: {e}")
```

### ✅ Ejemplo 3: Script de Diagnóstico Completo

```python
# diagnostico.py
import os
import requests
from dotenv import load_dotenv

def diagnosticar_conexion():
    """Script para diagnosticar problemas de conexión con Azure OpenAI"""
    
    load_dotenv()
    
    print("=" * 60)
    print("DIAGNÓSTICO DE CONEXIÓN AZURE OPENAI")
    print("=" * 60)
    
    # 1. Verificar variables de entorno
    print("\n1️⃣ VERIFICANDO VARIABLES DE ENTORNO:")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION")
    
    print(f"   Endpoint: {'✅ Configurado' if endpoint else '❌ NO CONFIGURADO'}")
    print(f"   API Key: {'✅ Configurada' if api_key else '❌ NO CONFIGURADA'}")
    print(f"   Deployment: {'✅ Configurado' if deployment else '❌ NO CONFIGURADO'}")
    print(f"   API Version: {'✅ Configurada' if api_version else '❌ NO CONFIGURADA'}")
    
    if not all([endpoint, api_key, deployment, api_version]):
        print("\n❌ ERROR: Faltan variables de entorno críticas")
        return
    
    # 2. Validar formato del endpoint
    print("\n2️⃣ VALIDANDO FORMATO DEL ENDPOINT:")
    if endpoint.startswith("https://") and endpoint.endswith("/"):
        print(f"   ✅ Formato correcto: {endpoint}")
    else:
        print(f"   ⚠️ Formato incorrecto: {endpoint}")
        print(f"   Debe ser: https://tu-recurso.openai.azure.com/")
    
    # 3. Test de conectividad básica
    print("\n3️⃣ PROBANDO CONECTIVIDAD:")
    try:
        response = requests.get(endpoint, timeout=10)
        print(f"   ✅ Servidor alcanzable (Status: {response.status_code})")
    except requests.exceptions.Timeout:
        print(f"   ❌ Timeout - El servidor no responde")
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Error de conexión - Verifica firewall/VPN")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 4. Test de API con LangChain
    print("\n4️⃣ PROBANDO CONEXIÓN CON LANGCHAIN:")
    try:
        from langchain_openai import AzureChatOpenAI
        
        llm = AzureChatOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=api_version,
            deployment_name=deployment,
            temperature=0
        )
        
        response = llm.invoke("Di solo 'OK'")
        print(f"   ✅ Conexión exitosa!")
        print(f"   Respuesta del modelo: {response.content}")
        
    except ImportError:
        print(f"   ❌ langchain-openai no instalado")
        print(f"   Ejecuta: pip install langchain-openai")
    except Exception as e:
        print(f"   ❌ Error en la conexión:")
        print(f"   {str(e)}")
        
        # Análisis del error
        error_str = str(e).lower()
        if "401" in error_str or "unauthorized" in error_str:
            print("\n   💡 SOLUCIÓN PROBABLE:")
            print("   - Verifica que la API Key sea correcta")
            print("   - Regenera la clave en el portal de Azure")
        elif "404" in error_str or "not found" in error_str:
            print("\n   💡 SOLUCIÓN PROBABLE:")
            print("   - Verifica el nombre del deployment")
            print("   - Lista deployments con: az cognitiveservices account deployment list")
        elif "timeout" in error_str or "connection" in error_str:
            print("\n   💡 SOLUCIÓN PROBABLE:")
            print("   - Verifica reglas de firewall/red en Azure")
            print("   - Verifica que no haya proxy/VPN bloqueando")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    diagnosticar_conexion()
```

### ✅ Ejemplo 4: Con Manejo de Errores Robusto

```python
# main_robusto.py
import os
import sys
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from openai import AzureOpenAI, APIError, APIConnectionError, RateLimitError

def crear_cliente_azure_openai():
    """Crea cliente con validaciones robustas"""
    
    load_dotenv()
    
    # Validar variables
    required_vars = {
        "AZURE_OPENAI_ENDPOINT": os.getenv("AZURE_OPENAI_ENDPOINT"),
        "AZURE_OPENAI_API_KEY": os.getenv("AZURE_OPENAI_API_KEY"),
        "AZURE_OPENAI_DEPLOYMENT_NAME": os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        "AZURE_OPENAI_API_VERSION": os.getenv("AZURE_OPENAI_API_VERSION")
    }
    
    missing = [k for k, v in required_vars.items() if not v]
    if missing:
        print(f"❌ Variables faltantes: {', '.join(missing)}")
        print("Crea un archivo .env con estas variables")
        sys.exit(1)
    
    try:
        llm = AzureChatOpenAI(
            azure_endpoint=required_vars["AZURE_OPENAI_ENDPOINT"],
            api_key=required_vars["AZURE_OPENAI_API_KEY"],
            api_version=required_vars["AZURE_OPENAI_API_VERSION"],
            deployment_name=required_vars["AZURE_OPENAI_DEPLOYMENT_NAME"],
            temperature=0.7,
            max_tokens=1000,
            timeout=30,  # Timeout de 30 segundos
            max_retries=3  # Reintentos automáticos
        )
        return llm
    except Exception as e:
        print(f"❌ Error al crear cliente: {e}")
        sys.exit(1)

def ejecutar_con_manejo_errores(llm, prompt):
    """Ejecuta prompt con manejo de errores específicos"""
    
    try:
        response = llm.invoke(prompt)
        return response.content
        
    except APIConnectionError as e:
        print(f"❌ Error de conexión: {e}")
        print("Verifica tu conexión a internet y las reglas de firewall")
        return None
        
    except RateLimitError as e:
        print(f"⚠️ Límite de tasa excedido: {e}")
        print("Espera unos segundos antes de reintentar")
        return None
        
    except APIError as e:
        print(f"❌ Error de API: {e}")
        if e.status_code == 401:
            print("API Key inválida o expirada")
        elif e.status_code == 404:
            print("Deployment no encontrado - verifica el nombre")
        return None
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return None

if __name__ == "__main__":
    print("Inicializando cliente Azure OpenAI...")
    llm = crear_cliente_azure_openai()
    
    print("Enviando prompt...")
    resultado = ejecutar_con_manejo_errores(
        llm, 
        "Explica en una frase qué es Azure OpenAI"
    )
    
    if resultado:
        print(f"\n✅ Respuesta:\n{resultado}")
    else:
        print("\n❌ No se pudo obtener respuesta")
```

---

## Solución de Problemas Específicos

### 🔧 Problema: "Error: 'NoneType' object has no attribute..."

**Causa:** Variables de entorno no cargadas

**Solución:**
```python
# Agregar al inicio de tu código
from pathlib import Path
from dotenv import load_dotenv

# Buscar .env en el directorio actual
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path, override=True)

# Verificar
import os
print(f"Endpoint cargado: {os.getenv('AZURE_OPENAI_ENDPOINT')}")
```

---

### 🔧 Problema: "Resource not found"

**Causa:** Nombre del deployment incorrecto

**Solución:**
```bash
# Listar deployments exactos
az cognitiveservices account deployment list \
  --name tu-recurso \
  --resource-group tu-rg \
  --query "[].name" -o tsv
```

Copia el nombre EXACTO en tu `.env`

---

### 🔧 Problema: "This model's maximum context length is..."

**Causa:** Tokens excedidos

**Solución:**
```python
llm = AzureChatOpenAI(
    # ... otras configuraciones ...
    max_tokens=4000,  # Ajustar según el modelo
    model_kwargs={
        "top_p": 0.95,
        "frequency_penalty": 0,
        "presence_penalty": 0
    }
)
```

---

### 🔧 Problema: Firewall / Acceso Denegado

**Causa:** Reglas de red restrictivas

**Solución en Azure Portal:**
1. Ve a tu recurso de Azure OpenAI
2. Configuración → Redes
3. Opciones:
   - Permitir todas las redes (desarrollo)
   - Agregar tu IP actual
   - Configurar reglas de red específicas

**O por CLI:**
```bash
# Permitir tu IP actual
MY_IP=$(curl -s ifconfig.me)
az cognitiveservices account network-rule add \
  --name tu-recurso \
  --resource-group tu-rg \
  --ip-address $MY_IP
```

---

### 🔧 Problema: Versión de API Incompatible

**Solución:** Usar versiones estables conocidas

```python
# Versiones recomendadas (ordenadas de más reciente a más antigua)
API_VERSIONS_RECOMENDADAS = [
    "2024-02-15-preview",
    "2023-12-01-preview",
    "2023-05-15",
    "2023-03-15-preview"
]
```

Prueba con diferentes versiones si una falla.

---

## Checklist Final

Usa esta lista para verificar tu configuración:

### ✅ Azure OpenAI (Portal/CLI)

- [ ] El recurso de Azure OpenAI existe y está aprovisionado
- [ ] Tienes acceso (rol Contributor o Cognitive Services User)
- [ ] El deployment existe y está activo
- [ ] La API Key es válida y no ha expirado
- [ ] Las reglas de red permiten tu IP
- [ ] El modelo es compatible con tu uso (chat vs completion)

### ✅ Configuración Local

- [ ] Python 3.8+ instalado
- [ ] Paquetes instalados: `pip install -r requirements.txt`
- [ ] Archivo `.env` existe en la raíz del proyecto
- [ ] Variables en `.env` no tienen espacios ni comillas innecesarias
- [ ] El endpoint termina con `/`
- [ ] Azure CLI autenticado: `az account show`

### ✅ Código

- [ ] `load_dotenv()` llamado antes de usar variables
- [ ] Usando `AzureChatOpenAI` (no `ChatOpenAI` a secas)
- [ ] Todos los parámetros requeridos están presentes
- [ ] Manejo de errores implementado
- [ ] Timeout configurado (ej: 30 segundos)

### ✅ Red y Conectividad

- [ ] Internet funcionando
- [ ] VPN activa si es requerida
- [ ] Proxy configurado si es necesario
- [ ] Firewall no bloqueando conexiones a Azure
- [ ] DNS resolviendo correctamente el endpoint

---

## Comandos Útiles de Troubleshooting

### Información del Recurso
```bash
# Ver todos los detalles del recurso
az cognitiveservices account show \
  --name tu-recurso \
  --resource-group tu-rg \
  --output json

# Ver solo el endpoint
az cognitiveservices account show \
  --name tu-recurso \
  --resource-group tu-rg \
  --query "properties.endpoint" -o tsv

# Ver el estado
az cognitiveservices account show \
  --name tu-recurso \
  --resource-group tu-rg \
  --query "properties.provisioningState" -o tsv
```

### Deployments
```bash
# Listar deployments con detalles
az cognitiveservices account deployment list \
  --name tu-recurso \
  --resource-group tu-rg \
  --output table

# Ver un deployment específico
az cognitiveservices account deployment show \
  --name tu-recurso \
  --resource-group tu-rg \
  --deployment-name nombre-deployment
```

### Keys y Acceso
```bash
# Listar claves
az cognitiveservices account keys list \
  --name tu-recurso \
  --resource-group tu-rg

# Regenerar clave
az cognitiveservices account keys regenerate \
  --name tu-recurso \
  --resource-group tu-rg \
  --key-name key1
```

### Test de Conectividad
```bash
# Test básico con curl (reemplaza los valores)
curl -X POST "https://tu-recurso.openai.azure.com/openai/deployments/tu-deployment/chat/completions?api-version=2024-02-15-preview" \
  -H "Content-Type: application/json" \
  -H "api-key: tu-api-key" \
  -d '{
    "messages": [{"role": "user", "content": "Hola"}],
    "max_tokens": 50
  }'
```

---

## Recursos Adicionales

### Documentación Oficial
- [Azure OpenAI Service](https://learn.microsoft.com/azure/cognitive-services/openai/)
- [LangChain Azure OpenAI](https://python.langchain.com/docs/integrations/llms/azure_openai)
- [OpenAI Python SDK](https://github.com/openai/openai-python)

### Herramientas de Diagnóstico
```bash
# Instalar herramientas de diagnóstico
pip install azure-identity azure-mgmt-cognitiveservices

# Test con OpenAI directo (sin LangChain)
pip install openai --upgrade
```

### Ejemplo de Test Rápido con SDK Nativo
```python
from openai import AzureOpenAI
import os

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

response = client.chat.completions.create(
    model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    messages=[{"role": "user", "content": "Test"}],
    max_tokens=10
)

print(response.choices[0].message.content)
```

---

## Notas Importantes

⚠️ **Seguridad:**
- USAR un sistema de Secretos para optener los parametros de Ambiente , NUNCA Subir esto a un repositorio Publico `.env` a Git
- USAR un sistema de Secretos para optener los parametros de Ambiente , NUNCA Subir esto a un repositorio Publico  compartas tu API Key públicamente
- RECOMENDACION DE SECGURIDAD PARA DATOS DE AMBIENTE, SERVICIO a usar Azure Key Vault en producción
- ACTIVAR UNA POLICA DE Rota las claves o Secrets periódicamente

💡 **Mejores Prácticas:**
- Usa variables de entorno para todos los secretos
- Implementa retry logic para fallos transitorios
- Configura timeouts apropiados (30-60 segundos)
- Monitorea el uso de tokens para evitar sobrecostos
- Usa logging para debugging en desarrollo

🔄 **Actualización O Librerias ya Validades por parte de los Entornos de Desarollo de la compañia:**
- Mantén actualizadas las librerías: `pip install --upgrade langchain-openai openai`
- Revisa las notas de cambio de Azure OpenAI
- Actualiza la API version cuando haya nuevas características

---

## Soporte

Si después de seguir esta guía aún tienes problemas:

1. Ejecuta el script de diagnóstico completo (`diagnostico.py`)
2. Revisa los logs de Azure OpenAI en el Portal
3. Verifica el estado del servicio: [Azure Status](https://status.azure.com/)
4. Contacta al soporte técnico de Azure con la información del diagnóstico

---

**Última actualización:** Octubre 2025
**Versión:** 1.0
