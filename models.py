from flask_sqlalchemy import SQLAlchemy

# Cria uma instância do SQLAlchemy
db = SQLAlchemy()


# Define a classe para o modelo 'TiposContas'
class TiposContas(db.Model):
    __tablename__ = "tipos_contas"  # Nome da tabela no banco de dados

    idtipos_contas = db.Column(db.Integer, primary_key=True)
    tipos_contas = db.Column(db.String(45))

    def __repr__(self):
        # Esta função é útil para representação de objetos em logs ou no console
        return f"<TiposContas {self.tipos_contas}>"
