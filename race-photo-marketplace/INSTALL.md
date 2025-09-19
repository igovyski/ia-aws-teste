# Guia de Instalação

## Problema com Python no Windows

Se você está vendo a mensagem "Python was not found", siga estes passos:

### Opção 1: Desabilitar alias do Windows Store
1. Abra **Configurações** do Windows
2. Vá em **Apps** > **Configurações avançadas de aplicativos** > **Aliases de execução de aplicativo**
3. Desative os aliases para **python.exe** e **python3.exe**

### Opção 2: Usar caminho completo do Python
Se você tem Python instalado, encontre o caminho:
```cmd
where python
```

Então execute:
```cmd
"C:\caminho\para\python.exe" run.py
```

### Opção 3: Instalar Python corretamente
1. Baixe Python de https://python.org
2. Durante a instalação, marque **"Add Python to PATH"**
3. Reinicie o terminal

## Executando a aplicação

Depois de resolver o Python:

```cmd
# Instalar dependências
pip install Flask Werkzeug Flask-Login python-dotenv

# Executar aplicação
python run.py
```

Acesse: http://localhost:5000

**Usuários de teste:**
- Admin: admin@example.com / admin123
- Cliente: cliente@example.com / cliente123