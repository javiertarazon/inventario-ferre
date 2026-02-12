# ✅ Checklist de Instalación en Producción
## Sistema de Inventario Ferre-Exito

---

## 📋 FASE 1: PREPARACIÓN (Antes de Instalar)

### Hardware
- [ ] Computadora/servidor cumple requisitos mínimos
  - [ ] Procesador: Core i3+ (recomendado i5)
  - [ ] RAM: 4 GB mínimo (recomendado 8 GB)
  - [ ] Disco: 10 GB libres (recomendado 50 GB SSD)
- [ ] UPS (respaldo eléctrico) disponible
- [ ] Red local configurada (si aplica)
- [ ] Conexión a internet estable

### Software Base
- [ ] Sistema operativo actualizado
  - [ ] Windows 10/11 o Windows Server, O
  - [ ] Linux Ubuntu 20.04+ o similar
- [ ] Antivirus actualizado (si aplica)
- [ ] Firewall configurado

### Documentos y Datos
- [ ] Archivo Excel con inventario actual
- [ ] Lista de proveedores
- [ ] Lista de clientes (si aplica)
- [ ] Tasa de cambio actual USD/Bs

---

## 📋 FASE 2: INSTALACIÓN DE SOFTWARE

### Python
- [ ] Python 3.10 o superior instalado
  - Descargar de: https://www.python.org/downloads/
  - [ ] Marcar "Add Python to PATH" durante instalación
- [ ] Verificar instalación: `python --version`
- [ ] Verificar pip: `pip --version`

### Código de la Aplicación
- [ ] Crear directorio: `C:\ferreteria-inventario` (Windows) o `/home/ferreteria/inventario` (Linux)
- [ ] Copiar todos los archivos del proyecto al directorio
- [ ] Verificar que existen estos archivos clave:
  - [ ] `app/` (carpeta)
  - [ ] `requirements.txt`
  - [ ] `wsgi.py`
  - [ ] `gunicorn_config.py`
  - [ ] `create_admin.py`
  - [ ] `.env.example`

### Entorno Virtual
- [ ] Crear entorno virtual: `python -m venv venv`
- [ ] Activar entorno virtual:
  - Windows: `venv\Scripts\activate`
  - Linux: `source venv/bin/activate`
- [ ] Verificar que el prompt cambió (debe mostrar `(venv)`)

### Dependencias Python
- [ ] Instalar dependencias: `pip install -r requirements.txt`
- [ ] Instalar Gunicorn: `pip install gunicorn`
- [ ] Verificar instalación: `pip list`

---

## 📋 FASE 3: CONFIGURACIÓN

### Variables de Entorno
- [ ] Copiar archivo de ejemplo: `copy .env.example .env` (Windows) o `cp .env.example .env` (Linux)
- [ ] Editar archivo `.env`:
  - [ ] Cambiar `FLASK_ENV=production`
  - [ ] Generar y configurar `SECRET_KEY` (usar: `python -c "import secrets; print(secrets.token_hex(32))"`)
  - [ ] Configurar `DATABASE_URL` (dejar SQLite por defecto o configurar PostgreSQL)
  - [ ] Revisar otras configuraciones

### Directorios
- [ ] Crear directorios necesarios:
  - [ ] `mkdir instance` (si no existe)
  - [ ] `mkdir logs`
  - [ ] `mkdir backups`
  - [ ] `mkdir uploads`

### Base de Datos
- [ ] Inicializar base de datos:
  ```bash
  python -c "from app import create_app, db; app = create_app('production'); app.app_context().push(); db.create_all()"
  ```
- [ ] Verificar que se creó: `instance/inventario.db`

### Usuario Administrador
- [ ] Ejecutar: `python create_admin.py`
- [ ] Ingresar datos del administrador:
  - [ ] Usuario (ej: admin)
  - [ ] Email (ej: admin@ferreteria.local)
  - [ ] Contraseña (mínimo 6 caracteres)
- [ ] Anotar credenciales en lugar seguro

---

## 📋 FASE 4: PRIMERA EJECUCIÓN

### Prueba Local
- [ ] Ejecutar aplicación: `gunicorn -c gunicorn_config.py wsgi:app`
- [ ] Verificar que inicia sin errores
- [ ] Abrir navegador en: `http://localhost:5000`
- [ ] Verificar que carga la página de login
- [ ] Iniciar sesión con usuario administrador
- [ ] Verificar que el dashboard carga correctamente

