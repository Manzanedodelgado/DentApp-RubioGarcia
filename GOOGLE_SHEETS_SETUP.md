# 📋 CONFIGURACIÓN GOOGLE SHEETS API - RUBIO GARCÍA DENTAL

## 🚨 PROBLEMA ACTUAL
Tu API key `AIzaSyCSYOu9D-SdyPVnBoqV7ySdA2oUsX7k8wA` está bloqueada con error `API_KEY_SERVICE_BLOCKED`.

## 🔧 SOLUCIÓN PASO A PASO

### 1. ACCEDER A GOOGLE CLOUD CONSOLE
- Ve a: https://console.cloud.google.com/
- Selecciona tu proyecto o crea uno nuevo

### 2. HABILITAR FACTURACIÓN
- Ve a "Facturación" en el menú izquierdo
- Asegúrate de que la facturación esté habilitada
- Si no está habilitada, configurar método de pago

### 3. HABILITAR GOOGLE SHEETS API
- Ve a "APIs y servicios" > "Biblioteca"
- Busca "Google Sheets API"
- Haz clic en "HABILITAR"

### 4. CONFIGURAR API KEY
- Ve a "APIs y servicios" > "Credenciales"
- Encuentra tu API key o crea una nueva
- Haz clic en tu API key para editarla

### 5. CONFIGURAR RESTRICCIONES
En la configuración del API key:

**Restricciones de API:**
- Selecciona "Restringir clave"
- Marca: "Google Sheets API"

**Restricciones de aplicación:**
- Selecciona "Direcciones IP (servidores web, trabajos cron, etc.)"
- Agrega estas IPs:
  - `0.0.0.0/0` (para permitir todos los IPs temporalmente)
  - O la IP específica de tu servidor

### 6. VERIFICAR CUOTAS
- Ve a "APIs y servicios" > "Google Sheets API" > "Cuotas"
- Verifica que tengas cuota disponible
- Límite: 100 solicitudes por 100 segundos por usuario

### 7. REGENERAR CLAVE (SI ES NECESARIO)
Si los pasos anteriores no funcionan:
- Ve a "Credenciales"
- Selecciona tu API key
- Haz clic en "Regenerar clave"
- Copia la nueva clave

## 🔄 ACTUALIZAR EN LA APLICACIÓN

Una vez que tengas la nueva API key funcionando:

1. **Actualizar backend/.env:**
```
GOOGLE_SHEETS_API_KEY=TU_NUEVA_API_KEY_AQUI
```

2. **Reiniciar el backend:**
```bash
sudo supervisorctl restart backend
```

3. **Probar la sincronización:**
- Ve a la aplicación
- La sincronización automática debería funcionar
- O usa el endpoint: POST /api/appointments/sync

## 📊 ESTRUCTURA ESPERADA DEL GOOGLE SHEET

Tu Google Sheet debe tener estas columnas:
- `Registro` - Número de registro
- `Apellidos` - Apellidos del paciente  
- `Nombre` - Nombre del paciente
- `TelMovil` - Teléfono móvil
- `Fecha` - Fecha de la cita (formato: YYYY-MM-DD)
- `Hora` - Hora de la cita (formato: HH:MM)
- `EstadoCita` - Estado (Planificada, Confirmada, Finalizada, Cancelada)
- `Tratamiento` - Tipo de tratamiento
- `Odontologo` - Nombre del odontólogo
- `Notas` - Notas adicionales
- `Duracion` - Duración en minutos

## ✅ VERIFICACIÓN

Una vez configurado correctamente, deberías ver en los logs:
- "🔍 Attempting to fetch data from Google Sheet"
- "✅ Successfully processed X appointments from Google Sheets"
- "📅 Appointments sorted by date"

## 🆘 SI NECESITAS AYUDA

Si sigues teniendo problemas:
1. Verifica que el proyecto de Google Cloud tenga facturación activa
2. Asegúrate de que la API esté habilitada
3. Revisa las restricciones del API key
4. Contacta a soporte de Google Cloud si persiste el problema

---

**IMPORTANTE:** Mientras configuras esto, la aplicación seguirá funcionando con datos de ejemplo para que puedas probar todas las funcionalidades.