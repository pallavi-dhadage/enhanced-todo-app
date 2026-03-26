"""
Simple tests for the Todo API
"""
import pytest
import json
import tempfile
import os

@pytest.fixture
def client():
    """Create a test client with proper database handling"""
    import src.app_working as app_module
    from src.app_working import app
    
    # Create temporary database
    test_db_fd, test_db_path = tempfile.mkstemp()
    
    # Override database path
    original_db = app_module.DATABASE
    app_module.DATABASE = test_db_path
    
    # Re-initialize database with new path
    app_module.init_db()
    
    # Create test client
    with app.test_client() as test_client:
        yield test_client
    
    # Cleanup
    app_module.DATABASE = original_db
    os.close(test_db_fd)
    os.unlink(test_db_path)

@pytest.fixture
def sample_todo(client):
    """Create a sample todo for testing"""
    todo_data = {
        'title': 'Sample Todo',
        'description': 'Sample description',
        'priority': 'high',
        'category': 'Testing'
    }
    response = client.post('/api/todos',
                          data=json.dumps(todo_data),
                          content_type='application/json')
    return json.loads(response.data)['id']

def test_health_endpoint(client):
    """Test health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert 'timestamp' in data

def test_get_empty_todos(client):
    """Test getting todos when empty"""
    response = client.get('/api/todos')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) == 0

def test_create_todo(client):
    """Test creating a new todo"""
    todo_data = {
        'title': 'Test Todo',
        'description': 'Test description',
        'priority': 'high',
        'category': 'Testing'
    }
    
    response = client.post('/api/todos',
                          data=json.dumps(todo_data),
                          content_type='application/json')
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['title'] == 'Test Todo'
    assert 'id' in data

def test_create_todo_without_title(client):
    """Test creating todo without title"""
    response = client.post('/api/todos',
                          data=json.dumps({}),
                          content_type='application/json')
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

def test_get_todos_after_create(client, sample_todo):
    """Test getting todos after creation"""
    response = client.get('/api/todos')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) >= 1
    assert data[0]['title'] == 'Sample Todo'

def test_stats_endpoint(client, sample_todo):
    """Test statistics endpoint"""
    response = client.get('/api/stats')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['total'] >= 1
    assert data['pending'] >= 1

def test_complete_todo(client, sample_todo):
    """Test completing a todo"""
    # Complete it
    complete_response = client.patch(f'/api/todos/{sample_todo}/complete',
                                     data=json.dumps({'completed': True}),
                                     content_type='application/json')
    assert complete_response.status_code == 200
    
    # Verify it's completed
    get_response = client.get('/api/todos')
    todos = json.loads(get_response.data)
    for todo in todos:
        if todo['id'] == sample_todo:
            assert todo['completed'] == 1
            break

def test_update_todo(client, sample_todo):
    """Test updating a todo"""
    update_data = {
        'title': 'Updated Todo',
        'priority': 'low'
    }
    
    response = client.patch(f'/api/todos/{sample_todo}',
                           data=json.dumps(update_data),
                           content_type='application/json')
    assert response.status_code == 200
    
    # Verify update
    get_response = client.get('/api/todos')
    todos = json.loads(get_response.data)
    for todo in todos:
        if todo['id'] == sample_todo:
            assert todo['title'] == 'Updated Todo'
            assert todo['priority'] == 'low'
            break

def test_delete_todo(client, sample_todo):
    """Test deleting a todo"""
    # Delete it
    delete_response = client.delete(f'/api/todos/{sample_todo}')
    assert delete_response.status_code == 200
    
    # Verify it's gone
    get_response = client.get('/api/todos')
    todos = json.loads(get_response.data)
    for todo in todos:
        assert todo['id'] != sample_todo

def test_get_categories(client, sample_todo):
    """Test getting categories"""
    response = client.get('/api/todos/categories')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) >= 1

def test_get_stats_empty_database(client):
    """Test stats with empty database"""
    # Delete all todos
    response = client.get('/api/todos')
    todos = json.loads(response.data)
    for todo in todos:
        client.delete(f'/api/todos/{todo["id"]}')
    
    # Check stats
    response = client.get('/api/stats')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['total'] == 0
    assert data['pending'] == 0
    assert data['completed'] == 0