### Prueba de Funcionalidades Básicas
- [ ] Crear una categoría de prueba
- [ ] Crear un producto de prueba
- [ ] Registrar un movimiento de prueba
- [ ] Generar un reporte de prueba
- [ ] Verificar que todo funciona

### Detener Aplicación
- [ ] Presionar `Ctrl+C` para detener
- [ ] Verificar que se detuvo correctamente

---

## 📋 FASE 5: CONFIGURACIÓN DE PRODUCCIÓN

### Windows - Servicio Automático (Opcional)

#### Opción A: NSSM (Recomendado)
- [ ] Descargar NSSM: https://nssm.cc/download
- [ ] Instalar servicio:
  ```powershell
  nssm install FerreteriInventario "C:\ferreteria-inventario\venv\Scripts\gunicorn.exe" "-c gunicorn_config.py wsgi:app"
  nssm set FerreteriInventario AppDirectory "C:\ferreteria-inventario"
  nssm start FerreteriInventario
  ```
- [ ] Verificar servicio: `nssm status FerreteriInventario`

#### Opción B: Programador de Tareas
- [ ] Crear tarea que ejecute al inicio
- [ ] Programa: `C:\ferreteria-inventario\venv\Scripts\gunicorn.exe`
- [ ] Argumentos: `-c gunicorn_config.py wsgi:app`
- [ ] Directorio: `C:\ferreteria-inventario`

### Linux - Servicio Systemd
- [ ] Crear archivo de servicio: `sudo nano /etc/systemd/system/ferreteria-inventario.service`
- [ ] Copiar configuración (ver `INFORME_PRODUCCION.md` sección 6.2)
- [ ] Recargar systemd: `sudo systemctl daemon-reload`
- [ ] Habilitar servicio: `sudo systemctl enable ferreteria-inventario`
- [ ] Iniciar servicio: `sudo systemctl start ferreteria-inventario`
- [ ] Verificar estado: `sudo systemctl status ferreteria-inventario`

### Firewall
- [ ] Permitir puerto 5000:
  - Windows: Configurar en "Firewall de Windows Defender"
  - Linux: `sudo ufw allow 5000/tcp`
- [ ] Verificar que otras computadoras pueden acceder

---

## 📋 FASE 6: RESPALDOS

### Configurar Respaldos Automáticos

#### Windows
- [ ] Dar permisos de ejecución a `backup.bat`
- [ ] Probar manualmente: `backup.bat`
- [ ] Verificar que se creó respaldo en `backups/`
- [ ] Configurar Programador de Tareas:
  - [ ] Crear tarea básica
  - [ ] Nombre: "Respaldo Inventario"
  - [ ] Desencadenador: Diario a las 2:00 AM
  - [ ] Acción: Iniciar programa `C:\ferreteria-inventario\backup.bat`

#### Linux
- [ ] Dar permisos: `chmod +x backup.sh`
- [ ] Probar manualmente: `./backup.sh`
- [ ] Verificar que se creó respaldo en `backups/`
- [ ] Configurar cron: `crontab -e`
- [ ] Agregar línea: `0 2 * * * /ruta/al/proyecto/backup.sh >> /ruta/al/proyecto/logs/backup.log 2>&1`

### Probar Restauración
- [ ] Detener aplicación
- [ ] Restaurar desde respaldo de prueba
- [ ] Iniciar aplicación
- [ ] Verificar que los datos están correctos

---

## 📋 FASE 7: CARGA DE DATOS

### Categorías
- [ ] Verificar que existen las 7 categorías:
  - [ ] Electricidad
  - [ ] Plomeria
  - [ ] Albañileria
  - [ ] Carpinteria
  - [ ] Herreria
  - [ ] Tornilleria
  - [ ] Miselaneos
- [ ] Si no existen, ejecutar: `python create_categories.py`

### Importar Inventario
- [ ] Preparar archivo Excel con columnas:
  - Descripcion del Articulo
  - Categoria
  - Cantidad Unid/kg
  - Precio Venta $
- [ ] Ir a "Cargar Inventario" en la aplicación
- [ ] Seleccionar archivo Excel
- [ ] Importar
- [ ] Verificar que se importaron correctamente
- [ ] Revisar errores si los hay

### Proveedores
- [ ] Crear proveedores principales
- [ ] Asignar proveedores a productos (si aplica)

### Clientes (Opcional)
- [ ] Crear clientes principales
- [ ] Verificar información de contacto

### Tasa de Cambio
- [ ] Ir a "Configuración de Precios"
- [ ] Actualizar tasa de cambio USD/Bs actual
- [ ] Verificar que los precios se calculan correctamente

