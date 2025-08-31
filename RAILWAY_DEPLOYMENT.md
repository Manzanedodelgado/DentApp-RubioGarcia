# 🚀 DESPLIEGUE EN RAILWAY - RUBIO GARCÍA DENTAL

## 📋 GUÍA PASO A PASO

### **PASO 1: Preparar cuenta GitHub**
1. **Ir a**: https://github.com
2. **Crear cuenta** si no tienes
3. **Crear nuevo repositorio**:
   - Nombre: `rubio-garcia-dental`
   - Público o Privado (recomiendo Privado)
   - **No** inicializar con README

### **PASO 2: Subir código a GitHub**
```bash
# En tu computadora, crear carpeta y copiar todos los archivos
mkdir rubio-garcia-dental
cd rubio-garcia-dental

# Copiar todos estos archivos:
# - backend/ (carpeta completa)
# - frontend/ (carpeta completa)  
# - package.json
# - railway.json
# - nixpacks.toml
# - Procfile
# - .env.example

# Inicializar git
git init
git add .
git commit -m "Initial deployment setup"

# Conectar con GitHub (usar la URL de tu repo)
git remote add origin https://github.com/TU-USUARIO/rubio-garcia-dental.git
git push -u origin main
```

### **PASO 3: Desplegar en Railway**
1. **Ir a**: https://railway.app
2. **Sign up with GitHub**
3. **New Project** → **Deploy from GitHub repo**
4. **Seleccionar**: `rubio-garcia-dental`
5. **Deploy**

### **PASO 4: Configurar Variables de Entorno**
En Railway dashboard → **Variables**:

```bash
MONGO_URL=mongodb://mongo:27017/rubio_garcia_dental
GOOGLE_SHEETS_API_KEY=AIzaSyA0c7nuWYhCyuiT8F2dBI_v-oqyjoutQ4A
EMERGENT_LLM_KEY=xai-KLUs5t4FjKzz8azEcjPm1VjsIJjy9E4F7QWkQTpIpy5N4Rdpo51724D2D
```

### **PASO 5: Agregar Base de Datos**
1. **En Railway**: Add service → **Database** → **MongoDB**
2. **Conectar**: Se creará automáticamente MONGO_URL
3. **Actualizar variable** MONGO_URL con la nueva URL

### **PASO 6: Obtener URL de la aplicación**
1. **En Railway**: Ir a tu proyecto
2. **Settings** → **Domains**  
3. **Generate Domain** → Te dará algo como: `https://rubio-garcia-dental-production.up.railway.app`

---

## 🔧 CONFIGURAR SCRIPT LOCAL

### **Una vez desplegada, actualizar sync_modified.py:**

```python
# Cambiar esta línea:
SAAS_APP_URL = 'http://localhost:8001/api/gesden/appointments/receive'

# Por tu URL real de Railway:
SAAS_APP_URL = 'https://rubio-garcia-dental-production.up.railway.app/api/gesden/appointments/receive'
```

---

## ✅ VERIFICAR FUNCIONAMIENTO

### **1. Probar aplicación web:**
- Ir a tu URL de Railway
- Debe aparecer el login (JMD/190582)
- Navegar por Dashboard, Agenda, etc.

### **2. Probar API:**
- `https://tu-url.railway.app/api/health` → Debe devolver "healthy"
- `https://tu-url.railway.app/api/treatment-codes` → Debe mostrar códigos

### **3. Probar script local:**
```bash
python sync_modified.py
```
Debe conectar a Gesden → Google Sheets → Railway SaaS

---

## 🎯 RESULTADO FINAL

### **Flujo completo funcionando:**
1. **Gesden** (local) → **Script Python** → **Google Sheets** ✅
2. **Gesden** (local) → **Script Python** → **Railway SaaS** ✅  
3. **Railway SaaS** → **Consentimientos automáticos** ✅
4. **Acceso web** → `https://tu-url.railway.app` ✅

### **Make.com → ❌ ELIMINADO**

---

## 📞 SOPORTE

Si hay problemas:
1. **Logs de Railway**: Ver en dashboard
2. **Logs del script**: Ejecutar `python sync_modified.py`
3. **Health check**: `https://tu-url.railway.app/api/health`