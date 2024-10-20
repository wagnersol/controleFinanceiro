from flask import Flask
from flask import render_template, send_from_directory, request, redirect, url_for, jsonify, session
from flask_cors import CORS
import sqlite3
import json
import psycopg

URL_CONNEXAO = "postgres://neondb_owner:3Vzlg8qIRBoa@ep-green-bonus-a58b1qy5.us-east-2.aws.neon.tech/neondb"

app = Flask(__name__)
CORS(app)

# Adiciona o icone nas páginas
@app.route('/favicon.ico')
def favicon():
    return send_from_directory('./static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route("/")
def hello_world():
    return render_template("home.html")

@app.route("/cadastro_usuario")
def cadastro_usuario():
    return render_template("cadastro_usuario.html")


@app.route("/cadastro_nota")
def cadastrar_nota():
    # if not session.get('nome'):
    #    return redirect(url_for('cadastro_usuario')) 
    return render_template("cadastro_nota.html") 

@app.route("/consulta")
def consulta_de_medicamentos():
    if not session.get('nome'):
        return redirect(url_for('cadastro_usuarios'))
    return render_template("consulta_medicamento.html")

@app.route("/sobre")
def sobre():
    return render_template("sobre.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/criar_nota", methods=["POST"])
def criar_nota():
    json_request = request.form
    print( json_request)
    nome_cliente = json_request["nome_cliente"]
    valor_entrada = json_request["valor_entrada"]
    valor_saida = json_request["valor_saida"]
    with psycopg.connect(URL_CONNEXAO) as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO nota_fiscal (nome_cliente, valor_entrada, valor_saida) VALUES (%s, %s, %s)", 
                        (nome_cliente, valor_entrada, valor_saida))
            conn.commit()

@app.route("/busca_notas_ficais", methods=["POST"])
def busca_notas_ficais():
    json_request = request.json
    print(json_request, json_request["nome_remedio"])
    nome_remedio = json_request["nome_remedio"]
    conn = sqlite3.connect('banco_de_dados.db')
    cursor = conn.cursor()    
    # Consultar os dados
    cursor.execute(f"""
        SELECT remedio.*, usuario.nome as nome_usuario, usuario.telefone, usuario.email 
        FROM remedio 
        JOIN usuario ON remedio.id_usuario = usuario.id
        WHERE upper(remedio.nome) like '%{nome_remedio}%'
    """)
    dados = cursor.fetchall()
    return jsonify(dados)

@app.route('/submit', methods=['POST'])
def submit():
    nome = request.form['nome']
    email = request.form['email']
    senha = request.form['senha']

    # conecta com SQLite.
    conn = sqlite3.connect('banco_de_dados.db')
    cursor = conn.cursor()

    # Inserir dados na tabela SQLite.
    cursor.execute('''INSERT INTO usuario (nome, email, telefone, senha)
                      VALUES (?, ?, ?, ?)''', (nome, email, senha))

# Commit e fechar conexão
    conn.commit()
    conn.close()

   # redireciona para página sucesso.html
    return redirect(url_for('login'))

 # submit dos remedios

@app.route('/submit_remedio', methods=['POST'])
def submit_remedio():
    nome = request.form['nome'].upper()
    quantidade = request.form['quantidade']
    dosagem = request.form['Dosagem do remédio']
    validade = request.form['Validade']
    id_usuario = session['id_usuario']

    # conecta com SQLite.
    conn = sqlite3.connect('banco_de_dados.db')
    cursor = conn.cursor()
  
    # Inserir dados na tabela SQLite.
    cursor.execute('''INSERT INTO remedio (nome, quantidade, dosagem, validade, id_usuario)
                      VALUES (?, ?, ?, ?, ?)''', (nome, quantidade, dosagem, validade, id_usuario))

    # Commit e fechar conexão
    conn.commit()
    conn.close()

   # redireciona para página sucesso.html
    return redirect(url_for('consulta_de_medicamentos'))

@app.route("/submit_login", methods=['POST'])
def submit_login():
    email = request.form['email']
    senha = request.form['senha']

    # Conecta com SQLite
    conn = sqlite3.connect('banco_de_dados.db')
    cursor = conn.cursor()

    # Consulta os dados
    cursor.execute("SELECT * FROM usuario WHERE email = ? AND senha = ?", (email, senha))
    dados = cursor.fetchall()

    # Fecha conexão com o banco de dados
    conn.close()

    if len(dados) > 0:
        session['nome'] = dados[0][1]
        session['email'] = email
        session['id_usuario'] = dados[0][0]
        session['secret_key'] = 'chave_acesso'
        return redirect(url_for('consulta_de_medicamentos'))
    else:
        return redirect(url_for('cadastro_usuario'))
        
if __name__=="__main__":
    app.secret_key = 'chave_acesso'
    app.run(host="0.0.0.0",port=9000, debug=True)
