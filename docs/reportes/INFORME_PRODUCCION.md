# Informe de Empaquetado y Producción
## Sistema de Inventario Ferre-Exito

---

## 1. RESUMEN EJECUTIVO

Este documento describe los requisitos, procedimientos y recursos necesarios para desplegar el Sistema de Inventario Ferre-Exito en un entorno de producción.

**Aplicación**: Sistema de Gestión de Inventario Web
**Tecnología**: Flask (Python) + SQLite/PostgreSQL
**Tipo**: Aplicación Web Multi-usuario
**Estado Actual**: Desarrollo completado, listo para producción

---

## 2. ARQUITECTURA DE LA APLICACIÓN

### 2.1 Stack Tecnológico

```
┌─────────────────────────────────────┐
│     Frontend (Navegador Web)        │
│  HTML5 + Bootstrap 5 + JavaScript   │
└─────────────────────────────────────┘
                 ↓ HTTP/HTTPS
┌─────────────────────────────────────┐
│      Servidor Web (Gunicorn)        │
│         Python 3.10+                │
└─────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│     Aplicación Flask                │
│  - Blueprints (Módulos)             │
│  - Servicios de Negocio             │
│  - Repositorios de Datos            │
└─────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│    Base de Datos                    │
│  SQLite (desarrollo/pequeña)        │
│  PostgreSQL (producción/grande)     │
└─────────────────────────────────────┘
```

### 2.2 Componentes Principales

1. **Aplicación Web Flask**
   - Gestión de productos (CRUD completo)
   - Sistema de movimientos (entradas/salidas)
   - Gestión de proveedores y clientes
   - Sistema de órdenes de venta
   - Reportes e inventario diario
   - Sistema de precios con tasa de cambio
   - Generación automática de códigos

2. **Base de Datos**
   - 12 tablas principales
   - Relaciones entre entidades
   - Auditoría completa (created_at, updated_at, deleted_at)
   - Soft deletes implementados

3. **Sistema de Autenticación**
   - Login/Logout
   - Gestión de sesiones
   - Control de acceso por roles

4. **Importación/Exportación**
   - Importación desde Excel
   - Exportación a Excel (Art. 177)
   - Generación de reportes

---

## 3. REQUISITOS DEL SISTEMA

### 3.1 Requisitos Mínimos (Instalación Pequeña)

**Hardware:**
- **Procesador**: Intel Core i3 o equivalente (2 núcleos)
- **RAM**: 4 GB mínimo
- **Disco Duro**: 10 GB libres
- **Red**: Conexión Ethernet 100 Mbps (si es servidor)

**Software:**
- **Sistema Operativo**: 
  - Windows 10/11 (64-bit)
  - Windows Server 2016 o superior
  - Linux (Ubuntu 20.04+, CentOS 8+)
- **Python**: 3.10 o superior
- **Navegador Web**: Chrome, Firefox, Edge (versiones recientes)

**Usuarios Concurrentes**: Hasta 5 usuarios simultáneos

### 3.2 Requisitos Recomendados (Instalación Mediana)

**Hardware:**
- **Procesador**: Intel Core i5 o equivalente (4 núcleos)
- **RAM**: 8 GB
- **Disco Duro**: 50 GB libres (SSD recomendado)
- **Red**: Conexión Gigabit Ethernet

**Software:**
- **Sistema Operativo**: Windows Server 2019/2022 o Linux Server
- **Python**: 3.11
- **Base de Datos**: PostgreSQL 14+ (recomendado para producción)
- **Redis**: Para caché y rate limiting

**Usuarios Concurrentes**: 10-20 usuarios simultáneos

### 3.3 Requisitos Óptimos (Instalación Grande)

**Hardware:**
- **Procesador**: Intel Xeon o AMD EPYC (8+ núcleos)
- **RAM**: 16 GB o más
- **Disco Duro**: 100 GB+ SSD NVMe
- **Red**: Conexión Gigabit Ethernet redundante

**Software:**
- **Sistema Operativo**: Linux Server (Ubuntu Server 22.04 LTS)
- **Python**: 3.11
- **Base de Datos**: PostgreSQL 15+ con replicación
- **Redis**: Para caché distribuido
- **Nginx**: Como proxy reverso
- **Supervisor**: Para gestión de procesos

