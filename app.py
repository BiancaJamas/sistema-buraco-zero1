from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
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

@app.route('/admin')
def admin():
    senha = request.args.get('senha')
    if senha != 'admin123':
        return "Acesso negado. Senha incorreta ou ausente.", 403

    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT id, nome, cpf, localizacao, bairro, descricao, foto_path, status, latitude, longitude FROM denuncias ORDER BY id DESC')
    denuncias = cursor.fetchall()
    conn.close()
    return render_template('admin.html', denuncias=denuncias)

@app.route('/admin/atualizar/<int:id>', methods=['POST'])
def atualizar_status(id):
    senha = request.args.get('senha')
    if senha != 'admin123':
        return "Acesso negado", 403
        
    novo_status = request.form.get('status')
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE denuncias SET status = ? WHERE id = ?", (novo_status, id))
    conn.commit()
    conn.close()
    
    return redirect(url_for('admin', senha=senha))

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