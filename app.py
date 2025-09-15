# from flask_sqlalchemy import SQLAlchemy
from flask import Flask, jsonify, request, Response
from models import (
    db,
    TiposContas,
    Categorias,
    Subcategorias,
    ContasBancarias,
    Operacoes,
    Cartoes,
    FaturasCartoes,
    OperacoesRecorrente,
    Recorrencias,
)
import os
from dotenv import load_dotenv
from datetime import date
from typing import Union, Tuple


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
def handle_tipos_contas() -> Union[Response, Tuple[Response, int]]:
    try:
        # LISTAR todos os tipos de conta
        if request.method == "GET":
            tipos_contas = TiposContas.query.all()
            # Converte a lista de objetos para um dicionário para a resposta JSON
            tipos_contas_list = [
                {"id": tc.idtipos_contas, "nome": tc.tipos_contas}
                for tc in tipos_contas
            ]
            return jsonify(tipos_contas_list), 200

        # CRIAR um novo tipo de conta
        elif request.method == "POST":
            try:
                data = request.get_json(silent=True) or {}
                nome_tipo = data.get("tipos_contas")
                if not nome_tipo:
                    return (
                        jsonify({"erro": "O nome do tipo de conta é obrigatório"}),
                        400,
                    )

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
            except Exception as e:
                return (
                    jsonify({"erro": "Erro ao processar JSON", "detalhes": str(e)}),
                    400,
                )
    except Exception as e:
        # Tratamento de erro para garantir que sempre retorne algo
        return jsonify({"erro": "Erro interno do servidor", "detalhes": str(e)}), 500

    # Retorno padrão caso nenhum dos métodos acima seja atendido
    # Isso evita que a função retorne None implicitamente
    return jsonify({"erro": "Método não permitido"}), 405


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


# --- NOVAS ROTAS PARA LANÇAMENTOS (OPERAÇÕES) ---
# Rota para LISTAR todos os lançamentos ou CRIAR um novo
@app.route("/lancamentos", methods=["GET", "POST"])
def handle_lancamentos():
    if request.method == "GET":
        lancamentos = Operacoes.query.all()
        lista_lancamentos = []
        for lancamento in lancamentos:
            # Acessamos os dados das tabelas relacionadas
            subcategoria = Subcategorias.query.get(lancamento.subcategorias_id)
            conta_bancaria = ContasBancarias.query.get(lancamento.contas_bancarias_id)

            lista_lancamentos.append(
                {
                    "id": lancamento.operacoes_id,
                    "tipo": lancamento.operacoes_tipo,
                    "descricao": lancamento.operacoes_descricao,
                    "data": str(lancamento.operacoes_data),
                    "valor": str(lancamento.operacoes_valor),
                    "conta": {
                        "id": conta_bancaria.idcontas_bancarias,
                        "nome": conta_bancaria.nome_conta,
                    },
                    "subcategoria": {
                        "id": subcategoria.subcategorias_id,
                        "nome": subcategoria.subcategorias_nome,
                        "categoria": subcategoria.categoria.categorias_nome,  # Acessa a categoria principal
                    },
                }
            )
        return jsonify(lista_lancamentos), 200

    elif request.method == "POST":
        data = request.json
        # A API espera o ID das chaves estrangeiras
        operacoes_tipo = data.get("operacoes_tipo")
        operacoes_descricao = data.get("operacoes_descricao")
        operacoes_data = data.get("operacoes_data")
        operacoes_valor = data.get("operacoes_valor")
        contas_bancarias_id = data.get("contas_bancarias_id")
        subcategorias_id = data.get("subcategorias_id")

        # Validação simples
        if not all(
            [
                operacoes_tipo,
                operacoes_descricao,
                operacoes_data,
                operacoes_valor,
                contas_bancarias_id,
                subcategorias_id,
            ]
        ):
            return jsonify({"erro": "Dados incompletos"}), 400

        # Converte a string de data para um objeto date
        try:
            data_lancamento = date.fromisoformat(operacoes_data)
        except ValueError:
            return jsonify({"erro": "Formato de data inválido. Use AAAA-MM-DD"}), 400

        novo_lancamento = Operacoes(
            operacoes_tipo=operacoes_tipo,
            operacoes_descricao=operacoes_descricao,
            operacoes_data=data_lancamento,
            operacoes_valor=operacoes_valor,
            contas_bancarias_id=contas_bancarias_id,
            subcategorias_id=subcategorias_id,
        )

        db.session.add(novo_lancamento)
        db.session.commit()
        return (
            jsonify(
                {
                    "mensagem": "Lançamento criado com sucesso!",
                    "id": novo_lancamento.operacoes_id,
                }
            ),
            201,
        )