**Usuarios Concurrentes**: 50+ usuarios simultáneos

---

## 4. OPCIONES DE DESPLIEGUE

### 4.1 Opción 1: Instalación Local (Computadora Individual)

**Ideal para**: Ferretería pequeña, 1-3 usuarios

**Ventajas:**
- Instalación simple
- Sin costos de servidor
- Acceso rápido local
- No requiere internet

**Desventajas:**
- Solo accesible desde esa computadora
- Sin respaldos automáticos
- Requiere que la PC esté siempre encendida

**Pasos de Instalación:**
1. Instalar Python 3.10+
2. Descargar el código de la aplicación
3. Instalar dependencias: `pip install -r requirements.txt`
4. Ejecutar: `python run_app.py`
5. Acceder desde: `http://localhost:5000`

### 4.2 Opción 2: Servidor Local en Red (LAN)

**Ideal para**: Ferretería mediana, 5-15 usuarios en la misma ubicación

**Ventajas:**
- Acceso desde múltiples computadoras en la red local
- Centralización de datos
- Mejor control y respaldos
- Rendimiento óptimo

**Desventajas:**
- Requiere una computadora dedicada como servidor
- Configuración de red necesaria
- Solo accesible dentro de la red local

**Pasos de Instalación:**
1. Configurar servidor Windows/Linux
2. Instalar Python y dependencias
3. Configurar Gunicorn como servidor WSGI
4. Configurar firewall para permitir puerto 5000
5. Acceder desde otras PCs: `http://[IP-SERVIDOR]:5000`

### 4.3 Opción 3: Servidor en la Nube (Internet)

**Ideal para**: Múltiples sucursales, acceso remoto, escalabilidad

**Ventajas:**
- Acceso desde cualquier lugar con internet
- Respaldos automáticos
- Escalabilidad
- Alta disponibilidad
- Mantenimiento profesional

**Desventajas:**
- Costo mensual de hosting
- Requiere conexión a internet
- Dependencia del proveedor

**Proveedores Recomendados:**
- **DigitalOcean**: $6-12 USD/mes (Droplet básico)
- **AWS Lightsail**: $5-10 USD/mes
- **Heroku**: $7-25 USD/mes
- **PythonAnywhere**: $5-12 USD/mes

---

## 5. PROCESO DE EMPAQUETADO

### 5.1 Preparación del Código

```bash
# 1. Limpiar archivos de desarrollo
rm -rf .pytest_cache __pycache__ *.pyc
rm -rf tests/ test_*.py

# 2. Crear archivo de configuración de producción
cp .env.example .env.production

# 3. Generar requirements.txt limpio
pip freeze > requirements.txt

# 4. Crear estructura de directorios
mkdir -p instance logs backups uploads
```

### 5.2 Archivos Necesarios para Producción

```
ferreteria-inventario/
├── app/                    # Código de la aplicación
├── instance/              # Base de datos SQLite
├── logs/                  # Archivos de log
├── backups/               # Respaldos automáticos
├── uploads/               # Archivos subidos
├── migrations/            # Migraciones de BD
├── requirements.txt       # Dependencias Python
├── wsgi.py               # Punto de entrada WSGI
├── .env.production       # Variables de entorno
├── gunicorn_config.py    # Configuración Gunicorn
└── README_PRODUCCION.md  # Instrucciones
```

### 5.3 Configuración de Producción

**Archivo: `.env.production`**
```bash
# Entorno
FLASK_ENV=production
SECRET_KEY=[GENERAR_CLAVE_SEGURA_AQUI]

# Base de Datos
DATABASE_URL=sqlite:///instance/inventario.db
# O para PostgreSQL:
# DATABASE_URL=postgresql://usuario:password@localhost/inventario

# Redis (opcional, para caché)
REDIS_URL=redis://localhost:6379/0

# Seguridad
SESSION_COOKIE_SECURE=True
WTF_CSRF_ENABLED=True

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# Respaldos
BACKUP_DIR=backups
BACKUP_RETENTION_DAYS=30
```

### 5.4 Configuración de Gunicorn

