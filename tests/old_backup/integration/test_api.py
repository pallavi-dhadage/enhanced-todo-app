import pytest
import json

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'status' in data
    assert data['status'] == 'healthy'

def test_user_registration(client):
    """Test user registration"""
    data = {
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'password123'
    }
    
    response = client.post('/api/register', json=data)
    assert response.status_code == 201
    
    data = json.loads(response.data)
    assert data['message'] == 'User created successfully'
    assert 'user' in data

def test_user_login(client, test_user):
    """Test user login"""
    data = {
        'username': test_user.username,
        'password': 'testpass123'
    }
    
    response = client.post('/api/login', json=data)
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'access_token' in data
    assert 'user' in data

def test_create_todo_authenticated(client, auth_token):
    """Test creating todo with authentication"""
    headers = {'Authorization': f'Bearer {auth_token}'}
    data = {
        'title': 'New Todo',
        'priority': 'high',
        'category': 'Work'
    }
    
    response = client.post('/api/todos', json=data, headers=headers)
    assert response.status_code == 201
    
    data = json.loads(response.data)
    assert data['title'] == 'New Todo'
    assert data['priority'] == 'high'
