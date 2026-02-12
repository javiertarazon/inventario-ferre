@echo off
REM ###############################################################################
REM Script de Respaldo Automático para Sistema de Inventario (Windows)
REM Uso: backup.bat
REM ###############################################################################

setlocal enabledelayedexpansion

REM Configuración
set SCRIPT_DIR=%~dp0
set BACKUP_DIR=%SCRIPT_DIR%backups
set DB_PATH=%SCRIPT_DIR%instance\inventario.db
set DATE_TIME=%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set DATE_TIME=%DATE_TIME: =0%
set RETENTION_DAYS=30
set LOG_FILE=%SCRIPT_DIR%logs\backup.log

REM Crear directorios si no existen
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"
if not exist "%SCRIPT_DIR%logs" mkdir "%SCRIPT_DIR%logs"

REM Función de logging
call :log "Iniciando respaldo..."

REM Verificar que existe la base de datos
if not exist "%DB_PATH%" (
    call :log_error "Base de datos no encontrada: %DB_PATH%"
    exit /b 1
)

REM Nombre del archivo de respaldo
set BACKUP_FILE=%BACKUP_DIR%\inventario_%DATE_TIME%.db

REM Respaldar base de datos
call :log "Copiando base de datos..."
copy "%DB_PATH%" "%BACKUP_FILE%" >nul 2>&1
if errorlevel 1 (
    call :log_error "Error al copiar base de datos"
    exit /b 1
)
call :log_success "Base de datos copiada: %BACKUP_FILE%"

REM Comprimir respaldo (requiere 7-Zip instalado)
if exist "C:\Program Files\7-Zip\7z.exe" (
    call :log "Comprimiendo respaldo..."
    "C:\Program Files\7-Zip\7z.exe" a -tgzip "%BACKUP_FILE%.gz" "%BACKUP_FILE%" >nul 2>&1
    if errorlevel 1 (
        call :log_error "Error al comprimir respaldo"
    ) else (
        del "%BACKUP_FILE%"
        call :log_success "Respaldo comprimido: %BACKUP_FILE%.gz"
    )
) else (
    call :log_warning "7-Zip no encontrado, respaldo sin comprimir"
)

REM Eliminar respaldos antiguos (más de RETENTION_DAYS días)
call :log "Eliminando respaldos antiguos (más de %RETENTION_DAYS% días)..."
forfiles /P "%BACKUP_DIR%" /M inventario_*.db* /D -%RETENTION_DAYS% /C "cmd /c del @path" 2>nul
if errorlevel 1 (
    call :log "No hay respaldos antiguos para eliminar"
) else (
    call :log_warning "Respaldos antiguos eliminados"
)

REM Contar respaldos totales
set COUNT=0
for %%f in ("%BACKUP_DIR%\inventario_*.db*") do set /a COUNT+=1
call :log "Total de respaldos disponibles: %COUNT%"

call :log_success "Respaldo completado exitosamente"

exit /b 0

REM Funciones de logging
:log
echo [%date% %time%] %~1 >> "%LOG_FILE%"
echo [%date% %time%] %~1
exit /b 0

:log_error
echo [%date% %time%] [ERROR] %~1 >> "%LOG_FILE%"
echo [ERROR] %~1
exit /b 0

:log_success
echo [%date% %time%] [OK] %~1 >> "%LOG_FILE%"
echo [OK] %~1
exit /b 0

:log_warning
echo [%date% %time%] [WARNING] %~1 >> "%LOG_FILE%"
echo [WARNING] %~1
exit /b 0
