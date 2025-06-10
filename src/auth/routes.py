"""
CryptoNinja 🥷 - Sistema de Autenticação
Rotas e lógica de login/logout
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
import uuid
import os

from .models import db, User, UserSession

# Blueprint para autenticação
auth_bp = Blueprint('auth', __name__, template_folder='templates')

# Configurar Flask-Login
login_manager = LoginManager()

def init_auth(app):
    """Inicializar sistema de autenticação"""
    
    # Configurar Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    login_manager.login_message_category = 'info'
    
    # Configurações de sessão
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'cryptoninja-secret-key-2025')
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
    
    # Registrar blueprint
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    print("🥷 CryptoNinja: Sistema de autenticação inicializado")

@login_manager.user_loader
def load_user(user_id):
    """Carregar usuário para Flask-Login"""
    return User.query.get(int(user_id))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    
    # Se já estiver logado, redirecionar
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        remember = data.get('remember', False)
        
        # Validações básicas
        if not username or not password:
            error = "Username e senha são obrigatórios"
            if request.is_json:
                return jsonify({'success': False, 'error': error}), 400
            flash(error, 'danger')
            return render_template('auth/login.html')
        
        # Buscar usuário
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password) and user.is_active:
            # Login bem-sucedido
            login_user(user, remember=remember)
            user.update_last_login()
            
            # Criar sessão personalizada
            create_user_session(user, request)
            
            success_msg = f"🥷 Bem-vindo ao CryptoNinja, {user.username}!"
            
            if request.is_json:
                return jsonify({
                    'success': True, 
                    'message': success_msg,
                    'redirect': url_for('index'),
                    'user': {
                        'username': user.username,
                        'is_admin': user.is_admin
                    }
                })
            
            flash(success_msg, 'success')
            
            # Redirecionar para página solicitada ou dashboard
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('index'))
            
        else:
            error = "Credenciais inválidas ou conta inativa"
            if request.is_json:
                return jsonify({'success': False, 'error': error}), 401
            flash(error, 'danger')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Logout do usuário"""
    
    # Desativar sessão personalizada
    deactivate_user_session(current_user)
    
    username = current_user.username
    logout_user()
    
    flash(f"🥷 {username} desconectado com sucesso!", 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile')
@login_required
def profile():
    """Perfil do usuário"""
    return render_template('auth/profile.html', user=current_user)

@auth_bp.route('/api/current-user')
@login_required
def current_user_api():
    """API para obter dados do usuário atual"""
    return jsonify({
        'success': True,
        'user': current_user.to_dict()
    })

@auth_bp.route('/admin/users')
@login_required
def admin_users():
    """Painel administrativo - Lista de usuários"""
    
    if not current_user.is_admin:
        flash("Acesso negado. Apenas administradores.", 'danger')
        return redirect(url_for('main'))
    
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('auth/admin_users.html', users=users)

@auth_bp.route('/admin/create-user', methods=['POST'])
@login_required
def admin_create_user():
    """Criar novo usuário (apenas admin)"""
    
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Acesso negado'}), 403
    
    data = request.get_json()
    
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    is_admin = data.get('is_admin', False)
    
    # Validações
    if not username or not email or not password:
        return jsonify({'success': False, 'error': 'Todos os campos são obrigatórios'}), 400
    
    if len(password) < 6:
        return jsonify({'success': False, 'error': 'Senha deve ter pelo menos 6 caracteres'}), 400
    
    # Verificar se usuário já existe
    if User.query.filter_by(username=username).first():
        return jsonify({'success': False, 'error': 'Username já existe'}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({'success': False, 'error': 'Email já existe'}), 400
    
    try:
        # Criar usuário
        user = User(
            username=username,
            email=email,
            password=password,
            is_admin=is_admin
        )
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Usuário {username} criado com sucesso',
            'user': user.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@auth_bp.route('/admin/toggle-user-status/<int:user_id>', methods=['POST'])
@login_required
def admin_toggle_user_status(user_id):
    """Ativar/desativar usuário"""
    
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Acesso negado'}), 403
    
    user = User.query.get_or_404(user_id)
    
    # Não permitir desativar o próprio usuário admin
    if user.id == current_user.id:
        return jsonify({'success': False, 'error': 'Não é possível desativar sua própria conta'}), 400
    
    user.is_active = not user.is_active
    db.session.commit()
    
    status = "ativado" if user.is_active else "desativado"
    
    return jsonify({
        'success': True,
        'message': f'Usuário {user.username} {status}',
        'user': user.to_dict()
    })

@auth_bp.route('/admin/toggle-user/<int:user_id>', methods=['POST'])
@login_required
def admin_toggle_user(user_id):
    """Ativar/desativar usuário (rota alternativa)"""
    
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Acesso negado'}), 403
    
    data = request.get_json()
    user = User.query.get_or_404(user_id)
    
    # Não permitir alterar o próprio usuário admin
    if user.id == current_user.id:
        return jsonify({'success': False, 'error': 'Não é possível alterar sua própria conta'}), 400
    
    user.is_active = data.get('active', True)
    db.session.commit()
    
    status = "ativado" if user.is_active else "desativado"
    
    return jsonify({
        'success': True,
        'message': f'Usuário {user.username} {status}',
        'user': user.to_dict()
    })

@auth_bp.route('/admin/toggle-admin/<int:user_id>', methods=['POST'])
@login_required
def admin_toggle_admin(user_id):
    """Promover/rebaixar usuário a admin"""
    
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Acesso negado'}), 403
    
    data = request.get_json()
    user = User.query.get_or_404(user_id)
    
    # Não permitir alterar o próprio usuário admin
    if user.id == current_user.id:
        return jsonify({'success': False, 'error': 'Não é possível alterar suas próprias permissões'}), 400
    
    user.is_admin = data.get('is_admin', False)
    db.session.commit()
    
    status = "promovido a admin" if user.is_admin else "removido de admin"
    
    return jsonify({
        'success': True,
        'message': f'Usuário {user.username} {status}',
        'user': user.to_dict()
    })

@auth_bp.route('/admin/users')
@login_required
def admin_users_api():
    """API para listar todos os usuários"""
    
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Acesso negado'}), 403
    
    users = User.query.all()
    
    return jsonify({
        'success': True,
        'users': [user.to_dict() for user in users],
        'total_users': len(users),
        'active_users': len([u for u in users if u.is_active]),
        'admin_users': len([u for u in users if u.is_admin])
    })

@auth_bp.route('/admin/delete-user/<int:user_id>', methods=['DELETE'])
@login_required
def admin_delete_user(user_id):
    """Deletar usuário (apenas admin)"""
    
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Acesso negado'}), 403
    
    user = User.query.get_or_404(user_id)
    
    # Não permitir deletar o próprio usuário admin
    if user.id == current_user.id:
        return jsonify({'success': False, 'error': 'Não é possível deletar sua própria conta'}), 400
    
    try:
        username = user.username
        
        # Deletar sessões do usuário primeiro
        UserSession.query.filter_by(user_id=user.id).delete()
        
        # Deletar usuário
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Usuário {username} deletado com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

def create_user_session(user, request):
    """Criar sessão personalizada para o usuário"""
    try:
        # Desativar sessões antigas
        UserSession.query.filter_by(user_id=user.id, is_active=True).update({'is_active': False})
        
        # Criar nova sessão
        session_token = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(hours=24)
        
        user_session = UserSession(
            user_id=user.id,
            session_token=session_token,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')[:500],
            expires_at=expires_at
        )
        
        db.session.add(user_session)
        db.session.commit()
        
        # Armazenar token na sessão Flask
        session['user_session_token'] = session_token
        
    except Exception as e:
        print(f"Erro ao criar sessão: {e}")

def deactivate_user_session(user):
    """Desativar sessão do usuário"""
    try:
        session_token = session.get('user_session_token')
        if session_token:
            UserSession.query.filter_by(
                session_token=session_token,
                user_id=user.id
            ).update({'is_active': False})
            db.session.commit()
            session.pop('user_session_token', None)
    except Exception as e:
        print(f"Erro ao desativar sessão: {e}")

# Filtro para templates - verificar se usuário é admin
@auth_bp.app_template_filter('is_admin')
def is_admin_filter(user):
    """Filtro para verificar se usuário é admin nos templates"""
    return user and hasattr(user, 'is_admin') and user.is_admin

# Context processor para disponibilizar current_user em todos os templates
@auth_bp.app_context_processor
def inject_user():
    """Injetar current_user em todos os templates"""
    return dict(current_user=current_user)
