from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from PIL import Image
import uuid
from datetime import datetime
from aws_mcp_service import aws_mcp
import json

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'static/photos'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Configuração do Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, email, name, is_admin=False):
        self.id = id
        self.email = email
        self.name = name
        self.is_admin = is_admin

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    if user:
        return User(user['id'], user['email'], user['name'], user['is_admin'])
    return None

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    
    # Tabela de usuários
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            is_admin BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de eventos
    conn.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            date TEXT NOT NULL,
            location TEXT NOT NULL,
            photographer_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (photographer_id) REFERENCES users (id)
        )
    ''')
    
    # Tabela de fotos
    conn.execute('''
        CREATE TABLE IF NOT EXISTS photos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            event_id INTEGER NOT NULL,
            runner_number TEXT,
            price REAL DEFAULT 15.00,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (event_id) REFERENCES events (id)
        )
    ''')
    
    # Tabela de carrinho
    conn.execute('''
        CREATE TABLE IF NOT EXISTS cart_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            photo_id INTEGER NOT NULL,
            quantity INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (photo_id) REFERENCES photos (id)
        )
    ''')
    
    # Criar usuário admin padrão
    admin_exists = conn.execute('SELECT id FROM users WHERE email = ?', ('admin@example.com',)).fetchone()
    if not admin_exists:
        conn.execute('''
            INSERT INTO users (email, password_hash, name, is_admin)
            VALUES (?, ?, ?, ?)
        ''', ('admin@example.com', generate_password_hash('admin123'), 'Administrador', True))
    
    # Criar usuário cliente padrão
    client_exists = conn.execute('SELECT id FROM users WHERE email = ?', ('cliente@example.com',)).fetchone()
    if not client_exists:
        conn.execute('''
            INSERT INTO users (email, password_hash, name, is_admin)
            VALUES (?, ?, ?, ?)
        ''', ('cliente@example.com', generate_password_hash('cliente123'), 'Cliente Teste', False))
    
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = get_db_connection()
    events = conn.execute('''
        SELECT e.*, u.name as photographer_name,
               COUNT(p.id) as photo_count
        FROM events e
        LEFT JOIN users u ON e.photographer_id = u.id
        LEFT JOIN photos p ON e.id = p.event_id
        GROUP BY e.id
        ORDER BY e.date DESC
    ''').fetchall()
    conn.close()
    return render_template('index.html', events=events)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            user_obj = User(user['id'], user['email'], user['name'], user['is_admin'])
            login_user(user_obj)
            return redirect(url_for('index'))
        else:
            flash('Email ou senha incorretos')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/event/<int:event_id>')
def event_photos(event_id):
    conn = get_db_connection()
    event = conn.execute('SELECT * FROM events WHERE id = ?', (event_id,)).fetchone()
    photos = conn.execute('SELECT * FROM photos WHERE event_id = ?', (event_id,)).fetchall()
    conn.close()
    
    if not event:
        flash('Evento não encontrado')
        return redirect(url_for('index'))
    
    return render_template('event_photos.html', event=event, photos=photos)

@app.route('/search')
def search():
    runner_number = request.args.get('runner_number', '')
    event_id = request.args.get('event_id', '')
    
    if not runner_number:
        return render_template('search.html', photos=[], runner_number='')
    
    conn = get_db_connection()
    query = '''
        SELECT p.*, e.name as event_name, e.date as event_date
        FROM photos p
        JOIN events e ON p.event_id = e.id
        WHERE p.runner_number LIKE ?
    '''
    params = [f'%{runner_number}%']
    
    if event_id:
        query += ' AND p.event_id = ?'
        params.append(event_id)
    
    photos = conn.execute(query, params).fetchall()
    conn.close()
    
    return render_template('search.html', photos=photos, runner_number=runner_number)

@app.route('/add_to_cart/<int:photo_id>')
@login_required
def add_to_cart(photo_id):
    conn = get_db_connection()
    
    # Verificar se já existe no carrinho
    existing = conn.execute('''
        SELECT id FROM cart_items 
        WHERE user_id = ? AND photo_id = ?
    ''', (current_user.id, photo_id)).fetchone()
    
    if existing:
        flash('Foto já está no carrinho!')
    else:
        conn.execute('''
            INSERT INTO cart_items (user_id, photo_id)
            VALUES (?, ?)
        ''', (current_user.id, photo_id))
        conn.commit()
        flash('Foto adicionada ao carrinho!')
    
    conn.close()
    return redirect(request.referrer or url_for('index'))

@app.route('/cart')
@login_required
def cart():
    conn = get_db_connection()
    items = conn.execute('''
        SELECT ci.*, p.filename, p.price, e.name as event_name
        FROM cart_items ci
        JOIN photos p ON ci.photo_id = p.id
        JOIN events e ON p.event_id = e.id
        WHERE ci.user_id = ?
    ''', (current_user.id,)).fetchall()
    
    total = sum(item['price'] for item in items)
    conn.close()
    
    return render_template('cart.html', items=items, total=total)

@app.route('/remove_from_cart/<int:item_id>')
@login_required
def remove_from_cart(item_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM cart_items WHERE id = ? AND user_id = ?', (item_id, current_user.id))
    conn.commit()
    conn.close()
    flash('Item removido do carrinho!')
    return redirect(url_for('cart'))

@app.route('/checkout')
@login_required
def checkout():
    # Simulação de checkout
    conn = get_db_connection()
    conn.execute('DELETE FROM cart_items WHERE user_id = ?', (current_user.id,))
    conn.commit()
    conn.close()
    flash('Compra realizada com sucesso! Você receberá as fotos por email.')
    return redirect(url_for('index'))

# Rotas administrativas
@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        flash('Acesso negado')
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    events = conn.execute('SELECT * FROM events ORDER BY date DESC').fetchall()
    conn.close()
    
    return render_template('admin.html', events=events)

@app.route('/admin/create_event', methods=['POST'])
@login_required
def create_event():
    if not current_user.is_admin:
        return redirect(url_for('index'))
    
    name = request.form['name']
    date = request.form['date']
    location = request.form['location']
    
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO events (name, date, location, photographer_id)
        VALUES (?, ?, ?, ?)
    ''', (name, date, location, current_user.id))
    conn.commit()
    conn.close()
    
    flash('Evento criado com sucesso!')
    return redirect(url_for('admin'))

