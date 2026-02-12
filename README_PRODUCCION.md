# Sistema de Inventario Ferre-Exito - Guía de Producción

## Inicio Rápido

### Windows

```powershell
# 1. Instalar Python 3.10+ desde https://www.python.org/downloads/

# 2. Crear entorno virtual
python -m venv venv
.\venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt
pip install gunicorn

# 4. Configurar variables de entorno
copy .env.example .env
# Editar .env con tus valores

# 5. Inicializar base de datos
python -c "from app import create_app, db; app = create_app('production'); app.app_context().push(); db.create_all()"

# 6. Crear usuario administrador
python create_admin.py

# 7. Ejecutar aplicación
gunicorn -c gunicorn_config.py wsgi:app
```

### Linux

```bash
# 1. Instalar dependencias del sistema
sudo apt update
sudo apt install python3.10 python3-pip python3-venv -y

# 2. Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# 3. Instalar dependencias Python
pip install -r requirements.txt
pip install gunicorn

# 4. Configurar variables de entorno
cp .env.example .env
nano .env  # Editar valores

# 5. Inicializar base de datos
python -c "from app import create_app, db; app = create_app('production'); app.app_context().push(); db.create_all()"

# 6. Crear usuario administrador
python create_admin.py

# 7. Ejecutar aplicación
gunicorn -c gunicorn_config.py wsgi:app
```

## Acceso a la Aplicación

Una vez iniciada, accede a:
- **URL Local**: http://localhost:5000
- **URL Red Local**: http://[IP-DEL-SERVIDOR]:5000

## Respaldos

### Windows
```powershell
# Ejecutar respaldo manual
.\backup.bat

# Programar respaldo diario (Programador de Tareas)
# 1. Abrir "Programador de tareas"
# 2. Crear tarea básica
# 3. Acción: Iniciar programa
# 4. Programa: C:\ruta\al\proyecto\backup.bat
# 5. Configurar horario (ej: 2:00 AM diario)
```

### Linux
```bash
# Dar permisos de ejecución
chmod +x backup.sh

# Ejecutar respaldo manual
./backup.sh

# Programar respaldo diario (cron)
crontab -e
# Agregar línea:
0 2 * * * /ruta/al/proyecto/backup.sh >> /ruta/al/proyecto/logs/backup.log 2>&1
```

## Restaurar desde Respaldo

### Windows
```powershell
# 1. Detener aplicación
# 2. Descomprimir respaldo
"C:\Program Files\7-Zip\7z.exe" x backups\inventario_YYYYMMDD_HHMMSS.db.gz

# 3. Reemplazar base de datos
copy inventario_YYYYMMDD_HHMMSS.db instance\inventario.db

# 4. Reiniciar aplicación
```

### Linux
```bash
# 1. Detener aplicación
sudo systemctl stop ferreteria-inventario

# 2. Descomprimir respaldo
gunzip -c backups/inventario_YYYYMMDD_HHMMSS.db.gz > instance/inventario.db

# 3. Reiniciar aplicación
sudo systemctl start ferreteria-inventario
```

## Monitoreo

### Ver Logs
```bash
# Logs de aplicación
tail -f logs/app.log

# Logs de acceso
tail -f logs/access.log

# Logs de errores
tail -f logs/error.log

# Logs de respaldos
tail -f logs/backup.log
```

### Verificar Estado (Linux con systemd)
```bash
# Estado del servicio
sudo systemctl status ferreteria-inventario

# Reiniciar servicio
sudo systemctl restart ferreteria-inventario

# Ver logs del servicio
sudo journalctl -u ferreteria-inventario -f
```

## Solución de Problemas

### La aplicación no inicia

1. Verificar logs: `tail -f logs/error.log`
2. Verificar puerto: `netstat -tulpn | grep 5000` (Linux) o `netstat -ano | findstr 5000` (Windows)
3. Verificar permisos de archivos
4. Verificar que el entorno virtual esté activado

### Error de base de datos

1. Verificar que existe: `ls -la instance/inventario.db`
2. Verificar permisos: `chmod 664 instance/inventario.db`
3. Restaurar desde respaldo si es necesario

### Lentitud

1. Verificar uso de recursos: `htop` (Linux) o Administrador de Tareas (Windows)
2. Optimizar base de datos: `sqlite3 instance/inventario.db "VACUUM;"`
3. Limpiar logs antiguos: `find logs -name "*.log" -mtime +30 -delete`

## Actualización del Sistema

```bash
# 1. Hacer respaldo
./backup.sh  # o backup.bat en Windows

# 2. Detener aplicación
sudo systemctl stop ferreteria-inventario  # Linux
# o cerrar proceso en Windows

# 3. Actualizar código
git pull  # si usas git
# o copiar archivos nuevos

# 4. Actualizar dependencias
source venv/bin/activate  # Linux
# o .\venv\Scripts\activate en Windows
pip install -r requirements.txt --upgrade

# 5. Ejecutar migraciones (si hay)
flask db upgrade

# 6. Reiniciar aplicación
sudo systemctl start ferreteria-inventario  # Linux
# o ejecutar gunicorn en Windows
```

## Seguridad

### Cambiar Contraseña de Admin

```python
python -c "from app import create_app, db; from app.models import User; app = create_app('production'); app.app_context().push(); admin = User.query.filter_by(username='admin').first(); admin.set_password('NUEVA_CONTRASEÑA'); db.session.commit(); print('Contraseña actualizada')"
```

### Generar Nueva SECRET_KEY

```python
python -c "import secrets; print(secrets.token_hex(32))"
# Copiar resultado a .env
```

## Contacto y Soporte

Para soporte técnico:
1. Revisar este documento
2. Consultar `INFORME_PRODUCCION.md` para información detallada
3. Revisar logs en `/logs`
4. Contactar al administrador del sistema

## Información del Sistema

- **Versión**: 1.0
- **Python**: 3.10+
- **Framework**: Flask 3.0
- **Base de Datos**: SQLite (desarrollo) / PostgreSQL (producción recomendada)
- **Servidor**: Gunicorn
- **Fecha**: Febrero 2026