**Archivo: `gunicorn_config.py`**
```python
import multiprocessing

# Servidor
bind = "0.0.0.0:5000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = "logs/access.log"
errorlog = "logs/error.log"
loglevel = "info"

# Proceso
daemon = False
pidfile = "gunicorn.pid"
user = None
group = None
tmp_upload_dir = None

# Seguridad
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
```

---

## 6. INSTALACIÓN PASO A PASO

### 6.1 Instalación en Windows Server

```powershell
# 1. Instalar Python 3.10+
# Descargar desde: https://www.python.org/downloads/
# Marcar "Add Python to PATH"

# 2. Verificar instalación
python --version
pip --version

# 3. Crear directorio de aplicación
mkdir C:\ferreteria-inventario
cd C:\ferreteria-inventario

# 4. Copiar archivos de la aplicación
# (Usar USB, red compartida, o descargar)

# 5. Crear entorno virtual
python -m venv venv
.\venv\Scripts\activate

# 6. Instalar dependencias
pip install -r requirements.txt
pip install gunicorn

# 7. Configurar variables de entorno
copy .env.example .env
# Editar .env con valores de producción

# 8. Inicializar base de datos
python -c "from app import create_app, db; app = create_app('production'); app.app_context().push(); db.create_all()"

# 9. Crear usuario administrador
python create_admin.py

# 10. Ejecutar aplicación
gunicorn -c gunicorn_config.py wsgi:app
```

### 6.2 Instalación en Linux (Ubuntu)

```bash
# 1. Actualizar sistema
sudo apt update && sudo apt upgrade -y

# 2. Instalar Python y dependencias
sudo apt install python3.10 python3-pip python3-venv -y
sudo apt install postgresql postgresql-contrib -y  # Opcional

# 3. Crear usuario para la aplicación
sudo useradd -m -s /bin/bash ferreteria
sudo su - ferreteria

# 4. Clonar/copiar aplicación
mkdir ~/inventario
cd ~/inventario
# Copiar archivos aquí

# 5. Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# 6. Instalar dependencias
pip install -r requirements.txt
pip install gunicorn

# 7. Configurar PostgreSQL (opcional)
sudo -u postgres createdb inventario
sudo -u postgres createuser ferreteria
sudo -u postgres psql -c "ALTER USER ferreteria WITH PASSWORD 'password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE inventario TO ferreteria;"

# 8. Configurar variables de entorno
cp .env.example .env
nano .env  # Editar valores

# 9. Inicializar base de datos
python -c "from app import create_app, db; app = create_app('production'); app.app_context().push(); db.create_all()"

# 10. Crear servicio systemd
sudo nano /etc/systemd/system/ferreteria-inventario.service
```

**Archivo de servicio systemd:**
```ini
[Unit]
Description=Ferreteria Inventario
After=network.target

[Service]
User=ferreteria
Group=ferreteria
WorkingDirectory=/home/ferreteria/inventario
Environment="PATH=/home/ferreteria/inventario/venv/bin"
ExecStart=/home/ferreteria/inventario/venv/bin/gunicorn -c gunicorn_config.py wsgi:app
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Activar y iniciar servicio
sudo systemctl daemon-reload
sudo systemctl enable ferreteria-inventario
sudo systemctl start ferreteria-inventario
sudo systemctl status ferreteria-inventario
```

---

## 7. CONFIGURACIÓN DE NGINX (Opcional pero Recomendado)

```nginx
server {
    listen 80;
    server_name inventario.ferreteria.local;

    # Redirigir a HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name inventario.ferreteria.local;

    # Certificados SSL
    ssl_certificate /etc/ssl/certs/inventario.crt;
    ssl_certificate_key /etc/ssl/private/inventario.key;

    # Configuración SSL
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Logs
    access_log /var/log/nginx/inventario_access.log;
    error_log /var/log/nginx/inventario_error.log;

    # Tamaño máximo de subida
    client_max_body_size 10M;

    # Proxy a Gunicorn
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Archivos estáticos (si los hay)
    location /static {
        alias /home/ferreteria/inventario/app/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

---

## 8. RESPALDOS Y MANTENIMIENTO

### 8.1 Script de Respaldo Automático

**Archivo: `backup.sh`**
```bash
#!/bin/bash

# Configuración
BACKUP_DIR="/home/ferreteria/backups"
DB_PATH="/home/ferreteria/inventario/instance/inventario.db"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Crear directorio de respaldos
mkdir -p $BACKUP_DIR

