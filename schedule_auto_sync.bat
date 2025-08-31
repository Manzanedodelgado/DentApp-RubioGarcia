@echo off
REM Script para programar la sincronización automática en Windows
REM Ejecuta cada 4 horas durante días laborables

echo Configurando tarea programada para sincronización automática...

REM Crear tarea programada que ejecute cada 4 horas de lunes a viernes
schtasks /create /tn "RubioGarciaAutoSync" /tr "C:\Rubio_sync\auto_sync_system.py" /sc hourly /mo 4 /d MON,TUE,WED,THU,FRI /st 09:00 /f

if %errorlevel% == 0 (
    echo ✅ Tarea programada creada exitosamente
    echo 📅 Se ejecutará cada 4 horas de lunes a viernes desde las 9:00 AM
    echo 📂 Archivo: C:\Rubio_sync\auto_sync_system.py
) else (
    echo ❌ Error creando la tarea programada
    echo Ejecute este script como Administrador
)

echo.
echo Para ver las tareas programadas: schtasks /query /tn "RubioGarciaAutoSync"
echo Para eliminar la tarea: schtasks /delete /tn "RubioGarciaAutoSync"
echo.
pause