# Rota para OBTER, ATUALIZAR ou DELETAR um lançamento específico
@app.route("/lancamentos/<int:lancamento_id>", methods=["GET", "PUT", "DELETE"])
def handle_lancamento(lancamento_id):
    lancamento = Operacoes.query.get(lancamento_id)
    if not lancamento:
        return jsonify({"erro": "Lançamento não encontrado"}), 404

    if request.method == "GET":
        subcategoria = Subcategorias.query.get(lancamento.subcategorias_id)
        conta_bancaria = ContasBancarias.query.get(lancamento.contas_bancarias_id)

        return (
            jsonify(
                {
                    "id": lancamento.operacoes_id,
                    "tipo": lancamento.operacoes_tipo,
                    "descricao": lancamento.operacoes_descricao,
                    "data": str(lancamento.operacoes_data),
                    "valor": str(lancamento.operacoes_valor),
                    "conta": {
                        "id": conta_bancaria.idcontas_bancarias,
                        "nome": conta_bancaria.nome_conta,
                    },
                    "subcategoria": {
                        "id": subcategoria.subcategorias_id,
                        "nome": subcategoria.subcategorias_nome,
                        "categoria": subcategoria.categoria.categorias_nome,
                    },
                }
            ),
            200,
        )

    elif request.method == "PUT":
        data = request.json
        lancamento.operacoes_tipo = data.get(
            "operacoes_tipo", lancamento.operacoes_tipo
        )
        lancamento.operacoes_descricao = data.get(
            "operacoes_descricao", lancamento.operacoes_descricao
        )
        lancamento.operacoes_data = data.get(
            "operacoes_data", str(lancamento.operacoes_data)
        )
        lancamento.operacoes_valor = data.get(
            "operacoes_valor", str(lancamento.operacoes_valor)
        )
        lancamento.contas_bancarias_id = data.get(
            "contas_bancarias_id", lancamento.contas_bancarias_id
        )
        lancamento.subcategorias_id = data.get(
            "subcategorias_id", lancamento.subcategorias_id
        )

        # Converte a string de data para um objeto date
        try:
            lancamento.operacoes_data = date.fromisoformat(lancamento.operacoes_data)
        except ValueError:
            return jsonify({"erro": "Formato de data inválido. Use AAAA-MM-DD"}), 400

        db.session.commit()
        return jsonify({"mensagem": "Lançamento atualizado com sucesso!"}), 200

    elif request.method == "DELETE":
        db.session.delete(lancamento)
        db.session.commit()
        return jsonify({"mensagem": "Lançamento deletado com sucesso!"}), 200


# --- NOVAS ROTAS PARA CONTAS BANCÁRIAS ---


