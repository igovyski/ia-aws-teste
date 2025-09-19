#!/usr/bin/env python
import os
import sys
import subprocess

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Instalar dependências
try:
    import flask
except ImportError:
    print("Instalando dependências...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Flask", "Werkzeug", "Flask-Login", "python-dotenv"])

# Importar e executar app
from app import app, init_db

if __name__ == '__main__':
    print("Inicializando banco de dados...")
    init_db()
    print("Iniciando servidor...")
    print("Acesse: http://localhost:5000")
    print("Login admin: admin@example.com / admin123")
    print("Login cliente: cliente@example.com / cliente123")
    app.run(debug=True, host='0.0.0.0', port=5000)