import pytest
import tempfile
import os
from src.app import app, init_db, get_db_connection

@pytest.fixture
def client():
    # Criar banco de dados temporário para testes
    db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            init_db()
        yield client
    
    os.close(db_fd)
    os.unlink(app.config['DATABASE'])

def test_index_page(client):
    """Testa se a página inicial carrega corretamente"""
    rv = client.get('/')
    assert rv.status_code == 200
    assert b'Race Photos' in rv.data
    assert b'Encontre suas fotos de corrida' in rv.data

def test_login_page(client):
    """Testa se a página de login carrega corretamente"""
    rv = client.get('/login')
    assert rv.status_code == 200
    assert b'Login' in rv.data

def test_login_success(client):
    """Testa login com credenciais válidas"""
    rv = client.post('/login', data={
        'email': 'admin@example.com',
        'password': 'admin123'
    }, follow_redirects=True)
    assert rv.status_code == 200
    assert b'Sair' in rv.data  # Verifica se o link de logout aparece

def test_login_failure(client):
    """Testa login com credenciais inválidas"""
    rv = client.post('/login', data={
        'email': 'wrong@example.com',
        'password': 'wrongpass'
    })
    assert rv.status_code == 200
    assert b'Email ou senha incorretos' in rv.data

def test_search_page(client):
    """Testa a página de busca"""
    rv = client.get('/search')
    assert rv.status_code == 200
    assert b'Buscar Fotos' in rv.data

def test_search_with_number(client):
    """Testa busca por número do peito"""
    rv = client.get('/search?runner_number=123')
    assert rv.status_code == 200
    assert b'Resultados para: #123' in rv.data

def test_cart_requires_login(client):
    """Testa se o carrinho requer login"""
    rv = client.get('/cart')
    assert rv.status_code == 302  # Redirect para login

def test_admin_requires_login(client):
    """Testa se o admin requer login"""
    rv = client.get('/admin')
    assert rv.status_code == 302  # Redirect para login

def test_admin_access_with_admin_user(client):
    """Testa acesso ao admin com usuário administrador"""
    # Fazer login como admin
    client.post('/login', data={
        'email': 'admin@example.com',
        'password': 'admin123'
    })
    
    rv = client.get('/admin')
    assert rv.status_code == 200
    assert b'Painel Administrativo' in rv.data

def test_create_event(client):
    """Testa criação de evento"""
    # Fazer login como admin
    client.post('/login', data={
        'email': 'admin@example.com',
        'password': 'admin123'
    })
    
    rv = client.post('/admin/create_event', data={
        'name': 'Corrida Teste',
        'date': '2024-12-31',
        'location': 'São Paulo'
    }, follow_redirects=True)
    
    assert rv.status_code == 200
    assert b'Evento criado com sucesso!' in rv.data

def test_database_initialization():
    """Testa se o banco de dados é inicializado corretamente"""
    # Criar banco temporário
    db_fd, db_path = tempfile.mkstemp()
    
    # Configurar app para usar banco temporário
    original_db = app.config.get('DATABASE')
    app.config['DATABASE'] = db_path
    
    try:
        with app.app_context():
            init_db()
            
            # Verificar se as tabelas foram criadas
            conn = get_db_connection()
            tables = conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
            """).fetchall()
            
            table_names = [table['name'] for table in tables]
            expected_tables = ['users', 'events', 'photos', 'cart_items']
            
            for table in expected_tables:
                assert table in table_names
            
            # Verificar se usuários padrão foram criados
            admin = conn.execute(
                'SELECT * FROM users WHERE email = ?', 
                ('admin@example.com',)
            ).fetchone()
            assert admin is not None
            assert admin['is_admin'] == True
            
            client = conn.execute(
                'SELECT * FROM users WHERE email = ?', 
                ('cliente@example.com',)
            ).fetchone()
            assert client is not None
            assert client['is_admin'] == False
            
            conn.close()
    
    finally:
        # Limpar
        os.close(db_fd)
        os.unlink(db_path)
        if original_db:
            app.config['DATABASE'] = original_db

if __name__ == '__main__':
    pytest.main([__file__])