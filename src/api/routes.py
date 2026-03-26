from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from datetime import datetime, timedelta
from sqlalchemy import func, and_
from src.models.database import db, Todo, User
from src.utils.cache import cache
from src.services.email_service import send_todo_reminder

api_bp = Blueprint('api', __name__)

@api_bp.route('/register', methods=['POST'])
def register():
    """User registration"""
    data = request.get_json()
    
    # Validate input
    if not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Username, email and password required'}), 400
    
    # Check if user exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 409
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 409
    
    # Create user
    user = User(
        username=data['username'],
        email=data['email']
    )
    user.password = data['password']
    
    db.session.add(user)
    db.session.commit()
    
    # Send welcome email
    send_todo_reminder(user.email, 'welcome', {'username': user.username})
    
    return jsonify({
        'message': 'User created successfully',
        'user': user.to_dict()
    }), 201

@api_bp.route('/login', methods=['POST'])
def login():
    """User login"""
    data = request.get_json()
    
    # Find user
    user = User.query.filter_by(username=data.get('username')).first()
    
    if not user or not user.check_password(data.get('password')):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Create access token
    access_token = create_access_token(
        identity=user.id,
        expires_delta=timedelta(hours=24)
    )
    
    return jsonify({
        'access_token': access_token,
        'user': user.to_dict()
    }), 200

@api_bp.route('/todos', methods=['GET'])
@jwt_required()
@cache.cached(timeout=60, query_string=True)
def get_todos():
    """Get user's todos with filters"""
    user_id = get_jwt_identity()
    
    # Get filter parameters
    priority = request.args.get('priority')
    category = request.args.get('category')
    status = request.args.get('status')
    search = request.args.get('search')
    
    # Build query
    query = Todo.query.filter_by(user_id=user_id)
    
    if priority and priority != 'all':
        query = query.filter_by(priority=priority)
    
    if category and category != 'all':
        query = query.filter_by(category=category)
    
    if status == 'completed':
        query = query.filter_by(completed=True)
    elif status == 'pending':
        query = query.filter_by(completed=False)
    
    if search:
        query = query.filter(Todo.title.ilike(f'%{search}%') | Todo.description.ilike(f'%{search}%'))
    
    todos = query.order_by(Todo.priority.desc(), Todo.due_date.asc(), Todo.created_at.desc()).all()
    
    return jsonify([todo.to_dict() for todo in todos]), 200

@api_bp.route('/todos', methods=['POST'])
@jwt_required()
def create_todo():
    """Create a new todo"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data.get('title'):
        return jsonify({'error': 'Title required'}), 400
    
    todo = Todo(
        title=data['title'],
        description=data.get('description', ''),
        priority=data.get('priority', 'medium'),
        category=data.get('category', 'General'),
        due_date=datetime.fromisoformat(data['due_date']) if data.get('due_date') else None,
        user_id=user_id
    )
    
    db.session.add(todo)
    db.session.commit()
    
    # Clear cache
    cache.clear()
    
    return jsonify(todo.to_dict()), 201

@api_bp.route('/todos/<int:todo_id>', methods=['PUT'])
@jwt_required()
def update_todo(todo_id):
    """Update a todo"""
    user_id = get_jwt_identity()
    todo = Todo.query.filter_by(id=todo_id, user_id=user_id).first_or_404()
    
    data = request.get_json()
    
    todo.title = data.get('title', todo.title)
    todo.description = data.get('description', todo.description)
    todo.priority = data.get('priority', todo.priority)
    todo.category = data.get('category', todo.category)
    todo.due_date = datetime.fromisoformat(data['due_date']) if data.get('due_date') else todo.due_date
    
    db.session.commit()
    
    # Clear cache
    cache.clear()
    
    return jsonify(todo.to_dict()), 200

@api_bp.route('/todos/<int:todo_id>', methods=['DELETE'])
@jwt_required()
def delete_todo(todo_id):
    """Delete a todo"""
    user_id = get_jwt_identity()
    todo = Todo.query.filter_by(id=todo_id, user_id=user_id).first_or_404()
    
    db.session.delete(todo)
    db.session.commit()
    
    # Clear cache
    cache.clear()
    
    return jsonify({'message': 'Todo deleted'}), 200

@api_bp.route('/todos/<int:todo_id>/complete', methods=['PATCH'])
@jwt_required()
def complete_todo(todo_id):
    """Mark todo as complete"""
    user_id = get_jwt_identity()
    todo = Todo.query.filter_by(id=todo_id, user_id=user_id).first_or_404()
    
    todo.completed = not todo.completed
    db.session.commit()
    
    # Clear cache
    cache.clear()
    
    return jsonify(todo.to_dict()), 200

@api_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """Get user statistics"""
    user_id = get_jwt_identity()
    
    stats = db.session.query(
        func.count(Todo.id).label('total'),
        func.sum(func.cast(Todo.completed, db.Integer)).label('completed'),
        func.sum(func.cast(~Todo.completed, db.Integer)).label('pending'),
        func.count(db.case((and_(Todo.priority == 'high', Todo.completed == False), 1))).label('high_priority'),
        func.count(func.distinct(Todo.category)).label('categories')
    ).filter_by(user_id=user_id).first()
    
    return jsonify({
        'total': stats.total or 0,
        'completed': stats.completed or 0,
        'pending': stats.pending or 0,
        'high_priority_pending': stats.high_priority or 0,
        'categories': stats.categories or 0
    }), 200