# Respaldar base de datos
cp $DB_PATH $BACKUP_DIR/inventario_$DATE.db

# Comprimir
gzip $BACKUP_DIR/inventario_$DATE.db

# Eliminar respaldos antiguos
find $BACKUP_DIR -name "inventario_*.db.gz" -mtime +$RETENTION_DAYS -delete

echo "Respaldo completado: inventario_$DATE.db.gz"
```

### 8.2 Configurar Cron para Respaldos Diarios

```bash
# Editar crontab
crontab -e

# Agregar línea para respaldo diario a las 2 AM
0 2 * * * /home/ferreteria/inventario/backup.sh >> /home/ferreteria/inventario/logs/backup.log 2>&1
```

### 8.3 Tareas de Mantenimiento

**Diarias:**
- Respaldo automático de base de datos
- Revisión de logs de errores
- Monitoreo de espacio en disco

**Semanales:**
- Limpieza de archivos temporales
- Revisión de rendimiento
- Actualización de tasa de cambio

**Mensuales:**
- Actualización de dependencias de seguridad
- Revisión de usuarios y permisos
- Optimización de base de datos
- Prueba de restauración de respaldos

---

## 9. SEGURIDAD

### 9.1 Checklist de Seguridad

- [ ] Cambiar SECRET_KEY por valor aleatorio seguro
- [ ] Cambiar contraseña del usuario admin
- [ ] Habilitar HTTPS con certificado SSL
- [ ] Configurar firewall (solo puertos necesarios)
- [ ] Habilitar rate limiting
- [ ] Configurar respaldos automáticos
- [ ] Actualizar sistema operativo regularmente
- [ ] Usar contraseñas fuertes
- [ ] Limitar acceso SSH (solo IPs conocidas)
- [ ] Configurar logs de auditoría
- [ ] Implementar política de contraseñas
- [ ] Revisar logs regularmente

### 9.2 Generar SECRET_KEY Seguro

```python
import secrets
print(secrets.token_hex(32))
# Copiar resultado a .env
```

### 9.3 Configuración de Firewall (Linux)

```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# Verificar
sudo ufw status
```

---

## 10. MONITOREO Y LOGS

### 10.1 Ubicación de Logs

```
logs/
├── app.log          # Log de aplicación
├── access.log       # Log de accesos (Gunicorn)
├── error.log        # Log de errores (Gunicorn)
└── backup.log       # Log de respaldos
```

### 10.2 Comandos Útiles de Monitoreo

```bash
# Ver logs en tiempo real
tail -f logs/app.log

# Buscar errores
grep ERROR logs/app.log

# Ver últimas 100 líneas
tail -n 100 logs/app.log

# Verificar estado del servicio
sudo systemctl status ferreteria-inventario

# Ver uso de recursos
htop
df -h  # Espacio en disco
free -h  # Memoria RAM
```

---

## 11. ESTIMACIÓN DE COSTOS

### 11.1 Opción 1: Servidor Local

**Inversión Inicial:**
- Computadora servidor: $500 - $1,500 USD
- UPS (respaldo eléctrico): $100 - $300 USD
- Switch de red (si no existe): $50 - $150 USD
- **Total**: $650 - $1,950 USD

**Costos Mensuales:**
- Electricidad: ~$20 USD/mes
- Internet: $30 - $50 USD/mes
- **Total**: $50 - $70 USD/mes

### 11.2 Opción 2: Servidor en la Nube

**Inversión Inicial:**
- Configuración inicial: $0 - $200 USD (si contratas a alguien)

**Costos Mensuales:**
- Hosting (DigitalOcean/AWS): $10 - $25 USD/mes
- Dominio: $1 - $2 USD/mes
- Certificado SSL: $0 (Let's Encrypt gratis)
- Respaldos adicionales: $5 - $10 USD/mes
- **Total**: $16 - $37 USD/mes

### 11.3 Opción 3: Híbrida (Recomendada)

- Servidor local para operación diaria
- Respaldo en la nube para seguridad
- **Costo**: Opción 1 + $10 USD/mes de respaldo en nube

---

## 12. CAPACITACIÓN Y SOPORTE

### 12.1 Materiales de Capacitación Necesarios

1. **Manual de Usuario** (a crear)
   - Gestión de productos
   - Registro de movimientos
   - Generación de reportes
   - Importación de Excel
   - Configuración de precios

2. **Manual de Administrador** (a crear)
   - Gestión de usuarios
   - Configuración del sistema
   - Respaldos y restauración
   - Solución de problemas comunes

3. **Videos Tutoriales** (recomendado)
   - Operaciones básicas (15 min)
   - Operaciones avanzadas (20 min)
   - Administración (15 min)

### 12.2 Plan de Capacitación Sugerido

**Día 1 (2 horas):**
- Introducción al sistema
- Navegación básica
- Gestión de productos
- Registro de movimientos

**Día 2 (2 horas):**
- Proveedores y clientes
- Órdenes de venta
- Reportes e inventario diario
- Importación de Excel

**Día 3 (1 hora):**
- Configuración de precios
- Generación de códigos
- Respaldos básicos
- Preguntas y respuestas

---

## 13. SOLUCIÓN DE PROBLEMAS COMUNES

### 13.1 La aplicación no inicia

```bash
# Verificar logs
tail -f logs/error.log