---

## 📋 FASE 8: CAPACITACIÓN

### Administrador
- [ ] Explicar estructura del sistema
- [ ] Mostrar gestión de usuarios
- [ ] Enseñar respaldos y restauración
- [ ] Explicar logs y monitoreo
- [ ] Revisar solución de problemas comunes

### Personal Operativo
- [ ] Mostrar navegación básica
- [ ] Enseñar gestión de productos
- [ ] Explicar registro de movimientos
- [ ] Mostrar generación de reportes
- [ ] Practicar importación de Excel

### Documentación Entregada
- [ ] `INFORME_PRODUCCION.md`
- [ ] `README_PRODUCCION.md`
- [ ] `RESUMEN_EJECUTIVO_PRODUCCION.md`
- [ ] Este checklist
- [ ] Credenciales de acceso (en sobre sellado)

---

## 📋 FASE 9: PRUEBAS FINALES

### Funcionalidad
- [ ] Crear producto nuevo
- [ ] Editar producto existente
- [ ] Eliminar producto (soft delete)
- [ ] Registrar entrada de inventario
- [ ] Registrar salida de inventario
- [ ] Crear orden de venta
- [ ] Generar reporte de inventario
- [ ] Exportar a Excel
- [ ] Importar desde Excel
- [ ] Buscar productos
- [ ] Filtrar por categoría

### Rendimiento
- [ ] Verificar tiempo de carga de páginas (< 2 segundos)
- [ ] Probar con múltiples usuarios simultáneos
- [ ] Verificar búsquedas rápidas

### Seguridad
- [ ] Intentar acceder sin login (debe redirigir)
- [ ] Verificar que solo admin puede gestionar usuarios
- [ ] Probar límite de intentos de login
- [ ] Verificar que las sesiones expiran

### Red (si aplica)
- [ ] Acceder desde otra computadora en la red
- [ ] Verificar velocidad de respuesta
- [ ] Probar con múltiples usuarios

---

## 📋 FASE 10: PUESTA EN PRODUCCIÓN

### Día 1 - Operación Paralela
- [ ] Sistema viejo y nuevo funcionando simultáneamente
- [ ] Registrar operaciones en ambos sistemas
- [ ] Comparar resultados al final del día
- [ ] Corregir discrepancias

### Día 2-7 - Monitoreo Intensivo
- [ ] Revisar logs diariamente
- [ ] Resolver problemas inmediatamente
- [ ] Recopilar feedback del personal
- [ ] Hacer ajustes necesarios

### Día 8+ - Operación Normal
- [ ] Desactivar sistema viejo
- [ ] Operación 100% en nuevo sistema
- [ ] Monitoreo regular
- [ ] Soporte continuo

---

## 📋 MANTENIMIENTO CONTINUO

### Diario
- [ ] Verificar que el respaldo automático se ejecutó
- [ ] Revisar logs de errores (si hay)

### Semanal
- [ ] Verificar espacio en disco
- [ ] Revisar rendimiento general
- [ ] Limpiar archivos temporales

### Mensual
- [ ] Actualizar tasa de cambio
- [ ] Revisar usuarios activos
- [ ] Optimizar base de datos: `sqlite3 instance/inventario.db "VACUUM;"`
- [ ] Probar restauración de respaldo
- [ ] Actualizar documentación si hay cambios

### Trimestral
- [ ] Actualizar dependencias de seguridad
- [ ] Revisar y actualizar contraseñas
- [ ] Auditoría de usuarios y permisos
- [ ] Planificar mejoras

---

## ✅ VERIFICACIÓN FINAL

Antes de considerar la instalación completa, verificar:

- [ ] ✅ Aplicación inicia automáticamente al encender el servidor
- [ ] ✅ Accesible desde todas las computadoras de la red
- [ ] ✅ Respaldos automáticos funcionando
- [ ] ✅ Personal capacitado y cómodo con el sistema
- [ ] ✅ Datos migrados correctamente
- [ ] ✅ Documentación entregada
- [ ] ✅ Contacto de soporte establecido
- [ ] ✅ Plan de mantenimiento definido

---

## 🎉 ¡INSTALACIÓN COMPLETADA!

Si todos los items están marcados, el sistema está listo para operación en producción.

**Fecha de instalación**: _______________
**Instalado por**: _______________
**Verificado por**: _______________

---

**Documento**: Checklist de Instalación
**Versión**: 1.0
**Fecha**: 11 de Febrero de 2026
