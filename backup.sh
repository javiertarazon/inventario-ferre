#!/bin/bash

###############################################################################
# Script de Respaldo Automático para Sistema de Inventario
# Uso: ./backup.sh
###############################################################################

# Configuración
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_DIR="${SCRIPT_DIR}/backups"
DB_PATH="${SCRIPT_DIR}/instance/inventario.db"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30
LOG_FILE="${SCRIPT_DIR}/logs/backup.log"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función de logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

# Verificar que existe la base de datos
if [ ! -f "$DB_PATH" ]; then
    log_error "Base de datos no encontrada: $DB_PATH"
    exit 1
fi

# Crear directorio de respaldos si no existe
mkdir -p "$BACKUP_DIR"
mkdir -p "$(dirname "$LOG_FILE")"

log "Iniciando respaldo..."

# Nombre del archivo de respaldo
BACKUP_FILE="${BACKUP_DIR}/inventario_${DATE}.db"

# Respaldar base de datos
log "Copiando base de datos..."
if cp "$DB_PATH" "$BACKUP_FILE"; then
    log_success "Base de datos copiada: $BACKUP_FILE"
else
    log_error "Error al copiar base de datos"
    exit 1
fi

# Comprimir respaldo
log "Comprimiendo respaldo..."
if gzip "$BACKUP_FILE"; then
    log_success "Respaldo comprimido: ${BACKUP_FILE}.gz"
    BACKUP_SIZE=$(du -h "${BACKUP_FILE}.gz" | cut -f1)
    log "Tamaño del respaldo: $BACKUP_SIZE"
else
    log_error "Error al comprimir respaldo"
    exit 1
fi

# Eliminar respaldos antiguos
log "Eliminando respaldos antiguos (más de $RETENTION_DAYS días)..."
DELETED_COUNT=$(find "$BACKUP_DIR" -name "inventario_*.db.gz" -mtime +$RETENTION_DAYS -delete -print | wc -l)
if [ "$DELETED_COUNT" -gt 0 ]; then
    log_warning "Eliminados $DELETED_COUNT respaldos antiguos"
else
    log "No hay respaldos antiguos para eliminar"
fi

# Contar respaldos totales
TOTAL_BACKUPS=$(find "$BACKUP_DIR" -name "inventario_*.db.gz" | wc -l)
log "Total de respaldos disponibles: $TOTAL_BACKUPS"

# Calcular espacio usado
BACKUP_DIR_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
log "Espacio usado por respaldos: $BACKUP_DIR_SIZE"

log_success "Respaldo completado exitosamente"

# Opcional: Enviar respaldo a ubicación remota
# Descomentar y configurar según necesidad
# rsync -avz "${BACKUP_FILE}.gz" usuario@servidor:/ruta/respaldos/

exit 0
