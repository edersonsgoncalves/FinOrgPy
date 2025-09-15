from flask_sqlalchemy import SQLAlchemy

# from sqlalchemy import Numeric, Date, ForeignKey
# from sqlalchemy.orm import relationship

# Cria uma instância do SQLAlchemy
db = SQLAlchemy()


# 1. Tabela tipos_contas
class TiposContas(db.Model):
    __tablename__ = "tipos_contas"
    idtipos_contas = db.Column(db.Integer, primary_key=True)
    tipos_contas = db.Column(db.String(45))
    contas_bancarias_rel = db.relationship(
        "ContasBancarias", backref="tipo_conta_rel", lazy=True
    )

    def __init__(self, tipos_contas: str):  # Pode ser 'nome' em vez de 'tipos_contas'
        self.tipos_contas = tipos_contas


# 2. Tabela categorias
class Categorias(db.Model):
    __tablename__ = "categorias"
    categorias_id = db.Column(db.Integer, primary_key=True)
    categorias_nome = db.Column(db.String(255), nullable=False)
    categorias_classe = db.Column(db.Integer, nullable=False)
    subcategorias = db.relationship(
        "Subcategorias", backref="categorias_id", lazy=True
    )  # Nome alterado para refletir 'categorias_pai'


# 3. Tabela subcategorias
class Subcategorias(db.Model):
    __tablename__ = "subcategorias"
    subcategorias_id = db.Column(db.Integer, primary_key=True)
    subcategorias_nome = db.Column(db.String(255), nullable=False)
    # Coluna 'subcategorias_classe' no seu DB
    subcategorias_classe = db.Column(db.Integer, nullable=False)
    # Nova chave estrangeira para o pai
    categorias_id = db.Column(db.Integer, db.ForeignKey("categorias.categorias_id"))

    operacoes = db.relationship("Operacoes", backref="subcategoria", lazy=True)


# 4. Tabela contas_moedas
class ContasMoedas(db.Model):
    __tablename__ = "contas_moedas"
    idcontas_moedas = db.Column(db.Integer, primary_key=True)
    contas_moedas_nome = db.Column(db.String(45))
    contas_moedas_simbolo = db.Column(db.String(4))
    contas_moedas_cotacao = db.Column(db.Numeric(10, 2))


# 5. Tabela contas_bancarias (atualizada)
class ContasBancarias(db.Model):
    __tablename__ = "contas_bancarias"
    idcontas_bancarias = db.Column(db.Integer, primary_key=True)
    nome_conta = db.Column(db.String(100), nullable=False)
    tipo_conta = db.Column(db.Integer, db.ForeignKey("tipos_contas.idtipos_contas"))
    conta_saldo_inicial = db.Column(db.Numeric(10, 0))  # decimal(10,0) [cite: 1]
    data_conta_saldo_incial = db.Column(db.Date)

    # NOVOS CAMPOS DO SEU ESQUEMA
    conta_moeda = db.Column(db.Integer, db.ForeignKey("contas_moedas.idcontas_moedas"))
    contas_limite = db.Column(db.Numeric(10, 0))  # decimal(10,0)
    contas_liquidez = db.Column(db.Integer)
    contas_cartao_fechamento = db.Column(db.Integer)
    contas_prev_debito = db.Column(db.Integer)
    contas_desconsiderar_saldo = db.Column(db.Integer)  # int

    operacoes = db.relationship("Operacoes", backref="conta_bancaria", lazy=True)


# 6. Tabela cartoes
class Cartoes(db.Model):
    __tablename__ = "cartoes"
    cartoes_id = db.Column(db.Integer, primary_key=True)
    cartoes_nome = db.Column(db.String(45))
    cartoes_final = db.Column(db.Integer)
    cartoes_atrelado = db.Column(db.Integer)
    cartoes_tipo = db.Column(db.Integer)
    faturas = db.relationship(
        "FaturasCartoes", backref="cartao_credito", lazy=True
    )  # Nome do modelo e backref ajustados


# 7. Tabela faturasCartoes (atualizada)
class FaturasCartoes(db.Model):
    __tablename__ = "faturasCartoes"
    faturasCartoesId = db.Column(db.Integer, primary_key=True)
    faturasCartoesVinculado = db.Column(db.Integer, db.ForeignKey("cartoes.cartoes_id"))
    faturasCartoesDtVencimento = db.Column(db.Date)
    faturasCartoesFechamento = db.Column(db.Date)
    faturasCartoesFechado = db.Column(db.Boolean)
    faturasCartoesValor = db.Column(db.Numeric(10, 2))
    faturasCartoesMesAno = db.Column(db.Date)


