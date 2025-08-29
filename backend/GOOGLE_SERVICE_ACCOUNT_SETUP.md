# 📋 CONFIGURACIÓN DEL SERVICE ACCOUNT DE GOOGLE

Para habilitar la **sincronización bidireccional** con Google Sheets, necesitas configurar un Service Account de Google con tu ID: `105327385088371729569`

## 🔧 **PASOS PARA CONFIGURAR**

### **1. Obtener el archivo JSON de credenciales**

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Selecciona tu proyecto o crea uno nuevo
3. Ve a **IAM & Admin > Service Accounts**
4. Busca tu Service Account con ID: `105327385088371729569`
5. Haz clic en el Service Account
6. Ve a la pestaña **"Keys"**
7. Haz clic en **"Add Key" > "Create New Key"**
8. Selecciona **"JSON"** como tipo
9. Descarga el archivo JSON

### **2. Subir el archivo a la aplicación**

1. **Renombra** el archivo descargado a: `service-account-key.json`
2. **Sube el archivo** a la carpeta: `/app/backend/`

### **3. Compartir el Google Sheet con el Service Account**

1. Abre el archivo JSON descargado
2. Busca el campo `"client_email"` (será algo como: `nombre@proyecto.iam.gserviceaccount.com`)
3. Ve a tu [Google Sheet](https://docs.google.com/spreadsheets/d/1MBDBHQ08XGuf5LxVHCFhHDagIazFkpBnxwqyEQIBJrQ)
4. Haz clic en **"Compartir"** (botón verde)
5. **Agrega el email del service account** con permisos de **"Editor"**
6. Haz clic en **"Enviar"**

### **4. Verificar configuración**

Una vez configurado, el sistema podrá:
- ✅ **Leer** datos del Google Sheet (ya funciona)
- ✅ **Escribir** cambios de vuelta al Google Sheet
- ✅ **Sincronizar** automáticamente los cambios de estado
- ✅ **Detectar** qué cambios están pendientes de sincronizar

## 🔄 **FUNCIONALIDADES DISPONIBLES**

### **En la Agenda:**
- Cambiar estado de citas: Planificada → Confirmada → Completada → Cancelada
- **Indicador visual** de cambios pendientes de sincronizar
- **Botón de sincronización** para enviar cambios a Google Sheets

### **Estados disponibles:**
- 📅 **Planificada** → `Planificada` en Google Sheets
- ✅ **Confirmada** → `Confirmada` en Google Sheets  
- ✔️ **Completada** → `Finalizada` en Google Sheets
- ❌ **Cancelada** → `Cancelada` en Google Sheets

### **Sincronización automática:**
- Los cambios se **marcan automáticamente** como pendientes
- **Contador visual** de cambios pendientes
- **Botón de sincronización** para enviar todos los cambios
- **Indicadores por cita** de estado de sincronización

## ⚠️ **IMPORTANTE**

1. **Mantén el archivo JSON seguro** - contiene credenciales de acceso
2. **No compartas el archivo** públicamente
3. **Verifica que el email del service account tenga permisos** de Editor en el Google Sheet

## 🧪 **PROBAR LA CONFIGURACIÓN**

Una vez subido el archivo, puedes probar:

1. **Cambiar el estado** de una cita en la Agenda
2. **Verificar** que aparece como "pendiente de sincronizar"  
3. **Hacer clic** en "Sincronizar con Google Sheets"
4. **Verificar** en Google Sheets que el cambio se aplicó

## 📞 **SOPORTE**

Si tienes problemas:
- Verifica que el archivo se llame exactamente `service-account-key.json`
- Confirma que está en `/app/backend/`
- Asegúrate de que el Service Account tenga permisos de Editor
- Reinicia el backend después de subir el archivo

---

**¿Necesitas ayuda?** Comparte el email del service account (del archivo JSON) para verificar la configuración.