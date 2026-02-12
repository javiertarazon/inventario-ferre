# Guía de Empaquetado y Requisitos para Producción
## Sistema de Inventario Ferre-Exito v1.1

**Fecha**: 11 de Febrero de 2026  
**Versión**: 1.1  
**Autor**: Sistema de Inventario Ferre-Exito

---

## 📋 TABLA DE CONTENIDOS

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Requisitos de Hardware](#requisitos-de-hardware)
3. [Requisitos de Software](#requisitos-de-software)
4. [Proceso de Empaquetado](#proceso-de-empaquetado)
5. [Instalación en PC de Producción](#instalación-en-pc-de-producción)
6. [Configuración Post-Instalación](#configuración-post-instalación)
7. [Verificación del Sistema](#verificación-del-sistema)
8. [Solución de Problemas](#solución-de-problemas)

---

## 1. RESUMEN EJECUTIVO

Este documento proporciona instrucciones detalladas para empaquetar y desplegar el Sistema de Inventario Ferre-Exito en un entorno de producción.

### ¿Qué incluye este documento?

- ✅ Requisitos exactos de hardware y software
- ✅ Proceso paso a paso de empaquetado
- ✅ Instrucciones de instalación
- ✅ Configuración de producción
- ✅ Lista de verificación completa

### Tiempo estimado de instalación

- **Preparación del PC**: 30-60 minutos
- **Instalación del sistema**: 20-30 minutos
- **Configuración y pruebas**: 30-45 minutos
- **TOTAL**: 1.5 - 2.5 horas

---

## 2. REQUISITOS DE HARDWARE

### 2.1 Configuración MÍNIMA (1-5 usuarios)

**Procesador**:
- Intel Core i3 (8ª generación o superior)
- AMD Ryzen 3 (2000 series o superior)
- 2 núcleos / 4 hilos mínimo
- Velocidad: 2.0 GHz o superior

**Memoria RAM**:
- 4 GB DDR4 mínimo
- Recomendado: 8 GB para mejor rendimiento

**Almacenamiento**:
- 20 GB de espacio libre en disco
- Tipo: HDD 7200 RPM o superior
- Recomendado: SSD para mejor rendimiento

**Red**:
- Tarjeta de red Ethernet 100 Mbps
- O WiFi 802.11n (si es servidor)

**Monitor**:
- Resolución mínima: 1366x768
- Recomendado: 1920x1080 (Full HD)

**Otros**:
- Teclado y mouse
- Puerto USB disponible (para respaldos en USB)


### 2.2 Configuración RECOMENDADA (5-15 usuarios)

**Procesador**:
- Intel Core i5 (10ª generación o superior)
- AMD Ryzen 5 (3000 series o superior)
- 4 núcleos / 8 hilos
- Velocidad: 2.5 GHz o superior

**Memoria RAM**:
- 8 GB DDR4 mínimo
- Recomendado: 16 GB

**Almacenamiento**:
- 50 GB de espacio libre
- SSD SATA (256 GB o superior)
- Velocidad lectura: 500 MB/s mínimo

**Red**:
- Tarjeta de red Gigabit Ethernet (1000 Mbps)
- Switch Gigabit para red local

**Monitor**:
- Resolución: 1920x1080 (Full HD)
- Tamaño: 21" o superior

**Otros**:
- UPS (Sistema de alimentación ininterrumpida) 1000VA
- Disco externo USB 3.0 para respaldos (1 TB)

**Costo aproximado**: $800 - $1,200 USD

### 2.3 Configuración ÓPTIMA (15+ usuarios)

**Procesador**:
- Intel Core i7 (11ª generación o superior)
- AMD Ryzen 7 (5000 series o superior)
- 8 núcleos / 16 hilos
- Velocidad: 3.0 GHz o superior

**Memoria RAM**:
- 16 GB DDR4 mínimo
- Recomendado: 32 GB
- Velocidad: 3200 MHz o superior

**Almacenamiento**:
- 100 GB de espacio libre
- SSD NVMe (512 GB o superior)
- Velocidad lectura: 3000 MB/s mínimo
- Disco secundario para respaldos (1 TB HDD)

**Red**:
- Tarjeta de red Gigabit Ethernet dual
- Switch Gigabit administrable
- Cableado Cat6 o superior

**Monitor**:
- Resolución: 1920x1080 o superior
- Dual monitor recomendado

**Otros**:
- UPS 1500VA con gestión remota
- Disco externo USB 3.0 para respaldos (2 TB)
- Sistema de refrigeración adecuado

**Costo aproximado**: $1,500 - $2,500 USD


---

## 3. REQUISITOS DE SOFTWARE

### 3.1 Sistema Operativo

**Opción 1: Windows (Recomendado para Ferre-Exito)**

- Windows 10 Pro (64-bit) - Versión 21H2 o superior
- Windows 11 Pro (64-bit)
- Windows Server 2019 Standard o superior

**Ventajas**:
- Interfaz familiar para usuarios
- Fácil administración
- Soporte técnico amplio

**Licencia**: $145 - $200 USD (Windows 10 Pro)

**Opción 2: Linux (Más económico)**

- Ubuntu Server 22.04 LTS (64-bit)
- Ubuntu Desktop 22.04 LTS (64-bit)
- Debian 11 o superior
- CentOS Stream 9

**Ventajas**:
- Gratuito y open source
- Más estable y seguro
- Menor consumo de recursos

**Licencia**: Gratuito

### 3.2 Software Base Requerido

#### Python 3.10 o superior

**Windows**:
- Descargar desde: https://www.python.org/downloads/
- Versión recomendada: Python 3.11.x
- Tamaño descarga: ~30 MB
- Espacio instalación: ~100 MB

**Linux**:
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
```

#### Git (Opcional, para actualizaciones)

**Windows**:
- Descargar desde: https://git-scm.com/download/win
- Versión: 2.40 o superior
- Tamaño: ~50 MB

**Linux**:
```bash
sudo apt install git
```


### 3.3 Dependencias Python (Incluidas en el paquete)

El sistema requiere las siguientes librerías Python (ya incluidas en `requirements.txt`):

```
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-Login==0.6.3
Flask-WTF==1.2.1
Flask-Migrate==4.0.5
Werkzeug==3.0.1
SQLAlchemy==2.0.23
pandas==2.1.4
openpyxl==3.1.2
python-dotenv==1.0.0
bcrypt==4.1.2
gunicorn==21.2.0
```

**Tamaño total de dependencias**: ~150 MB

### 3.4 Software Adicional (Opcional)

#### Para Producción Avanzada:

**PostgreSQL** (Si se requiere base de datos más robusta):
- Versión: 15 o superior
- Tamaño: ~200 MB
- Uso: Reemplazar SQLite para mayor capacidad

**Redis** (Para caché):
- Versión: 7.0 o superior
- Tamaño: ~50 MB
- Uso: Mejorar rendimiento

**Nginx** (Proxy reverso):
- Versión: 1.24 o superior
- Tamaño: ~10 MB
- Uso: Servir aplicación con SSL/HTTPS

---

## 4. PROCESO DE EMPAQUETADO

### 4.1 Preparar el Paquete de Instalación

#### Paso 1: Clonar o Descargar el Repositorio

**Opción A: Usando Git**
```bash
git clone https://github.com/javiertarazon/inventario-ferre.git
cd inventario-ferre
git checkout v1.1
```

**Opción B: Descarga Directa**
1. Ir a: https://github.com/javiertarazon/inventario-ferre
2. Click en "Code" → "Download ZIP"
3. Descomprimir en carpeta deseada


#### Paso 2: Estructura del Paquete

El paquete debe contener:

```
inventario-ferre/
├── app/                          # Código de la aplicación
│   ├── blueprints/              # Módulos de rutas
│   ├── models/                  # Modelos de base de datos
│   ├── repositories/            # Capa de acceso a datos
│   ├── services/                # Lógica de negocio
│   ├── templates/               # Plantillas HTML
│   ├── utils/                   # Utilidades
│   └── __init__.py
├── migrations/                   # Migraciones de BD
├── instance/                     # Base de datos (se crea en instalación)
├── logs/                        # Logs (se crea en instalación)
├── backups/                     # Respaldos (se crea en instalación)
├── uploads/                     # Archivos subidos (se crea en instalación)
├── .env.example                 # Plantilla de configuración
├── requirements.txt             # Dependencias Python
├── run_app.py                   # Script de ejecución desarrollo
├── wsgi.py                      # Punto de entrada producción
├── gunicorn_config.py           # Configuración Gunicorn
├── create_admin.py              # Script crear administrador
├── create_categories.py         # Script crear categorías
├── backup.sh                    # Script respaldo Linux
├── backup.bat                   # Script respaldo Windows
├── README.md                    # Documentación principal
├── INFORME_PRODUCCION.md        # Guía de producción
├── RESUMEN_EJECUTIVO_PRODUCCION.md
├── CHECKLIST_INSTALACION.md
└── VERSION                      # Número de versión
```

**Tamaño total del paquete**: ~5-10 MB (sin dependencias)

#### Paso 3: Crear Paquete Comprimido

**Windows**:
```powershell
# Usando 7-Zip o WinRAR
Compress-Archive -Path "inventario-ferre" -DestinationPath "inventario-ferre-v1.1.zip"
```

**Linux**:
```bash
tar -czf inventario-ferre-v1.1.tar.gz inventario-ferre/
```

**Tamaño del archivo comprimido**: ~2-3 MB


### 4.2 Crear Paquete con Dependencias (Instalación Offline)

Para instalación en PC sin internet:

#### Paso 1: Descargar Dependencias

```bash
# Crear carpeta para dependencias
mkdir dependencias

# Descargar todas las dependencias
pip download -r requirements.txt -d dependencias/
```

**Tamaño de carpeta dependencias**: ~150-200 MB

#### Paso 2: Crear Paquete Completo

```bash
# Incluir código + dependencias
tar -czf inventario-ferre-v1.1-completo.tar.gz inventario-ferre/ dependencias/
```

**Tamaño del paquete completo**: ~100-150 MB comprimido

---

## 5. INSTALACIÓN EN PC DE PRODUCCIÓN

### 5.1 Preparación del PC

#### Checklist Pre-Instalación

- [ ] PC cumple requisitos mínimos de hardware
- [ ] Sistema operativo instalado y actualizado
- [ ] Usuario con permisos de administrador
- [ ] Conexión a internet (para instalación online)
- [ ] Antivirus configurado (agregar excepciones si es necesario)
- [ ] Firewall configurado
- [ ] Espacio en disco verificado (mínimo 20 GB libres)

#### Paso 1: Instalar Python

**Windows**:

1. Descargar Python 3.11 desde https://www.python.org/downloads/
2. Ejecutar instalador
3. ✅ IMPORTANTE: Marcar "Add Python to PATH"
4. Click "Install Now"
5. Esperar finalización (~5 minutos)

**Verificar instalación**:
```powershell
python --version
# Debe mostrar: Python 3.11.x

pip --version
# Debe mostrar: pip 23.x.x
```

**Linux**:
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip -y
python3.11 --version
```


### 5.2 Instalación del Sistema

#### Paso 1: Descomprimir Paquete

**Windows**:
```powershell
# Crear carpeta de instalación
mkdir C:\ferreteria-inventario
cd C:\ferreteria-inventario

# Descomprimir paquete
Expand-Archive -Path "inventario-ferre-v1.1.zip" -DestinationPath .
```

**Linux**:
```bash
# Crear carpeta de instalación
sudo mkdir -p /opt/ferreteria-inventario
cd /opt/ferreteria-inventario

# Descomprimir paquete
sudo tar -xzf inventario-ferre-v1.1.tar.gz
```

#### Paso 2: Crear Entorno Virtual

**Windows**:
```powershell
cd C:\ferreteria-inventario\inventario-ferre

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
.\venv\Scripts\activate

# Verificar activación (debe aparecer (venv) en el prompt)
```

**Linux**:
```bash
cd /opt/ferreteria-inventario/inventario-ferre

# Crear entorno virtual
python3.11 -m venv venv

# Activar entorno virtual
source venv/bin/activate
```

#### Paso 3: Instalar Dependencias

**Instalación Online** (con internet):
```bash
pip install -r requirements.txt
```

Tiempo estimado: 5-10 minutos

**Instalación Offline** (sin internet):
```bash
pip install --no-index --find-links=../dependencias -r requirements.txt
```


#### Paso 4: Configurar Variables de Entorno

```bash
# Copiar plantilla de configuración
cp .env.example .env

# Editar archivo .env
# Windows: notepad .env
# Linux: nano .env
```

**Contenido mínimo de .env**:
```bash
# Entorno
FLASK_ENV=production
SECRET_KEY=tu-clave-secreta-muy-segura-aqui-cambiar

# Base de Datos
DATABASE_URL=sqlite:///instance/inventario.db

# Configuración de la aplicación
FLASK_APP=wsgi.py

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# Respaldos
BACKUP_DIR=backups
BACKUP_RETENTION_DAYS=30
```

**IMPORTANTE**: Cambiar `SECRET_KEY` por un valor aleatorio seguro.

**Generar SECRET_KEY seguro**:
```python
python -c "import secrets; print(secrets.token_hex(32))"
```

#### Paso 5: Crear Directorios Necesarios

```bash
# Crear directorios
mkdir -p instance logs backups uploads

# Verificar estructura
ls -la
```

#### Paso 6: Inicializar Base de Datos

```bash
# Crear base de datos
python -c "from app import create_app, db; app = create_app('production'); app.app_context().push(); db.create_all(); print('Base de datos creada exitosamente')"
```

#### Paso 7: Crear Usuario Administrador

```bash
python create_admin.py
```

Seguir las instrucciones en pantalla:
- Ingresar nombre de usuario (ej: admin)
- Ingresar email
- Ingresar contraseña (mínimo 8 caracteres)
- Confirmar contraseña


#### Paso 8: Crear Categorías Iniciales

```bash
python create_categories.py
```

Esto creará las 7 categorías predefinidas:
- Electricidad
- Plomería
- Albañilería
- Carpintería
- Herrería
- Tornillería
- Misceláneos

#### Paso 9: Probar Instalación

**Modo Desarrollo** (para pruebas):
```bash
python run_app.py
```

Abrir navegador en: http://localhost:5000

**Modo Producción** (para uso real):
```bash
gunicorn -c gunicorn_config.py wsgi:app
```

Abrir navegador en: http://localhost:5000

**Credenciales de prueba**:
- Usuario: admin
- Contraseña: (la que configuraste)

---

## 6. CONFIGURACIÓN POST-INSTALACIÓN

### 6.1 Configurar Inicio Automático

#### Windows - Crear Servicio

**Opción 1: Usar NSSM (Non-Sucking Service Manager)**

1. Descargar NSSM desde: https://nssm.cc/download
2. Extraer nssm.exe
3. Abrir CMD como Administrador:

```cmd
cd C:\ferreteria-inventario\inventario-ferre

# Instalar servicio
nssm install FerreteriaInventario "C:\ferreteria-inventario\inventario-ferre\venv\Scripts\gunicorn.exe" "-c gunicorn_config.py wsgi:app"

# Configurar directorio de trabajo
nssm set FerreteriaInventario AppDirectory "C:\ferreteria-inventario\inventario-ferre"

# Iniciar servicio
nssm start FerreteriaInventario
```

**Opción 2: Tarea Programada**

1. Abrir "Programador de tareas"
2. Crear tarea básica
3. Nombre: "Ferreteria Inventario"
4. Desencadenador: Al iniciar el sistema
5. Acción: Iniciar programa
6. Programa: `C:\ferreteria-inventario\inventario-ferre\venv\Scripts\python.exe`
7. Argumentos: `run_app.py`
8. Directorio: `C:\ferreteria-inventario\inventario-ferre`


#### Linux - Crear Servicio Systemd

Crear archivo de servicio:
```bash
sudo nano /etc/systemd/system/ferreteria-inventario.service
```

Contenido:
```ini
[Unit]
Description=Sistema de Inventario Ferre-Exito
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/ferreteria-inventario/inventario-ferre
Environment="PATH=/opt/ferreteria-inventario/inventario-ferre/venv/bin"
ExecStart=/opt/ferreteria-inventario/inventario-ferre/venv/bin/gunicorn -c gunicorn_config.py wsgi:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Activar servicio:
```bash
sudo systemctl daemon-reload
sudo systemctl enable ferreteria-inventario
sudo systemctl start ferreteria-inventario
sudo systemctl status ferreteria-inventario
```

### 6.2 Configurar Firewall

#### Windows Firewall

```powershell
# Abrir puerto 5000
New-NetFirewallRule -DisplayName "Ferreteria Inventario" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow
```

#### Linux UFW

```bash
sudo ufw allow 5000/tcp
sudo ufw enable
sudo ufw status
```

### 6.3 Configurar Respaldos Automáticos

#### Windows - Tarea Programada

1. Abrir "Programador de tareas"
2. Crear tarea básica
3. Nombre: "Respaldo Inventario"
4. Desencadenador: Diariamente a las 2:00 AM
5. Acción: Iniciar programa
6. Programa: `C:\ferreteria-inventario\inventario-ferre\backup.bat`

#### Linux - Cron Job

```bash
# Editar crontab
crontab -e

# Agregar línea (respaldo diario a las 2 AM)
0 2 * * * /opt/ferreteria-inventario/inventario-ferre/backup.sh >> /opt/ferreteria-inventario/inventario-ferre/logs/backup.log 2>&1
```


### 6.4 Configurar Acceso desde Otros PCs en la Red

#### Paso 1: Obtener IP del Servidor

**Windows**:
```powershell
ipconfig
# Buscar "Dirección IPv4" (ej: 192.168.1.100)
```

**Linux**:
```bash
ip addr show
# O
hostname -I
```

#### Paso 2: Configurar Gunicorn para Escuchar en Todas las Interfaces

Editar `gunicorn_config.py`:
```python
bind = "0.0.0.0:5000"  # Cambiar de 127.0.0.1:5000 a 0.0.0.0:5000
```

#### Paso 3: Reiniciar Servicio

**Windows**:
```powershell
nssm restart FerreteriaInventario
```

**Linux**:
```bash
sudo systemctl restart ferreteria-inventario
```

#### Paso 4: Acceder desde Otros PCs

En cualquier PC de la red, abrir navegador:
```
http://192.168.1.100:5000
```

(Reemplazar 192.168.1.100 con la IP real del servidor)

---

## 7. VERIFICACIÓN DEL SISTEMA

### 7.1 Checklist de Verificación

#### Verificación Básica

- [ ] Python instalado correctamente (`python --version`)
- [ ] Entorno virtual creado y activado
- [ ] Dependencias instaladas (`pip list`)
- [ ] Archivo .env configurado
- [ ] SECRET_KEY cambiado
- [ ] Directorios creados (instance, logs, backups, uploads)
- [ ] Base de datos inicializada
- [ ] Usuario administrador creado
- [ ] Categorías creadas

#### Verificación de Funcionalidad

- [ ] Aplicación inicia sin errores
- [ ] Login funciona correctamente
- [ ] Dashboard se carga
- [ ] Puede crear un producto de prueba
- [ ] Puede editar el producto
- [ ] Puede eliminar el producto
- [ ] Búsqueda funciona
- [ ] Filtros por categoría funcionan
- [ ] Importación de Excel funciona
- [ ] Exportación de reportes funciona


#### Verificación de Red

- [ ] Servidor accesible desde localhost
- [ ] Servidor accesible desde otros PCs en la red
- [ ] Firewall configurado correctamente
- [ ] Puerto 5000 abierto

#### Verificación de Respaldos

- [ ] Script de respaldo ejecuta correctamente
- [ ] Respaldos se guardan en carpeta backups/
- [ ] Respaldos se comprimen correctamente
- [ ] Tarea programada configurada

### 7.2 Comandos de Verificación

```bash
# Verificar Python
python --version

# Verificar pip
pip --version

# Verificar dependencias instaladas
pip list

# Verificar estructura de directorios
ls -la

# Verificar base de datos
ls -la instance/

# Verificar logs
ls -la logs/

# Verificar proceso corriendo (Linux)
ps aux | grep gunicorn

# Verificar puerto abierto (Linux)
netstat -tulpn | grep 5000

# Verificar servicio (Linux)
sudo systemctl status ferreteria-inventario
```

### 7.3 Pruebas de Carga

#### Prueba con 1 Usuario
```bash
# Abrir navegador y navegar por todas las secciones
# Verificar tiempos de respuesta < 1 segundo
```

#### Prueba con Múltiples Usuarios
```bash
# Abrir 5-10 navegadores simultáneamente
# Realizar operaciones concurrentes
# Verificar que no hay errores
```

---

## 8. SOLUCIÓN DE PROBLEMAS

### 8.1 Problemas Comunes

#### Problema: "Python no se reconoce como comando"

**Solución**:
1. Reinstalar Python marcando "Add to PATH"
2. O agregar manualmente a PATH:
   - Windows: Variables de entorno → PATH → Agregar `C:\Python311`
   - Linux: Agregar a ~/.bashrc: `export PATH=$PATH:/usr/bin/python3.11`


#### Problema: "Error al instalar dependencias"

**Solución**:
```bash
# Actualizar pip
python -m pip install --upgrade pip

# Limpiar caché
pip cache purge

# Reinstalar dependencias
pip install -r requirements.txt --no-cache-dir
```

#### Problema: "No se puede acceder desde otros PCs"

**Solución**:
1. Verificar que gunicorn escucha en 0.0.0.0:5000
2. Verificar firewall:
   ```powershell
   # Windows
   Get-NetFirewallRule -DisplayName "Ferreteria Inventario"
   ```
3. Verificar IP del servidor:
   ```bash
   ipconfig  # Windows
   ip addr   # Linux
   ```
4. Ping desde otro PC:
   ```bash
   ping 192.168.1.100
   ```

#### Problema: "Base de datos bloqueada"

**Solución**:
```bash
# Detener aplicación
# Verificar procesos usando la BD
lsof instance/inventario.db  # Linux
# Reiniciar aplicación
```

#### Problema: "Aplicación lenta"

**Solución**:
1. Verificar recursos del sistema:
   ```bash
   # Windows
   taskmgr
   
   # Linux
   htop
   top
   ```
2. Aumentar workers en gunicorn_config.py:
   ```python
   workers = 4  # Aumentar según CPU
   ```
3. Optimizar base de datos:
   ```bash
   sqlite3 instance/inventario.db "VACUUM;"
   ```

#### Problema: "Error 500 al cargar página"

**Solución**:
1. Revisar logs:
   ```bash
   tail -f logs/error.log
   tail -f logs/app.log
   ```
2. Verificar SECRET_KEY en .env
3. Verificar permisos de archivos:
   ```bash
   # Linux
   sudo chown -R www-data:www-data /opt/ferreteria-inventario
   ```


### 8.2 Logs y Diagnóstico

#### Ubicación de Logs

```
logs/
├── app.log          # Log general de la aplicación
├── error.log        # Log de errores
├── access.log       # Log de accesos (Gunicorn)
└── backup.log       # Log de respaldos
```

#### Comandos Útiles

```bash
# Ver últimas 50 líneas del log
tail -n 50 logs/app.log

# Ver log en tiempo real
tail -f logs/app.log

# Buscar errores
grep ERROR logs/app.log

# Buscar por fecha
grep "2026-02-11" logs/app.log

# Ver tamaño de logs
du -h logs/
```

### 8.3 Contacto y Soporte

Para soporte adicional:

1. **Documentación**: Revisar INFORME_PRODUCCION.md
2. **Logs**: Revisar archivos en carpeta logs/
3. **Tests**: Ejecutar `pytest` para verificar sistema
4. **GitHub**: https://github.com/javiertarazon/inventario-ferre

---

## 9. RESUMEN DE RECURSOS NECESARIOS

### 9.1 Tabla Comparativa de Configuraciones

| Recurso | Mínimo | Recomendado | Óptimo |
|---------|--------|-------------|--------|
| **Procesador** | Core i3 2 núcleos | Core i5 4 núcleos | Core i7 8 núcleos |
| **RAM** | 4 GB | 8 GB | 16 GB |
| **Disco** | 20 GB HDD | 50 GB SSD | 100 GB NVMe |
| **Red** | 100 Mbps | 1 Gbps | 1 Gbps Dual |
| **Usuarios** | 1-5 | 5-15 | 15+ |
| **Costo** | $500-800 | $800-1,200 | $1,500-2,500 |

### 9.2 Software Requerido

| Software | Versión | Tamaño | Licencia | Costo |
|----------|---------|--------|----------|-------|
| Windows 10 Pro | 21H2+ | 20 GB | Comercial | $145-200 |
| Ubuntu Server | 22.04 LTS | 5 GB | GPL | Gratis |
| Python | 3.11+ | 100 MB | PSF | Gratis |
| Sistema Inventario | 1.1 | 10 MB | Propietaria | - |
| Dependencias Python | - | 150 MB | Varias | Gratis |


### 9.3 Espacio en Disco Requerido

| Componente | Tamaño |
|------------|--------|
| Sistema Operativo | 20-30 GB |
| Python + pip | 100 MB |
| Código de la aplicación | 10 MB |
| Dependencias Python | 150 MB |
| Base de datos (inicial) | 1 MB |
| Base de datos (1000 productos) | 5-10 MB |
| Logs (por mes) | 50-100 MB |
| Respaldos (30 días) | 300-500 MB |
| **TOTAL MÍNIMO** | **25 GB** |
| **RECOMENDADO** | **50 GB** |

### 9.4 Ancho de Banda de Red

| Usuarios | Ancho de Banda Mínimo | Recomendado |
|----------|----------------------|-------------|
| 1-5 | 10 Mbps | 50 Mbps |
| 5-15 | 50 Mbps | 100 Mbps |
| 15+ | 100 Mbps | 500 Mbps |

### 9.5 Consumo Eléctrico Estimado

| Configuración | Consumo (Watts) | Costo Mensual* |
|---------------|-----------------|----------------|
| Mínima | 50-100 W | $10-15 |
| Recomendada | 100-150 W | $15-25 |
| Óptima | 150-250 W | $25-40 |

*Basado en $0.15 por kWh, 24/7

---

## 10. CHECKLIST FINAL DE INSTALACIÓN

### Pre-Instalación
- [ ] PC cumple requisitos mínimos
- [ ] Sistema operativo instalado
- [ ] Conexión a internet disponible
- [ ] Usuario administrador disponible
- [ ] Espacio en disco verificado (20+ GB)

### Instalación de Software Base
- [ ] Python 3.11+ instalado
- [ ] Python agregado a PATH
- [ ] pip funcionando correctamente
- [ ] Git instalado (opcional)

### Instalación del Sistema
- [ ] Paquete descargado/descomprimido
- [ ] Entorno virtual creado
- [ ] Dependencias instaladas
- [ ] Archivo .env configurado
- [ ] SECRET_KEY cambiado
- [ ] Directorios creados

### Configuración de Base de Datos
- [ ] Base de datos inicializada
- [ ] Usuario administrador creado
- [ ] Categorías creadas
- [ ] Datos de prueba cargados (opcional)


### Configuración de Producción
- [ ] Servicio/tarea programada configurado
- [ ] Inicio automático habilitado
- [ ] Firewall configurado
- [ ] Puerto 5000 abierto
- [ ] Acceso desde red local verificado

### Configuración de Respaldos
- [ ] Script de respaldo probado
- [ ] Tarea programada de respaldo configurada
- [ ] Carpeta de respaldos creada
- [ ] Respaldo manual exitoso

### Verificación Final
- [ ] Aplicación inicia correctamente
- [ ] Login funciona
- [ ] Dashboard carga
- [ ] CRUD de productos funciona
- [ ] Búsqueda funciona
- [ ] Importación Excel funciona
- [ ] Exportación funciona
- [ ] Acceso desde otros PCs funciona
- [ ] Respaldos automáticos funcionan

### Documentación
- [ ] Credenciales documentadas
- [ ] IP del servidor documentada
- [ ] Procedimientos de respaldo documentados
- [ ] Contactos de soporte documentados

---

## 11. RECOMENDACIONES FINALES

### 11.1 Seguridad

1. **Cambiar contraseñas por defecto**
   - Usuario admin debe tener contraseña fuerte
   - Cambiar SECRET_KEY en .env

2. **Configurar respaldos**
   - Respaldos diarios automáticos
   - Copias en ubicación externa (USB, nube)
   - Probar restauración periódicamente

3. **Actualizar sistema**
   - Mantener Windows/Linux actualizado
   - Actualizar Python cuando sea necesario
   - Revisar actualizaciones de la aplicación

4. **Monitorear logs**
   - Revisar logs semanalmente
   - Buscar errores o accesos sospechosos
   - Limpiar logs antiguos (>30 días)

### 11.2 Mantenimiento

**Diario**:
- Verificar que aplicación está corriendo
- Verificar respaldo automático se ejecutó

**Semanal**:
- Revisar logs de errores
- Verificar espacio en disco
- Probar acceso desde diferentes PCs

**Mensual**:
- Optimizar base de datos (VACUUM)
- Limpiar logs antiguos
- Verificar respaldos
- Actualizar tasa de cambio


### 11.3 Capacitación de Usuarios

**Personal Operativo** (2 horas):
- Navegación básica
- Gestión de productos
- Registro de movimientos
- Generación de reportes

**Administrador** (3 horas):
- Todo lo anterior +
- Gestión de usuarios
- Configuración del sistema
- Respaldos y restauración
- Solución de problemas

### 11.4 Plan de Contingencia

**Si el servidor falla**:
1. Verificar logs en carpeta logs/
2. Reiniciar servicio/aplicación
3. Si persiste, restaurar desde respaldo más reciente
4. Contactar soporte técnico

**Si se pierde la base de datos**:
1. Detener aplicación
2. Restaurar desde carpeta backups/
3. Copiar respaldo más reciente a instance/
4. Reiniciar aplicación
5. Verificar datos

**Si hay problemas de red**:
1. Verificar conexión física
2. Verificar firewall
3. Verificar IP del servidor
4. Reiniciar router/switch si es necesario

---

## 12. CONCLUSIÓN

Este documento proporciona toda la información necesaria para empaquetar e instalar el Sistema de Inventario Ferre-Exito v1.1 en un entorno de producción.

### Resumen de Requisitos Mínimos

**Hardware**:
- Procesador: Intel Core i3 o equivalente
- RAM: 4 GB (8 GB recomendado)
- Disco: 20 GB libres (50 GB recomendado)
- Red: Ethernet 100 Mbps

**Software**:
- Windows 10 Pro o Ubuntu 22.04 LTS
- Python 3.11 o superior
- 150 MB para dependencias

**Tiempo de Instalación**: 1.5 - 2.5 horas

**Costo Total Estimado**: $500 - $1,200 USD (hardware + software)

### Próximos Pasos

1. Verificar que el PC cumple los requisitos
2. Descargar/preparar el paquete de instalación
3. Seguir los pasos de instalación en orden
4. Completar el checklist de verificación
5. Capacitar a los usuarios
6. ¡Comenzar a usar el sistema!

---

**Documento generado**: 11 de Febrero de 2026  
**Versión del Sistema**: 1.1  
**Autor**: Sistema de Inventario Ferre-Exito  
**Estado**: ✅ LISTO PARA PRODUCCIÓN

Para más información, consultar:
- INFORME_PRODUCCION.md - Guía completa de producción
- RESUMEN_EJECUTIVO_PRODUCCION.md - Resumen ejecutivo
- CHECKLIST_INSTALACION.md - Lista de verificación
- README_PRODUCCION.md - Guía rápida
