# 📋 GUÍA DE INSTALACIÓN PASO A PASO
## Eliminar Make.com e Implementar Consentimientos Automáticos

---

## 📁 ARCHIVOS NECESARIOS

Descarga estos archivos a tu carpeta donde tienes el script actual:

### **Archivos principales:**
1. `sync_modified.py` ← Tu nuevo script (reemplaza sync.py)
2. `service-account-key.json` ← Credenciales Google (ya configuradas)
3. `requirements_sync.txt` ← Dependencias Python
4. `test_google_connection.py` ← Script de prueba

### **Archivos opcionales de prueba:**
5. `test_sync_functions.py` ← Para probar sin conexión a Gesden
6. `INSTALACION_PASO_A_PASO.md` ← Esta guía

---

## 🔧 PASO 1: CONFIGURAR ENTORNO PYTHON

### **1.1 - Instalar dependencias**
Abre CMD/Terminal en tu carpeta y ejecuta:
```bash
pip install -r requirements_sync.txt
```

**Si da error**, prueba:
```bash
pip install gspread google-auth google-auth-oauthlib google-auth-httplib2 pyodbc requests
```

### **1.2 - Verificar instalación**
```bash
python -c "import gspread; print('✅ gspread instalado correctamente')"
```

---

## 🌐 PASO 2: CONFIGURAR URL DE TU APLICACIÓN SAAS

### **2.1 - Encontrar tu URL de aplicación**
¿Dónde tienes desplegada tu aplicación SaaS?

**Opciones comunes:**
- `https://tu-dominio.com` ← Si tienes dominio propio
- `https://app-nombre.vercel.app` ← Si usas Vercel
- `https://app-nombre.herokuapp.com` ← Si usas Heroku
- `http://tu-ip:8001` ← Si es servidor propio

### **2.2 - Actualizar sync_modified.py**
Abrir `sync_modified.py` y cambiar la línea 15:

**Cambiar esto:**
```python
SAAS_APP_URL = 'http://localhost:8001/api/gesden/appointments/receive'
```

**Por esto (ejemplo):**
```python
SAAS_APP_URL = 'https://tu-app-real.com/api/gesden/appointments/receive'
```

---

## 🧪 PASO 3: PROBAR CONFIGURACIÓN

### **3.1 - Probar Google Sheets**
```bash
python test_google_connection.py
```

**Resultado esperado:**
```
🎉 PRUEBA COMPLETADA EXITOSAMENTE
   ✅ Google Sheets está configurado correctamente
```

### **3.2 - Probar conexión SaaS (opcional)**
```bash
python test_sync_functions.py
```

**Resultado esperado:**
```
🎉 ¡ÉXITO TOTAL! MAKE.COM ELIMINADO
✅ Google Sheets: Funcionando perfectamente
✅ SaaS App: Consentimientos automáticos listos
```

---

## ⚙️ PASO 4: PROGRAMAR TAREA AUTOMÁTICA

### **4.1 - Windows Task Scheduler**

1. **Abrir Task Scheduler** (Programador de tareas)
2. **Buscar tu tarea actual** que ejecuta `sync.py`
3. **Hacer clic derecho** → "Propiedades"
4. **Ir a "Acciones"** → Editar
5. **Cambiar "Argumentos"** de:
   ```
   sync.py
   ```
   Por:
   ```
   sync_modified.py
   ```

### **4.2 - Verificar programación**
- **Frecuencia recomendada**: Cada 10-15 minutos
- **Hora de inicio**: La que ya tengas configurada
- **Usuario**: El mismo que ya tenías

---

## 🔄 PASO 5: REALIZAR PRIMERA PRUEBA REAL

### **5.1 - Backup de seguridad**
Antes de cambiar nada:
```bash
copy sync.py sync_backup.py
```

### **5.2 - Ejecución manual de prueba**
```bash
python sync_modified.py
```

**Verificar que funcione:**
1. ✅ Se conecta a SQL Server
2. ✅ Extrae datos de Gesden  
3. ✅ Los envía a Google Sheets
4. ✅ Los envía a SaaS App
5. ✅ No hay errores en el log

### **5.3 - Verificar resultados**
- **Google Sheets**: Ver si aparecen nuevas filas
- **SaaS App**: Verificar que se crearon citas y consentimientos

---

## 🎯 PASO 6: ACTIVAR EN PRODUCCIÓN

### **6.1 - Si la prueba fue exitosa**
```bash
# Opcional: Renombrar scripts
ren sync.py sync_old.py
ren sync_modified.py sync.py
```

### **6.2 - Deshabilitar Make.com**
1. **No eliminar aún** - Solo pausar
2. **En Make.com**: Poner el scenario en "Paused"
3. **Monitorear 24h** que sync_modified.py funciona bien

### **6.3 - Eliminar Make.com definitivamente**
**Solo después de confirmar que todo funciona:**
- Borrar el scenario de Make.com
- Cancelar suscripción si no tienes otros usos

---

## 🔍 SOLUCIÓN DE PROBLEMAS

### **Error "No module named 'gspread'"**
```bash
pip install gspread google-auth
```

### **Error "Archivo service-account-key.json no encontrado"**
- Verificar que está en la misma carpeta
- Verificar que se llama exactamente así

### **Error 403 Google Sheets**
- Verificar que compartiste el sheet con el service account
- Email: `rubio-garcia-sheets-sync@appgest-470518.iam.gserviceaccount.com`

### **Error conexión SaaS App**
- Verificar que la URL es correcta
- Verificar que la aplicación está funcionando
- Probar URL en navegador

---

## 📞 SOPORTE

Si tienes problemas en cualquier paso:
1. **Revisar logs** del script para errores específicos
2. **Probar cada componente** por separado
3. **Volver al backup** si es necesario

---

## ✅ RESULTADO FINAL

Una vez completado:
- ❌ **Eliminado**: Make.com
- ✅ **Funcionando**: Gesden → Script → Google Sheets (directo)
- ✅ **Nuevo**: Gesden → Script → SaaS App (consentimientos automáticos)
- ✅ **Beneficios**: Más rápido, menos dependencias, consentimientos automáticos

🎉 **¡Tu clínica tendrá consentimientos automáticos para cirugías, endodoncias, periodoncia, ortodoncia y LOPD para primeras citas!**