#!/bin/bash

echo "🔧 Iniciando Sistema de Ferretería con Normativa SENIAT"
echo "========================================================"

# Función para verificar si un puerto está en uso
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        return 0
    else
        return 1
    fi
}

# Detener procesos existentes en los puertos
echo "📋 Verificando puertos..."
if check_port 5000; then
    echo "⚠️  Puerto 5000 en uso, liberando..."
    kill $(lsof -t -i:5000) 2>/dev/null || true
fi

if check_port 5173; then
    echo "⚠️  Puerto 5173 en uso, liberando..."
    kill $(lsof -t -i:5173) 2>/dev/null || true
fi

sleep 2

# Iniciar Backend
echo ""
echo "🚀 Iniciando Backend (FastAPI)..."
echo "   Servidor: http://localhost:5000"
echo "   Documentación API: http://localhost:5000/docs"
cd /workspace/backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload &
BACKEND_PID=$!
cd /workspace

sleep 3

# Verificar si el backend inició correctamente
if ps -p $BACKEND_PID > /dev/null; then
    echo "✅ Backend iniciado exitosamente (PID: $BACKEND_PID)"
else
    echo "❌ Error al iniciar el backend"
    exit 1
fi

# Iniciar Frontend
echo ""
echo "🎨 Iniciando Frontend (React + Vite)..."
echo "   Aplicación: http://localhost:5173"
cd /workspace/frontend
npm run dev -- --host 0.0.0.0 --port 5173 &
FRONTEND_PID=$!
cd /workspace

sleep 5

# Verificar si el frontend inició correctamente
if ps -p $FRONTEND_PID > /dev/null; then
    echo "✅ Frontend iniciado exitosamente (PID: $FRONTEND_PID)"
else
    echo "❌ Error al iniciar el frontend"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo ""
echo "========================================================"
echo "✨ SISTEMA COMPLETAMENTE INICIADO"
echo "========================================================"
echo ""
echo "📱 Accesos:"
echo "   🌐 Frontend: http://localhost:5173"
echo "   🔌 API Docs: http://localhost:5000/docs"
echo "   💾 Backend:  http://localhost:5000"
echo ""
echo "🔐 Credenciales por defecto:"
echo "   Email: admin@ferreteria.com"
echo "   Password: admin123"
echo ""
echo "📊 Características activas:"
echo "   ✅ Tasa BCV automática con 3 reintentos"
echo "   ✅ Sistema bimonetario USD/VES"
echo "   ✅ Cálculo IVA (16%, 8%, exento) e IGTF (3%)"
echo "   ✅ Validación de RIF venezolano"
echo "   ✅ Roles: Admin, Cajero, Almacénista"
echo "   ✅ Auditoría de acciones"
echo "   ✅ Responsive (PC, Tablet, Móvil)"
echo ""
echo "🛑 Para detener el sistema presiona: Ctrl+C"
echo "========================================================"

# Esperar a que el usuario interrumpa
wait
