@echo off
echo Iniciando Race Photo Marketplace...

echo Instalando dependências...
python -m pip install -r requirements.txt

echo Inicializando banco de dados...
python src\app.py init-db

echo Iniciando servidor...
echo Acesse: http://localhost:5000
python src\app.py

pause