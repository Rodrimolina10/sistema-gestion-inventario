#!/usr/bin/env python
"""
Sistema de Gestión de Inventario - API REST
Versión 2.0 - Modernizado
"""
import sys
import os

# Limpiar caché de módulos importados
if 'api' in sys.modules:
    del sys.modules['api']
for module in list(sys.modules.keys()):
    if module.startswith('api.'):
        del sys.modules[module]

from api import app

def print_banner():
    """Imprime el banner de inicio del servidor"""
    banner = """
    ╔════════════════════════════════════════════════════════════╗
    ║   Sistema de Gestión de Inventario - API REST             ║
    ║   Versión 2.0 - Modernizado                              ║
    ╠════════════════════════════════════════════════════════════╣
    ║   Servidor: http://localhost:5000                   ║
    ║   Documentación: http://localhost:5000/          ║
    ║   Estado: ONLINE ✅                                        ║
    ╚════════════════════════════════════════════════════════════╝
    """
    print(banner)

if __name__ == '__main__':
    print_banner()
    # Deshabilitar reloader para forzar uso del código nuevo
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)