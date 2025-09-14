from flask import Flask

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


# Bloco para executar a aplicação
if __name__ == "__main__":
    with app.app_context():
        # Cria as tabelas no banco de dados, se elas não existirem
        db.create_all()
    app.run(debug=True)
