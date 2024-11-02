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
    if not session.get('nome'):
       return redirect(url_for('cadastro_usuario')) 
    return render_template("cadastro_nota.html") 

@app.route("/consulta_balanco")
def consulta_balanco():
    if not session.get('nome'):
        return redirect(url_for('cadastro_usuarios'))
    return render_template("consulta_balanco.html")

@app.route("/executa_consulta_balanco", methods=["POST"])
def executa_consulta_balanco():
    json_request = request.json
    print(json_request)
    ativo = json_request["ativo"] # Se for TRUE, queremos notas com valor_entrada > 0
    passivo = json_request["passivo"]  # Se for TRUE, queremos notas com valor_saida > 0

    notas_ativo = []
    notas_passivo = []

    with psycopg.connect(URL_CONNEXAO) as conn:
        with conn.cursor() as cur:
            if ativo:
                cur.execute("SELECT nome_cliente, valor_entrada, valor_saida, data_emissao FROM nota_fiscal where valor_entrada > 0")
                notas_ativo = cur.fetchall()

            if passivo:
                cur.execute("SELECT nome_cliente, valor_entrada, valor_saida, data_emissao FROM nota_fiscal where valor_saida > 0")
                notas_passivo = cur.fetchall()

    dados = notas_ativo + notas_passivo

    dados_formatados = []
    for nota_fiscal in dados:
        dados_formatados.append(
            [
                nota_fiscal[0],
                nota_fiscal[1],
                nota_fiscal[2],
                nota_fiscal[3].strftime("%d-%m-%Y"),
            ]
        )

    print("@@@@@")
    print(dados_formatados)

    return jsonify(dados_formatados)

@app.route("/sobre")
def sobre():
    return render_template("sobre.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/criar_nota", methods=["POST"])
def criar_nota():
    nome_cliente = request.form["nome_tomador_de_servicos"]
    cpf_cnpj = request.form["numero_tomador_cpf_cnpj"]
    valor_entrada = request.form["valor_entrada"]
    valor_saida = request.form["valor_saida"]
    data_emissao = request.form["data_emissao"]
    with psycopg.connect(URL_CONNEXAO) as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO nota_fiscal (nome_cliente, cpf_cnpj, data_emissao, valor_entrada, valor_saida) VALUES (%s, %s, %s, %s, %s)", 
                        (nome_cliente, cpf_cnpj, data_emissao, valor_entrada, valor_saida))
            conn.commit()
    return render_template("nota_cadastrada.html")

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

@app.route('/submit_usuario', methods=['POST'])
def submit_usuario():
    nome = request.form['nome']
    email = request.form['email']
    senha = request.form['senha']
    with psycopg.connect(URL_CONNEXAO) as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO usuarios (nome, email, senha) VALUES (%s, %s, %s)", 
                        (nome, email, senha))
            conn.commit()
    return redirect(url_for('login'))

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

    with psycopg.connect(URL_CONNEXAO) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM usuarios where email = %s and senha = %s", (email, senha))
            usuario = cur.fetchone()

    if len(usuario) > 0:
        session['nome'] = usuario[1]
        session['email'] = email
        session['id_usuario'] = usuario[0]
        session['secret_key'] = 'chave_acesso'
        return redirect(url_for('cadastrar_nota'))
    else:
        return redirect(url_for('cadastro_usuario'))
        
if __name__=="__main__":
    app.secret_key = 'chave_acesso'
    app.run(host="0.0.0.0",port=9000, debug=True)