# 8. Tabela tipos_operacoes (anteriormente TiposLancamentos)
class TiposOperacoes(db.Model):
    __tablename__ = "tipos_operacoes"
    tipo_operacao_id = db.Column(db.Integer, primary_key=True)
    tipo_operacao_nome = db.Column(db.String(50))
    operacoes = db.relationship("Operacoes", backref="tipo_operacao", lazy=True)


# 9. Tabela operacoes (atualizada)
class Operacoes(db.Model):
    __tablename__ = "operacoes"
    operacoes_id = db.Column(db.Integer, primary_key=True)
    operacoes_data_lancamento = db.Column(db.Date)  # campo `operacoes_data_lancamento`
    operacoes_descricao = db.Column(db.String(255))
    operacoes_conta = db.Column(
        db.Integer, db.ForeignKey("contas_bancarias.idcontas_bancarias")
    )  # FK para `contas_bancarias`
    operacoes_valor = db.Column(db.Numeric(10, 2))
    operacoes_tipo = db.Column(
        db.Integer, db.ForeignKey("tipos_operacoes.tipo_operacao_id")
    )  # FK para `tipos_operacoes`

    # NOVOS CAMPOS DO SEU ESQUEMA
    operacoes_transf_rel = db.Column(db.Integer)
    operacoes_categoria = db.Column(
        db.Integer, db.ForeignKey("subcategorias.subcategorias_id")
    )  # FK para `subcategorias`
    operacoes_parcela = db.Column(db.Numeric(6, 3))
    operacoes_fatura = db.Column(
        db.Integer, db.ForeignKey("faturasCartoes.faturasCartoesId")
    )  # FK para `faturasCartoes`
    operacoes_cartao_atrelado = db.Column(
        db.Integer, db.ForeignKey("cartoes.cartoes_id")
    )  # FK para `cartoes`
    operacoes_recorrencia = db.Column(db.Integer)
    operacoes_projeto = db.Column(db.Integer)
    operacoes_data_efetivado = db.Column(db.Date)
    operacoes_efetivado = db.Column(db.Boolean)
    operacoes_validacao = db.Column(db.Boolean)


# 10. Tabela recorrencias
class Recorrencias(db.Model):
    __tablename__ = "recorrencias"
    recorrencia_id = db.Column(db.Integer, primary_key=True)
    operacao_id = db.Column(db.Integer, db.ForeignKey("operacoes.operacoes_id"))
    recorrencia_descricao = db.Column(db.String(100))
    frequencia = db.Column(db.String(50))
    data_inicio = db.Column(db.Date)
    data_fim = db.Column(db.Date)
    status = db.Column(db.String(50))
    ultimo_lancamento = db.Column(db.Date)
    dias_uteis = db.Column(db.Integer)


# 11. Tabela operacoes_recorrente
class OperacoesRecorrente(db.Model):
    __tablename__ = "operacoes_recorrente"
    recorrencia_id = db.Column(db.Integer, primary_key=True)
    recorrencia_data_lancamento = db.Column(db.Date)
    recorrencia_descricao = db.Column(db.String(255))
    recorrencia_conta = db.Column(db.Integer)
    recorrencia_valor = db.Column(db.Numeric(10, 2))
    recorrencia_tipo = db.Column(db.Integer)
    recorrencia_categoria = db.Column(db.Integer)
    recorrencia_fatura = db.Column(db.Integer)
    recorrencia_prazo = db.Column(db.Integer)
    recorrencia_validacao = db.Column(db.Boolean)


# 12. Tabela projetos
class Projetos(db.Model):
    __tablename__ = "projetos"
    projetos_id = db.Column(db.Integer, primary_key=True)
    projetos_nome = db.Column(db.String(45))
    projetos_inicio = db.Column(db.Date)
    projetos_fim = db.Column(db.Date)
    projetos_cor = db.Column(db.String(6))


# 13. Tabela login
class Login(db.Model):
    __tablename__ = "login"
    UsuarioID = db.Column(db.Integer, primary_key=True)
    UsuarioNome = db.Column(db.String(255), nullable=False)
    UsuarioEmail = db.Column(db.String(255), nullable=False)
    UsuarioNivel = db.Column(db.Integer, nullable=False)
    UsuarioAcesso = db.Column(db.String(255), nullable=False)
    UsuarioSenha = db.Column(db.String(255), nullable=False)