@app.route('/admin/upload_photo', methods=['POST'])
@login_required
def upload_photo():
    if not current_user.is_admin:
        return redirect(url_for('admin'))
    
    if 'photo' not in request.files:
        flash('Nenhuma foto selecionada')
        return redirect(url_for('admin'))
    
    file = request.files['photo']
    event_id = request.form['event_id']
    
    if file.filename == '':
        flash('Nenhuma foto selecionada')
        return redirect(url_for('admin'))
    
    if file:
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        # Usar AWS MCP para detectar números automaticamente
        try:
            # Detectar números de peito usando AWS Rekognition
            detection_result = aws_mcp.detect_runner_numbers(file_path)
            
            runner_numbers = []
            if detection_result.get('success') and detection_result.get('numbers'):
                runner_numbers = [item['number'] for item in detection_result['numbers']]
            
            # Analisar qualidade da foto
            quality_result = aws_mcp.analyze_photo_quality(file_path)
            
            # Informações básicas da imagem
            image_info = aws_mcp.get_basic_image_info(file_path)
            
            # Salvar no banco
            conn = get_db_connection()
            runner_number_str = ','.join(runner_numbers) if runner_numbers else request.form.get('runner_number', '')
            
            conn.execute('''
                INSERT INTO photos (filename, event_id, runner_number, price)
                VALUES (?, ?, ?, ?)
            ''', (unique_filename, event_id, runner_number_str, 15.00))
            conn.commit()
            conn.close()
            
            if runner_numbers:
                flash(f'Foto enviada! Números detectados automaticamente: {", ".join(runner_numbers)}')
            elif detection_result.get('error'):
                flash(f'Foto enviada! Erro na detecção: {detection_result["error"]}')
            else:
                flash('Foto enviada! Nenhum número detectado automaticamente.')
                
        except Exception as e:
            flash(f'Foto enviada, mas erro na detecção automática: {str(e)}')
    
    return redirect(url_for('admin'))

@app.route('/api/mcp/detect_numbers', methods=['POST'])
@login_required
def api_detect_numbers():
    """API endpoint para detecção de números via AWS MCP"""
    if not current_user.is_admin:
        return jsonify({'error': 'Acesso negado'}), 403
    
    data = request.get_json()
    image_path = data.get('image_path')
    
    if not image_path:
        return jsonify({'error': 'Caminho da imagem não fornecido'}), 400
    
    try:
        result = aws_mcp.detect_runner_numbers(image_path)
        return jsonify(result)
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    # Criar diretório de uploads se não existir
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Inicializar banco de dados
    if len(os.sys.argv) > 1 and os.sys.argv[1] == 'init-db':
        init_db()
        print("Banco de dados inicializado!")
    else:
        init_db()  # Sempre inicializar na primeira execução
        
        # Inicializar AWS MCP
        if aws_mcp.aws_available:
            print("AWS MCP disponível!")
        else:
            print("AWS MCP não configurado - funcionalidades limitadas")
        
        app.run(debug=True)