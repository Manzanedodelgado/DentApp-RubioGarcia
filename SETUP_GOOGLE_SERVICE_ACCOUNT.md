# 🔧 CONFIGURACIÓN GOOGLE SERVICE ACCOUNT
## Eliminar Make.com - Acceso directo a Google Sheets

### PASO 1: Crear Service Account en Google Cloud

1. **Ir a Google Cloud Console**:
   - Visita: https://console.cloud.google.com/
   - Selecciona tu proyecto o crea uno nuevo

2. **Habilitar APIs necesarias**:
   - Ve a "APIs & Services" > "Library"
   - Busca y habilita: **Google Sheets API**
   - Busca y habilita: **Google Drive API**

3. **Crear Service Account**:
   - Ve a "IAM & Admin" > "Service Accounts"
   - Clic en "Create Service Account"
   - **Nombre**: `gesden-sync-service`
   - **Description**: `Service account for Gesden to Google Sheets sync`
   - Clic "Create and Continue"

4. **Asignar Rol**:
   - En "Role", selecciona: **Editor** (o **Google Sheets Editor** si disponible)
   - Clic "Continue" > "Done"

### PASO 2: Generar Clave JSON

1. **Crear Clave**:
   - En la lista de Service Accounts, clic en el que acabas de crear
   - Ve a la pestaña "Keys"
   - Clic "Add Key" > "Create new key"
   - Selecciona **JSON**
   - Clic "Create"

2. **Descargar Archivo**:
   - Se descargará un archivo JSON automáticamente
   - **Renómbralo a**: `service-account-key.json`
   - **Guárdalo** en la misma carpeta que tu script Python

### PASO 3: Dar Acceso a Google Sheets

1. **Copiar Email del Service Account**:
   - En el archivo JSON descargado, busca el campo: `"client_email"`
   - Ejemplo: `gesden-sync-service@tu-proyecto.iam.gserviceaccount.com`

2. **Compartir Google Sheets**:
   - Abre tu Google Sheet: https://docs.google.com/spreadsheets/d/1MBDBHQ08XGuf5LxVHCFhHDagIazFkpBnxwqyEQIBJrQ/edit
   - Clic en "Compartir" (botón azul arriba derecha)
   - Pega el email del service account
   - **Permisos**: Selecciona **Editor** (para que pueda escribir)
   - Clic "Enviar"

### PASO 4: Instalar Dependencias Python

Ejecuta estos comandos en tu terminal/cmd donde tienes el script:

```bash
pip install gspread google-auth google-auth-oauthlib google-auth-httplib2
```

### PASO 5: Configurar Script

En el archivo `sync_modified.py`, actualiza estas líneas:

```python
# Línea 11: Tu Google Sheet ID (ya está correcto)
GOOGLE_SHEET_ID = '1MBDBHQ08XGuf5LxVHCFhHDagIazFkpBnxwqyEQIBJrQ'

# Línea 12: Ruta al archivo JSON (asegúrate que esté en la misma carpeta)
SERVICE_ACCOUNT_FILE = 'service-account-key.json'

# Línea 15: URL de tu aplicación SaaS (cambiar por la real)
SAAS_APP_URL = 'https://TU-APP-REAL.com/api/gesden/appointments/receive'

# Línea 16: API Key si es necesario (opcional)
SAAS_API_KEY = 'tu-api-key-si-es-necesario'
```

### PASO 6: Estructura de Archivos

Tu carpeta debe quedar así:
```
📁 tu-carpeta-gesden/
├── sync_modified.py          ← Script nuevo (reemplaza sync.py)
├── service-account-key.json  ← Clave de Google (descargada)
└── sync.py                   ← Tu script original (respaldo)
```

### PASO 7: Probar la Configuración

1. **Ejecutar script modificado**:
```bash
python sync_modified.py
```

2. **Verificar logs**:
   - Debe mostrar: "✅ Google Sheets: Registro X enviado correctamente"
   - Debe mostrar: "✅ SaaS App: Registro X enviado correctamente"

3. **Verificar Google Sheets**:
   - Abre tu Google Sheet
   - Debe aparecer nueva fila con datos de Gesden
   - **Sin pasar por Make.com**

### PASO 8: Automatizar (Opcional)

Una vez que funcione, puedes programar el script modificado:

**Windows Task Scheduler**:
- Reemplaza la tarea actual que ejecuta `sync.py`
- Cambiar por: `python C:\ruta\completa\sync_modified.py`

---

## 🔍 TROUBLESHOOTING

### Error "403 Forbidden":
- Verifica que compartiste el Google Sheet con el service account email
- Verifica que habilitaste Google Sheets API

### Error "File not found service-account-key.json":
- Verifica que el archivo JSON está en la misma carpeta que el script
- Verifica que se llama exactamente: `service-account-key.json`

### Error "Invalid credentials":
- Re-descarga el archivo JSON del service account
- Verifica que no se corrompió durante la descarga

### Script funciona pero no aparece en SaaS App:
- Verifica que `SAAS_APP_URL` sea la URL correcta de tu aplicación
- Verifica los logs del script para errores de HTTP

---

## ✅ RESULTADO FINAL

Una vez configurado:
- ❌ **Eliminado**: Make.com (ya no se usa)
- ✅ **Directo**: Gesden → Script → Google Sheets
- ✅ **Nuevo**: Gesden → Script → SaaS App (consentimientos automáticos)
- ✅ **Beneficios**: Más rápido, menos dependencias, más control