# Rota para LISTAR todas as contas bancárias ou CRIAR uma nova
@app.route("/contas-bancarias", methods=["GET", "POST"])
def handle_contas_bancarias():
    if request.method == "GET":
        contas = ContasBancarias.query.all()
        lista_contas = []
        for conta in contas:
            # Acessamos o objeto de relacionamento para obter o nome do tipo de conta
            tipo_conta_obj = conta.tipo_conta_rel

            lista_contas.append(
                {
                    "id": conta.idcontas_bancarias,
                    "nome": conta.nome_conta,
                    "tipo_conta": {
                        "id": tipo_conta_obj.idtipos_contas,
                        "nome": tipo_conta_obj.tipos_contas,
                    },
                    "saldo_inicial": (
                        str(conta.conta_saldo_inicial)
                        if conta.conta_saldo_inicial is not None
                        else None
                    ),
                    "data_saldo_inicial": (
                        str(conta.data_conta_saldo_incial)
                        if conta.data_conta_saldo_incial is not None
                        else None
                    ),
                }
            )
        return jsonify(lista_contas), 200

    elif request.method == "POST":
        data = request.json
        nome_conta = data.get("nome_conta")
        tipo_conta_id = data.get("tipo_conta")
        saldo_inicial = data.get("conta_saldo_inicial")
        data_saldo_inicial_str = data.get("data_conta_saldo_incial")

        if not all([nome_conta, tipo_conta_id]):
            return (
                jsonify(
                    {"erro": "Nome da conta e o ID do tipo de conta são obrigatórios."}
                ),
                400,
            )

        # Verifica se o tipo de conta existe
        tipo_conta_relacionado = TiposContas.query.get(tipo_conta_id)
        if not tipo_conta_relacionado:
            return jsonify({"erro": "ID do tipo de conta não encontrado."}), 404

        data_saldo_inicial = None
        if data_saldo_inicial_str:
            try:
                data_saldo_inicial = date.fromisoformat(data_saldo_inicial_str)
            except ValueError:
                return (
                    jsonify({"erro": "Formato de data inválido. Use AAAA-MM-DD"}),
                    400,
                )

        nova_conta = ContasBancarias(
            nome_conta=nome_conta,
            tipo_conta=tipo_conta_id,
            conta_saldo_inicial=saldo_inicial,
            data_conta_saldo_incial=data_saldo_inicial,
        )
        db.session.add(nova_conta)
        db.session.commit()
        return (
            jsonify(
                {
                    "mensagem": "Conta criada com sucesso!",
                    "id": nova_conta.idcontas_bancarias,
                }
            ),
            201,
        )


# Rota para OBTER, ATUALIZAR ou DELETAR uma conta específica
@app.route("/contas-bancarias/<int:conta_id>", methods=["GET", "PUT", "DELETE"])
def handle_conta_bancaria(conta_id):
    conta = ContasBancarias.query.get(conta_id)
    if not conta:
        return jsonify({"erro": "Conta não encontrada"}), 404

    if request.method == "GET":
        tipo_conta_obj = conta.tipo_conta_rel
        return (
            jsonify(
                {
                    "id": conta.idcontas_bancarias,
                    "nome": conta.nome_conta,
                    "tipo_conta": {
                        "id": tipo_conta_obj.idtipos_contas,
                        "nome": tipo_conta_obj.tipos_contas,
                    },
                    "saldo_inicial": (
                        str(conta.conta_saldo_inicial)
                        if conta.conta_saldo_inicial is not None
                        else None
                    ),
                    "data_saldo_inicial": (
                        str(conta.data_conta_saldo_incial)
                        if conta.data_conta_saldo_incial is not None
                        else None
                    ),
                }
            ),
            200,
        )

    elif request.method == "PUT":
        data = request.json
        conta.nome_conta = data.get("nome_conta", conta.nome_conta)
        conta.tipo_conta = data.get("tipo_conta", conta.tipo_conta)
        conta.conta_saldo_inicial = data.get(
            "conta_saldo_inicial", conta.conta_saldo_inicial
        )
        data_str = data.get("data_conta_saldo_incial")

        if data_str:
            try:
                conta.data_conta_saldo_incial = date.fromisoformat(data_str)
            except ValueError:
                return (
                    jsonify({"erro": "Formato de data inválido. Use AAAA-MM-DD"}),
                    400,
                )

        db.session.commit()
        return jsonify({"mensagem": "Conta atualizada com sucesso!"}), 200

    elif request.method == "DELETE":
        db.session.delete(conta)
        db.session.commit()
        return jsonify({"mensagem": "Conta deletada com sucesso!"}), 200


# --- NOVAS ROTAS PARA CARTÕES E FATURAS ---


