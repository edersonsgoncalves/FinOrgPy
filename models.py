from flask_sqlalchemy import SQLAlchemy

# Cria uma instância do SQLAlchemy
db = SQLAlchemy()


# Define a classe para o modelo 'TiposContas'
class TiposContas(db.Model):
    __tablename__ = "tipos_contas"
    idtipos_contas = db.Column(db.Integer, primary_key=True)
    tipos_contas = db.Column(db.String(45))

    def __repr__(self):
        return f"<TiposContas {self.tipos_contas}>"


# --- MODELO ATUALIZADO: CATEGORIAS E SUBCATEGORIAS ---


class Categorias(db.Model):
    __tablename__ = "categorias"
    categorias_id = db.Column(db.Integer, primary_key=True)
    categorias_nome = db.Column(db.String(255), nullable=False)
    categorias_classe = db.Column(db.Integer, nullable=False)

    # Define o relacionamento com o modelo Subcategorias
    subcategorias = db.relationship("Subcategorias", backref="categoria", lazy=True)

    def __repr__(self):
        return f"<Categorias {self.categorias_nome}>"


class Subcategorias(db.Model):
    __tablename__ = "subcategorias"
    subcategorias_id = db.Column(db.Integer, primary_key=True)
    subcategorias_nome = db.Column(db.String(255), nullable=False)

    # Define a chave estrangeira que liga a subcategoria à categoria principal
    categorias_id = db.Column(
        db.Integer, db.ForeignKey("categorias.categorias_id"), nullable=False
    )

    def __repr__(self):
        return f"<Subcategorias {self.subcategorias_nome}>"


# --- NOVOS MODELOS: Contas Bancarias e Operações ---


class ContasBancarias(db.Model):
    __tablename__ = "contas_bancarias"
    idcontas_bancarias = db.Column(db.Integer, primary_key=True)
    nome_conta = db.Column(db.String(100), nullable=False)
    tipo_conta = db.Column(db.Integer, db.ForeignKey("tipos_contas.idtipos_contas"))
    conta_saldo_inicial = db.Column(db.Numeric(10, 2))  # Ajustado para 2 casas decimais
    data_conta_saldo_incial = db.Column(db.Date)

    # NOVOS CAMPOS ADICIONADOS
    conta_moeda = db.Column(db.Integer)
    contas_limite = db.Column(db.Numeric(10, 2))  # Ajustado para 2 casas decimais
    contas_liquidez = db.Column(db.Integer)
    contas_cartao_fechamento = db.Column(db.Integer)
    contas_prev_debito = db.Column(db.Integer)
    contas_desconsiderar_saldo = db.Column(db.Boolean)

    operacoes = db.relationship("Operacoes", backref="conta_bancaria", lazy=True)

    def __repr__(self):
        return f"<ContasBancarias {self.nome_conta}>"


class Operacoes(db.Model):
    __tablename__ = "operacoes"
    operacoes_id = db.Column(db.Integer, primary_key=True)
    operacoes_tipo = db.Column(
        db.Integer
    )  # Por enquanto, tipo de lançamento como um inteiro
    operacoes_descricao = db.Column(db.String(255))
    operacoes_data = db.Column(db.Date)
    operacoes_valor = db.Column(db.Numeric(10, 2))

    # Chaves Estrangeiras para relacionamentos
    contas_bancarias_id = db.Column(
        db.Integer, db.ForeignKey("contas_bancarias.idcontas_bancarias")
    )
    subcategorias_id = db.Column(
        db.Integer, db.ForeignKey("subcategorias.subcategorias_id")
    )

    def __repr__(self):
        return f"<Operacoes {self.operacoes_descricao}>"
