"""
CryptoNinja 🥷 - Sistema de Autenticação
Configuração do banco de dados PostgreSQL e modelos de usuário
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_bcrypt import Bcrypt
from datetime import datetime
import os

# Inicializar extensões
db = SQLAlchemy()
bcrypt = Bcrypt()

class User(UserMixin, db.Model):
    """Modelo de usuário para autenticação"""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Campos adicionais para trading
    balance = db.Column(db.Float, default=10000.0)  # Saldo inicial paper trading
    total_trades = db.Column(db.Integer, default=0)
    total_pnl = db.Column(db.Float, default=0.0)
    
    def __init__(self, username, email, password, is_admin=False):
        self.username = username
        self.email = email
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        self.is_admin = is_admin
    
    def check_password(self, password):
        """Verificar senha"""
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """Atualizar último login"""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def update_trading_stats(self, pnl_change, trade_count_change=1):
        """Atualizar estatísticas de trading"""
        self.total_pnl += pnl_change
        self.total_trades += trade_count_change
        db.session.commit()
    
    def to_dict(self):
        """Converter para dicionário"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_admin': self.is_admin,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'balance': self.balance,
            'total_trades': self.total_trades,
            'total_pnl': self.total_pnl
        }
    
    def __repr__(self):
        return f'<User {self.username}>'

class UserSession(db.Model):
    """Modelo para rastrear sessões de usuário"""
    
    __tablename__ = 'user_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_token = db.Column(db.String(255), unique=True, nullable=False)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relacionamento
    user = db.relationship('User', backref=db.backref('sessions', lazy=True))
    
    def is_expired(self):
        """Verificar se a sessão expirou"""
        return datetime.utcnow() > self.expires_at
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat(),
            'is_active': self.is_active
        }

def get_database_config():
    """Obter configuração do banco de dados"""
    
    # Configuração padrão PostgreSQL
    config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'cryptoninja'),
        'username': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'postgres')
    }
    
    # URL de conexão PostgreSQL
    db_url = f"postgresql://{config['username']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
    
    return db_url

def init_database(app):
    """Inicializar banco de dados"""
    
    # Configurar SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = get_database_config()
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True
    }
    
    # Inicializar extensões
    db.init_app(app)
    bcrypt.init_app(app)
    
    print("🥷 CryptoNinja: Banco de dados PostgreSQL configurado")
    
    return db

def create_tables(app):
    """Criar tabelas no banco de dados"""
    with app.app_context():
        try:
            db.create_all()
            print("✅ Tabelas criadas com sucesso")
            return True
        except Exception as e:
            print(f"❌ Erro ao criar tabelas: {e}")
            return False

def create_admin_user(app, username="admin", email="admin@cryptoninja.com", password="ninja123"):
    """Criar usuário administrador inicial"""
    with app.app_context():
        try:
            # Verificar se admin já existe
            admin = User.query.filter_by(username=username).first()
            if admin:
                print(f"⚠️ Usuário admin '{username}' já existe")
                return admin
            
            # Criar usuário admin
            admin = User(
                username=username,
                email=email,
                password=password,
                is_admin=True
            )
            
            db.session.add(admin)
            db.session.commit()
            
            print(f"✅ Usuário admin criado: {username}")
            print(f"📧 Email: {email}")
            print(f"🔑 Senha: {password}")
            print("⚠️ IMPORTANTE: Altere a senha padrão após o primeiro login!")
            
            return admin
            
        except Exception as e:
            print(f"❌ Erro ao criar usuário admin: {e}")
            db.session.rollback()
            return None

def test_database_connection():
    """Testar conexão com o banco de dados"""
    try:
        from sqlalchemy import create_engine, text
        
        engine = create_engine(get_database_config())
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            result.fetchone()
        
        print("✅ Conexão com PostgreSQL bem-sucedida")
        return True
        
    except Exception as e:
        print(f"❌ Erro de conexão PostgreSQL: {e}")
        print("💡 Dicas:")
        print("   • Verifique se o PostgreSQL está rodando")
        print("   • Confirme as credenciais no arquivo .env")
        print("   • Certifique-se de que o banco 'cryptoninja' existe")
        return False
