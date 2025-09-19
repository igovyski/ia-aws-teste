#!/usr/bin/env python3
"""
Script para executar todos os testes do projeto
"""
import subprocess
import sys
import os

def run_tests():
    """Executa os testes automatizados"""
    print("🧪 Executando testes automatizados...")
    
    # Verificar se pytest está instalado
    try:
        import pytest
    except ImportError:
        print("❌ pytest não encontrado. Instalando...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pytest", "pytest-flask"])
    
    # Executar testes
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "tests/", 
        "-v", 
        "--tb=short"
    ], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("Erros:", result.stderr)
    
    if result.returncode == 0:
        print("✅ Todos os testes passaram!")
    else:
        print("❌ Alguns testes falharam.")
        sys.exit(1)

def check_code_quality():
    """Verifica qualidade do código"""
    print("\n🔍 Verificando qualidade do código...")
    
    # Verificar se flake8 está instalado
    try:
        subprocess.check_call([sys.executable, "-m", "flake8", "--version"], 
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("📦 Instalando flake8...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "flake8"])
    
    # Executar flake8
    result = subprocess.run([
        sys.executable, "-m", "flake8", 
        "src/", 
        "--max-line-length=100",
        "--ignore=E501,W503"
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Código está seguindo as boas práticas!")
    else:
        print("⚠️  Sugestões de melhoria:")
        print(result.stdout)

if __name__ == "__main__":
    run_tests()
    check_code_quality()
    print("\n🎉 Verificação completa!")