# Rota para LISTAR todos os cartões ou CRIAR um novo
@app.route("/cartoes", methods=["GET", "POST"])
def handle_cartoes():
    if request.method == "GET":
        cartoes = Cartoes.query.all()
        lista_cartoes = []
        for cartao in cartoes:
            # Inclui as faturas na resposta do cartão
            faturas = [
                {
                    "id": fat.faturasCartoesId,
                    "vencimento": str(fat.faturasCartoesDtVencimento),
                }
                for fat in cartao.faturas
            ]
            lista_cartoes.append(
                {
                    "id": cartao.cartoes_id,
                    "nome": cartao.cartoes_nome,
                    "final": cartao.cartoes_final,
                    "tipo": cartao.cartoes_tipo,
                    "faturas": faturas,
                }
            )
        return jsonify(lista_cartoes), 200

    elif request.method == "POST":
        data = request.json
        cartoes_nome = data.get("cartoes_nome")
        cartoes_final = data.get("cartoes_final")
        cartoes_tipo = data.get("cartoes_tipo")

        if not all([cartoes_nome, cartoes_final, cartoes_tipo]):
            return (
                jsonify({"erro": "O nome, final e tipo do cartão são obrigatórios"}),
                400,
            )

        novo_cartao = Cartoes(
            cartoes_nome=cartoes_nome,
            cartoes_final=cartoes_final,
            cartoes_tipo=cartoes_tipo,
        )
        db.session.add(novo_cartao)
        db.session.commit()
        return (
            jsonify(
                {"mensagem": "Cartão criado com sucesso!", "id": novo_cartao.cartoes_id}
            ),
            201,
        )


# Rota para OBTER, ATUALIZAR ou DELETAR um cartão específico
@app.route("/cartoes/<int:cartao_id>", methods=["GET", "PUT", "DELETE"])
def handle_cartao(cartao_id):
    cartao = Cartoes.query.get(cartao_id)
    if not cartao:
        return jsonify({"erro": "Cartão não encontrado"}), 404

    if request.method == "GET":
        faturas = [
            {
                "id": fat.faturasCartoesId,
                "vencimento": str(fat.faturasCartoesDtVencimento),
            }
            for fat in cartao.faturas
        ]
        return (
            jsonify(
                {
                    "id": cartao.cartoes_id,
                    "nome": cartao.cartoes_nome,
                    "final": cartao.cartoes_final,
                    "tipo": cartao.cartoes_tipo,
                    "faturas": faturas,
                }
            ),
            200,
        )

    elif request.method == "PUT":
        data = request.json
        cartao.cartoes_nome = data.get("cartoes_nome", cartao.cartoes_nome)
        cartao.cartoes_final = data.get("cartoes_final", cartao.cartoes_final)
        cartao.cartoes_tipo = data.get("cartoes_tipo", cartao.cartoes_tipo)

        db.session.commit()
        return jsonify({"mensagem": "Cartão atualizado com sucesso!"}), 200

    elif request.method == "DELETE":
        db.session.delete(cartao)
        db.session.commit()
        return jsonify({"mensagem": "Cartão deletado com sucesso!"}), 200


# Rota para LISTAR faturas de um cartão ou CRIAR uma nova fatura
@app.route("/cartoes/<int:cartao_id>/faturas", methods=["GET", "POST"])
def handle_faturas_por_cartao(cartao_id):
    cartao = Cartoes.query.get(cartao_id)
    if not cartao:
        return jsonify({"erro": "Cartão não encontrado"}), 404

    if request.method == "GET":
        faturas = [
            {
                "id": fat.faturasCartoesId,
                "vencimento": str(fat.faturasCartoesDtVencimento),
            }
            for fat in cartao.faturas
        ]
        return jsonify(faturas), 200

    elif request.method == "POST":
        data = request.json
        dt_vencimento_str = data.get("faturasCartoesDtVencimento")
        dt_fechamento_str = data.get("faturasCartoesFechamento")
        valor = data.get("faturasCartoesValor")

        if not all([dt_vencimento_str, dt_fechamento_str, valor]):
            return jsonify({"erro": "Dados de fatura incompletos"}), 400

        try:
            dt_vencimento = date.fromisoformat(dt_vencimento_str)
            dt_fechamento = date.fromisoformat(dt_fechamento_str)
        except ValueError:
            return jsonify({"erro": "Formato de data inválido. Use AAAA-MM-DD"}), 400

        nova_fatura = FaturasCartoes(
            faturasCartoesVinculado=cartao_id,
            faturasCartoesDtVencimento=dt_vencimento,
            faturasCartoesFechamento=dt_fechamento,
            faturasCartoesValor=valor,
        )

        db.session.add(nova_fatura)
        db.session.commit()
        return (
            jsonify(
                {
                    "mensagem": "Fatura criada com sucesso!",
                    "id": nova_fatura.faturasCartoesId,
                }
            ),
            201,
        )


