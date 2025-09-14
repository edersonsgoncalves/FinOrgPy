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
