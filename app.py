from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

app = Flask(__name__)

# Chave secreta protegida e puxada de forma segura pelo .env
app.secret_key = os.getenv('SECRET_KEY')

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Tabela de Denúncias
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS denuncias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cpf TEXT NOT NULL,
            localizacao TEXT NOT NULL,
            bairro TEXT NOT NULL,
            descricao TEXT NOT NULL,
            foto_path TEXT,
            status TEXT DEFAULT 'Pendente',
            latitude REAL,
            longitude REAL
        )
    ''')
    try:
        cursor.execute('ALTER TABLE denuncias ADD COLUMN latitude REAL')
    except sqlite3.OperationalError:
        pass
        
    try:
        cursor.execute('ALTER TABLE denuncias ADD COLUMN longitude REAL')
    except sqlite3.OperationalError:
        pass

    # Tabela nova para armazenar os Reparos / Feedbacks de melhoria dos cidadãos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reparos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            localizacao TEXT NOT NULL,
            bairro TEXT NOT NULL,
            descricao TEXT NOT NULL,
            foto_path TEXT,
            status TEXT DEFAULT 'Aguardando Validação'
        )
    ''')

    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/denuncia', methods=['GET', 'POST'])
def denuncia():
    if request.method == 'POST':
        nome = request.form.get('nome')
        cpf = request.form.get('cpf')
        localizacao = request.form.get('localizacao')
        bairro = request.form.get('bairro')
        descricao = request.form.get('descricao')
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        
        lat = float(latitude) if latitude else None
        lon = float(longitude) if longitude else None
        
        foto = request.files.get('foto')
        foto_path = None
        if foto and foto.filename != '':
            foto_path = os.path.join(app.config['UPLOAD_FOLDER'], foto.filename)
            foto.save(foto_path)

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO denuncias (nome, cpf, localizacao, bairro, descricao, foto_path, latitude, longitude)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (nome, cpf, localizacao, bairro, descricao, foto_path, lat, lon))
        conn.commit()
        conn.close()

        return redirect(url_for('painel'))

    return render_template('denuncia.html')

# --- ROTA PARA O RELATAR REPARO ---
@app.route('/reparo', methods=['GET', 'POST'])
def reparo():
    if request.method == 'POST':
        localizacao = request.form.get('localizacao')
        bairro = request.form.get('bairro')
        descricao = request.form.get('descricao')
        
        foto = request.files.get('foto')
        foto_path = None
        if foto and foto.filename != '':
            foto_path = os.path.join(app.config['UPLOAD_FOLDER'], 'reparo_' + foto.filename)
            foto.save(foto_path)

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO reparos (localizacao, bairro, descricao, foto_path)
            VALUES (?, ?, ?, ?)
        ''', (localizacao, bairro, descricao, foto_path))
        conn.commit()
        conn.close()

        return redirect(url_for('index'))

    return render_template('reparo.html')

# --- PAINEL PÚBLICO ---
@app.route('/painel')
def painel():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT bairro, COUNT(*) as total FROM denuncias GROUP BY bairro ORDER BY total DESC')
    ranking_bairros = cursor.fetchall()
    
    cursor.execute('SELECT id, localizacao, bairro, descricao, foto_path, status, latitude, longitude FROM denuncias ORDER BY id DESC')
    denuncias = cursor.fetchall()
    
    conn.close()
    return render_template('painel.html', denuncias=denuncias, ranking_bairros=ranking_bairros)

# --- ROTAS DE AUTENTICAÇÃO E ADMINISTRAÇÃO (COM AS 3 ABAS) ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    erro = None
    if request.method == 'POST':
        senha_digitada = request.form.get('senha')
        senha_correta = os.getenv('ADMIN_SENHA')
        
        if senha_digitada == senha_correta:
            session['admin_logado'] = True
            return redirect(url_for('admin_ocorrencias'))
        else:
            erro = 'Senha incorreta. Tente novamente.'
    return render_template('login.html', erro=erro)

@app.route('/logout')
def logout():
    session.pop('admin_logado', None)
    return redirect(url_for('login'))

# Aba 1: Novas Ocorrências (Gerenciamento de buracos)
@app.route('/admin')
@app.route('/admin/ocorrencias')
def admin_ocorrencias():
    if not session.get('admin_logado'):
        return redirect(url_for('login'))

    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT id, nome, cpf, localizacao, bairro, descricao, foto_path, status, latitude, longitude FROM denuncias ORDER BY id DESC')
    denuncias = cursor.fetchall()
    conn.close()
    return render_template('admin_ocorrencias.html', ocorrencias=denuncias)

# Aba 2: Painel de Controle e Gestão
@app.route('/admin/painel')
def admin_painel():
    if not session.get('admin_logado'):
        return redirect(url_for('login'))

    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) as total FROM denuncias')
    total_denuncias = cursor.fetchone()['total']
    cursor.execute('SELECT COUNT(*) as total FROM reparos')
    total_reparos = cursor.fetchone()['total']
    conn.close()

    return render_template('admin_painel.html', total_denuncias=total_denuncias, total_reparos=total_reparos)

# Aba 3: Relatos de Reparos
@app.route('/admin/reparos')
def admin_reparos():
    if not session.get('admin_logado'):
        return redirect(url_for('login'))

    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT id, localizacao, bairro, descricao, foto_path, status FROM reparos ORDER BY id DESC')
    reparos = cursor.fetchall()
    conn.close()
    return render_template('admin_reparos.html', reparos=reparos)

@app.route('/admin/atualizar/<int:id>', methods=['POST'])
def atualizar_status(id):
    if not session.get('admin_logado'):
        return "Acesso negado", 403
        
    novo_status = request.form.get('status')
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE denuncias SET status = ? WHERE id = ?", (novo_status, id))
    conn.commit()
    conn.close()
    
    return redirect(url_for('admin_ocorrencias'))

# ---------------------------------------------

@app.route('/api/denuncias', methods=['GET'])
def api_denuncias():
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, nome, localizacao, bairro, descricao, status, latitude, longitude FROM denuncias')
        registros = cursor.fetchall()
        conn.close()

        lista_denuncias = []
        for reg in registros:
            lista_denuncias.append({
                "id": reg[0],
                "nome": reg[1],
                "localizacao": reg[2],
                "bairro": reg[3],
                "descricao": reg[4],
                "status": reg[5],
                "latitude": reg[6],
                "longitude": reg[7]
            })

        return jsonify(lista_denuncias), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)