# --- NOVAS ROTAS PARA TEMPLATES DE LANÇAMENTOS RECORRENTES ---


# Rota para LISTAR todos os templates ou CRIAR um novo
@app.route("/lancamentos-recorrentes", methods=["GET", "POST"])
def handle_templates_recorrentes():
    if request.method == "GET":
        templates = OperacoesRecorrente.query.all()
        lista_templates = []
        for template in templates:
            lista_templates.append(
                {
                    "id": template.recorrencia_id,
                    "descricao": template.recorrencia_descricao,
                    "valor": str(template.recorrencia_valor),
                    "tipo": template.recorrencia_tipo,
                    "categoria": template.recorrencia_categoria,
                    "fatura": template.recorrencia_fatura,
                }
            )
        return jsonify(lista_templates), 200

    elif request.method == "POST":
        data = request.json
        descricao = data.get("recorrencia_descricao")
        valor = data.get("recorrencia_valor")
        tipo = data.get("recorrencia_tipo")
        categoria = data.get("recorrencia_categoria")

        if not all([descricao, valor, tipo, categoria]):
            return jsonify({"erro": "Campos obrigatórios incompletos"}), 400

        novo_template = OperacoesRecorrente(
            recorrencia_descricao=descricao,
            recorrencia_valor=valor,
            recorrencia_tipo=tipo,
            recorrencia_categoria=categoria,
        )
        db.session.add(novo_template)
        db.session.commit()
        return (
            jsonify(
                {
                    "mensagem": "Template de lançamento recorrente criado com sucesso!",
                    "id": novo_template.recorrencia_id,
                }
            ),
            201,
        )


# --- NOVAS ROTAS PARA REGRAS DE RECORRÊNCIA ---


# Rota para LISTAR todas as regras ou CRIAR uma nova
@app.route("/regras-recorrencia", methods=["GET", "POST"])
def handle_regras_recorrencia():
    if request.method == "GET":
        regras = Recorrencias.query.all()
        lista_regras = []
        for regra in regras:
            lista_regras.append(
                {
                    "id": regra.recorrencia_id,
                    "operacao_id": regra.operacao_id,
                    "descricao": regra.recorrencia_descricao,
                    "frequencia": regra.frequencia,
                    "data_inicio": str(regra.data_inicio),
                    "data_fim": str(regra.data_fim) if regra.data_fim else None,
                    "status": regra.status,
                }
            )
        return jsonify(lista_regras), 200

    elif request.method == "POST":
        data = request.json
        operacao_id = data.get("operacao_id")
        frequencia = data.get("frequencia")
        data_inicio_str = data.get("data_inicio")
        status = data.get("status", "Ativo")  # Valor padrão para 'status'

        if not all([operacao_id, frequencia, data_inicio_str]):
            return jsonify({"erro": "Campos obrigatórios incompletos"}), 400

        try:
            data_inicio = date.fromisoformat(data_inicio_str)
        except ValueError:
            return jsonify({"erro": "Formato de data inválido. Use AAAA-MM-DD"}), 400

        nova_regra = Recorrencias(
            operacao_id=operacao_id,
            recorrencia_descricao=data.get("recorrencia_descricao"),
            frequencia=frequencia,
            data_inicio=data_inicio,
            data_fim=(
                date.fromisoformat(data.get("data_fim"))
                if data.get("data_fim")
                else None
            ),
            status=status,
        )

        db.session.add(nova_regra)
        db.session.commit()
        return (
            jsonify(
                {
                    "mensagem": "Regra de recorrência criada com sucesso!",
                    "id": nova_regra.recorrencia_id,
                }
            ),
            201,
        )


# Bloco para executar a aplicação
if __name__ == "__main__":
    with app.app_context():
        # Cria as tabelas no banco de dados, se elas não existirem
        db.create_all()
    app.run(debug=True)
