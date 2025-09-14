from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from models import db, TiposContas, Categorias, Subcategorias
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


# --- NOVAS ROTAS PARA CATEGORIAS ---


# Rota para LISTAR todas as categorias ou CRIAR uma nova categoria
@app.route("/categorias", methods=["GET", "POST"])
def handle_categorias():
    if request.method == "GET":
        categorias = Categorias.query.all()
        lista_categorias = []
        for cat in categorias:
            # Inclui as subcategorias na resposta da categoria
            subcategorias = [
                {"id": sub.subcategorias_id, "nome": sub.subcategorias_nome}
                for sub in cat.subcategorias
            ]
            lista_categorias.append(
                {
                    "id": cat.categorias_id,
                    "nome": cat.categorias_nome,
                    "classe": cat.categorias_classe,
                    "subcategorias": subcategorias,
                }
            )
        return jsonify(lista_categorias), 200

    elif request.method == "POST":
        data = request.json
        nome = data.get("categorias_nome")
        classe = data.get("categorias_classe")
        if not nome or classe is None:
            return (
                jsonify({"erro": "O nome e a classe da categoria são obrigatórios"}),
                400,
            )

        nova_categoria = Categorias(categorias_nome=nome, categorias_classe=classe)
        db.session.add(nova_categoria)
        db.session.commit()
        return (
            jsonify(
                {
                    "mensagem": "Categoria criada com sucesso!",
                    "id": nova_categoria.categorias_id,
                }
            ),
            201,
        )


# Rota para OBTER, ATUALIZAR ou DELETAR uma categoria específica
@app.route("/categorias/<int:categoria_id>", methods=["GET", "PUT", "DELETE"])
def handle_categoria(categoria_id):
    categoria = Categorias.query.get(categoria_id)
    if not categoria:
        return jsonify({"erro": "Categoria não encontrada"}), 404

    if request.method == "GET":
        subcategorias = [
            {"id": sub.subcategorias_id, "nome": sub.subcategorias_nome}
            for sub in categoria.subcategorias
        ]
        return (
            jsonify(
                {
                    "id": categoria.categorias_id,
                    "nome": categoria.categorias_nome,
                    "classe": categoria.categorias_classe,
                    "subcategorias": subcategorias,
                }
            ),
            200,
        )

    elif request.method == "PUT":
        data = request.json
        nome = data.get("categorias_nome", categoria.categorias_nome)
        classe = data.get("categorias_classe", categoria.categorias_classe)

        categoria.categorias_nome = nome
        categoria.categorias_classe = classe
        db.session.commit()
        return jsonify({"mensagem": "Categoria atualizada com sucesso!"}), 200

    elif request.method == "DELETE":
        # Se tentar deletar uma categoria com subcategorias, o banco de dados pode dar erro de chave estrangeira.
        # Por enquanto, deixamos assim. Poderíamos adicionar a lógica de deleção em cascata no modelo.
        db.session.delete(categoria)
        db.session.commit()
        return jsonify({"mensagem": "Categoria deletada com sucesso!"}), 200


# --- NOVAS ROTAS PARA SUBCATEGORIAS ---


# Rota para LISTAR subcategorias de uma categoria específica ou CRIAR uma nova
@app.route("/categorias/<int:categoria_id>/subcategorias", methods=["GET", "POST"])
def handle_subcategorias_por_categoria(categoria_id):
    categoria = Categorias.query.get(categoria_id)
    if not categoria:
        return jsonify({"erro": "Categoria não encontrada"}), 404

    if request.method == "GET":
        subcategorias = [
            {"id": sub.subcategorias_id, "nome": sub.subcategorias_nome}
            for sub in categoria.subcategorias
        ]
        return jsonify(subcategorias), 200

    elif request.method == "POST":
        data = request.json
        nome = data.get("subcategorias_nome")
        if not nome:
            return jsonify({"erro": "O nome da subcategoria é obrigatório"}), 400

        nova_subcategoria = Subcategorias(
            subcategorias_nome=nome, categorias_id=categoria_id
        )
        db.session.add(nova_subcategoria)
        db.session.commit()
        return (
            jsonify(
                {
                    "mensagem": "Subcategoria criada com sucesso!",
                    "id": nova_subcategoria.subcategorias_id,
                }
            ),
            201,
        )


# Rota para OBTER, ATUALIZAR ou DELETAR uma subcategoria específica
@app.route("/subcategorias/<int:subcategoria_id>", methods=["GET", "PUT", "DELETE"])
def handle_subcategoria(subcategoria_id):
    subcategoria = Subcategorias.query.get(subcategoria_id)
    if not subcategoria:
        return jsonify({"erro": "Subcategoria não encontrada"}), 404

    if request.method == "GET":
        return (
            jsonify(
                {
                    "id": subcategoria.subcategorias_id,
                    "nome": subcategoria.subcategorias_nome,
                    "categoria_id": subcategoria.categorias_id,
                }
            ),
            200,
        )

    elif request.method == "PUT":
        data = request.json
        nome = data.get("subcategorias_nome", subcategoria.subcategorias_nome)
        subcategoria.subcategorias_nome = nome
        db.session.commit()
        return jsonify({"mensagem": "Subcategoria atualizada com sucesso!"}), 200

    elif request.method == "DELETE":
        db.session.delete(subcategoria)
        db.session.commit()
        return jsonify({"mensagem": "Subcategoria deletada com sucesso!"}), 200


# Bloco para executar a aplicação
if __name__ == "__main__":
    with app.app_context():
        # Cria as tabelas no banco de dados, se elas não existirem
        db.create_all()
    app.run(debug=True)