# Verificar que el puerto no esté en uso
netstat -tulpn | grep 5000

# Reiniciar servicio
sudo systemctl restart ferreteria-inventario
```

### 13.2 Error de base de datos

```bash
# Verificar permisos
ls -la instance/inventario.db

# Restaurar desde respaldo
cp backups/inventario_YYYYMMDD.db.gz .
gunzip inventario_YYYYMMDD.db.gz
cp inventario_YYYYMMDD.db instance/inventario.db
```

### 13.3 Lentitud en la aplicación

```bash
# Verificar uso de recursos
htop

# Limpiar caché
rm -rf __pycache__

# Optimizar base de datos SQLite
sqlite3 instance/inventario.db "VACUUM;"
```

---

## 14. ROADMAP DE MEJORAS FUTURAS

### Corto Plazo (1-3 meses)
- [ ] Implementar sistema de notificaciones
- [ ] Agregar gráficos y estadísticas
- [ ] Mejorar reportes con más filtros
- [ ] Implementar API REST completa

### Mediano Plazo (3-6 meses)
- [ ] Aplicación móvil (Android/iOS)
- [ ] Integración con lectores de código de barras
- [ ] Sistema de facturación electrónica
- [ ] Multi-sucursal

### Largo Plazo (6-12 meses)
- [ ] Integración con sistemas contables
- [ ] Predicción de demanda con IA
- [ ] Sistema de punto de venta (POS)
- [ ] E-commerce integrado

---

## 15. CONCLUSIONES Y RECOMENDACIONES

### 15.1 Recomendación Principal

Para Ferre-Exito, recomendamos la **Opción Híbrida**:
- Servidor local para operación diaria (mejor rendimiento, sin dependencia de internet)
- Respaldos automáticos en la nube (seguridad de datos)
- Costo razonable y escalable

### 15.2 Especificaciones Recomendadas

**Servidor:**
- Intel Core i5 (4 núcleos) o superior
- 8 GB RAM
- 256 GB SSD
- Windows 10 Pro o Windows Server 2019
- UPS de 1000VA mínimo

**Red:**
- Router con QoS habilitado
- Switch Gigabit
- Cableado Cat6

### 15.3 Próximos Pasos

1. **Inmediato:**
   - Adquirir hardware recomendado
   - Configurar red local
   - Instalar sistema operativo

2. **Semana 1:**
   - Instalar aplicación
   - Migrar datos existentes
   - Capacitar usuarios clave

3. **Semana 2:**
   - Operación en paralelo (sistema viejo + nuevo)
   - Ajustes y correcciones
   - Capacitación completa del personal

4. **Semana 3:**
   - Transición completa al nuevo sistema
   - Monitoreo intensivo
   - Soporte continuo

### 15.4 Contacto y Soporte

Para soporte técnico o consultas:
- Revisar documentación en `/docs`
- Consultar logs en `/logs`
- Contactar al desarrollador/administrador del sistema

---

**Documento generado**: 11 de Febrero de 2026
**Versión**: 1.0
**Estado**: Listo para Producción
