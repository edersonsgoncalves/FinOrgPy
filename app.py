from flask import Flask, jsonify, request

# from flask_sqlalchemy import SQLAlchemy
from models import db  # , TiposContas
import os  # Importa a biblioteca para interagir com o sistema operacional

# Importa e carrega as variáveis do arquivo .env
from dotenv import load_dotenv

load_dotenv()

# Cria a instância da aplicação Flask
app = Flask(__name__)

# Configurações do Banco de Dados
# A string de conexão é lida da variável de ambiente
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Inicializa o SQLAlchemy com a aplicação Flask
db.init_app(app)


# --- Exemplo de uma rota de teste para garantir que tudo está funcionando ---
@app.route("/")
def home():
    return "Bem-vindo ao FinOrg - Administrador Financeiro"


# Rota para LISTAR todos os tipos de conta e para CRIAR um novo tipo
@app.route("/tipos-contas", methods=["GET", "POST"])
def handle_tipos_contas():
    # LISTAR todos os tipos de conta
    if request.method == "GET":
        tipos_contas = TiposContas.query.all()
        # Converte a lista de objetos para um dicionário para a resposta JSON
        tipos_contas_list = [
            {"id": tc.idtipos_contas, "nome": tc.tipos_contas} for tc in tipos_contas
        ]
        return jsonify(tipos_contas_list), 200

    # CRIAR um novo tipo de conta
    elif request.method == "POST":
        data = request.json
        nome_tipo = data.get("tipos_contas")
        if not nome_tipo:
            return jsonify({"erro": "O nome do tipo de conta é obrigatório"}), 400

        novo_tipo = TiposContas(tipos_contas=nome_tipo)
        db.session.add(novo_tipo)
        db.session.commit()
        return (
            jsonify(
                {
                    "mensagem": "Tipo de conta criado com sucesso!",
                    "id": novo_tipo.idtipos_contas,
                }
            ),
            201,
        )


# Rota para OBTER, ATUALIZAR ou DELETAR um tipo de conta específico
@app.route("/tipos-contas/<int:tipo_id>", methods=["GET", "PUT", "DELETE"])
def handle_tipo_conta(tipo_id):
    tipo_conta = TiposContas.query.get(tipo_id)
    if not tipo_conta:
        return jsonify({"erro": "Tipo de conta não encontrado"}), 404

    # OBTER detalhes de um tipo de conta específico
    if request.method == "GET":
        return (
            jsonify({"id": tipo_conta.idtipos_contas, "nome": tipo_conta.tipos_contas}),
            200,
        )

    # ATUALIZAR um tipo de conta existente
    elif request.method == "PUT":
        data = request.json
        nome_atualizado = data.get("tipos_contas")
        if not nome_atualizado:
            return jsonify({"erro": "O nome do tipo de conta é obrigatório"}), 400

        tipo_conta.tipos_contas = nome_atualizado
        db.session.commit()
        return jsonify({"mensagem": "Tipo de conta atualizado com sucesso!"}), 200

    # DELETAR um tipo de conta
    elif request.method == "DELETE":
        # Aqui você pode adicionar a lógica para checar se há registros associados, como mencionaste.
        # Por agora, vamos permitir a exclusão direta.
        db.session.delete(tipo_conta)
        db.session.commit()
        return jsonify({"mensagem": "Tipo de conta deletado com sucesso!"}), 200


# Bloco para executar a aplicação
if __name__ == "__main__":
    with app.app_context():
        # Cria as tabelas no banco de dados, se elas não existirem
        db.create_all()
    app.run(debug=True)
