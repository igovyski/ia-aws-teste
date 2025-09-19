@echo off
echo Iniciando Race Photo Marketplace...

echo Instalando dependências...
py -m pip install Flask Werkzeug Flask-Login python-dotenv

echo Inicializando banco de dados...
py src\app.py init-db

echo Iniciando servidor...
echo Acesse: http://localhost:5000
py src\app.py

pause