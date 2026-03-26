import pytest
from datetime import datetime, timedelta
from src.models.database import db, User, Todo

def test_create_user(app):
    """Test user creation"""
    user = User(
        username='testuser',
        email='test@example.com'
    )
    user.password = 'testpass123'
    
    db.session.add(user)
    db.session.commit()
    
    assert user.id is not None
    assert user.username == 'testuser'
    assert user.email == 'test@example.com'
    assert user.check_password('testpass123')
    assert not user.check_password('wrongpass')

def test_create_todo(app, test_user):
    """Test todo creation"""
    todo = Todo(
        title='Test Todo',
        description='Test description',
        priority='high',
        category='Testing',
        due_date=datetime.now().date() + timedelta(days=1),
        user_id=test_user.id
    )
    
    db.session.add(todo)
    db.session.commit()
    
    assert todo.id is not None
    assert todo.title == 'Test Todo'
    assert todo.priority == 'high'
    assert not todo.completed

def test_todo_to_dict(test_todo):
    """Test todo to dict conversion"""
    todo_dict = test_todo.to_dict()
    
    assert 'id' in todo_dict
    assert 'title' in todo_dict
    assert 'priority' in todo_dict
    assert 'completed' in todo_dict
    assert 'created_at' in todo_dict
