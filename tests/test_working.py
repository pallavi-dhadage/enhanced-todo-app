"""
Simplified tests that only test the working app
"""
import pytest
import json
import tempfile
import os

@pytest.fixture
def client():
    """Create a test client with the working app"""
    import src.app_working as app_module
    from src.app_working import app
    
    # Create temporary database
    test_db_fd, test_db_path = tempfile.mkstemp()
    
    # Override database path
    original_db = app_module.DATABASE
    app_module.DATABASE = test_db_path
    
    # Re-initialize database
    app_module.init_db()
    
    # Create test client
    with app.test_client() as test_client:
        yield test_client
    
    # Cleanup
    app_module.DATABASE = original_db
    os.close(test_db_fd)
    os.unlink(test_db_path)

def test_health_endpoint(client):
    """Test health check"""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'

def test_index_endpoint(client):
    """Test index endpoint"""
    response = client.get('/')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['name'] == 'Todo API'
    assert 'endpoints' in data

def test_create_todo(client):
    """Test creating a todo"""
    response = client.post('/api/todos',
                          data=json.dumps({'title': 'Test Todo'}),
                          content_type='application/json')
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['title'] == 'Test Todo'
    assert 'id' in data

def test_get_todos(client):
    """Test getting todos"""
    # Create a todo first
    client.post('/api/todos',
               data=json.dumps({'title': 'Test Todo'}),
               content_type='application/json')
    
    # Get todos
    response = client.get('/api/todos')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) >= 1

def test_stats_endpoint(client):
    """Test statistics endpoint"""
    response = client.get('/api/stats')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'total' in data
    assert 'pending' in data
    assert 'completed' in data
    assert isinstance(data['total'], int)

def test_categories_endpoint(client):
    """Test categories endpoint"""
    response = client.get('/api/todos/categories')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)

def test_create_todo_with_all_fields(client):
    """Test creating todo with all fields"""
    todo_data = {
        'title': 'Complete Project',
        'description': 'Finish the todo app',
        'priority': 'high',
        'category': 'Work',
        'due_date': '2025-12-31'
    }
    
    response = client.post('/api/todos',
                          data=json.dumps(todo_data),
                          content_type='application/json')
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['title'] == 'Complete Project'

def test_update_todo(client):
    """Test updating a todo"""
    # Create todo
    create_response = client.post('/api/todos',
                                  data=json.dumps({'title': 'Original'}),
                                  content_type='application/json')
    todo_id = json.loads(create_response.data)['id']
    
    # Update todo
    update_response = client.patch(f'/api/todos/{todo_id}',
                                   data=json.dumps({'title': 'Updated'}),
                                   content_type='application/json')
    assert update_response.status_code == 200
    
    # Verify update
    get_response = client.get('/api/todos')
    todos = json.loads(get_response.data)
    for todo in todos:
        if todo['id'] == todo_id:
            assert todo['title'] == 'Updated'

def test_complete_todo(client):
    """Test completing a todo"""
    # Create todo
    create_response = client.post('/api/todos',
                                  data=json.dumps({'title': 'To Complete'}),
                                  content_type='application/json')
    todo_id = json.loads(create_response.data)['id']
    
    # Complete todo
    complete_response = client.patch(f'/api/todos/{todo_id}/complete',
                                     data=json.dumps({'completed': True}),
                                     content_type='application/json')
    assert complete_response.status_code == 200
    
    # Verify completed
    get_response = client.get('/api/todos')
    todos = json.loads(get_response.data)
    for todo in todos:
        if todo['id'] == todo_id:
            assert todo['completed'] == 1

def test_delete_todo(client):
    """Test deleting a todo"""
    # Create todo
    create_response = client.post('/api/todos',
                                  data=json.dumps({'title': 'To Delete'}),
                                  content_type='application/json')
    todo_id = json.loads(create_response.data)['id']
    
    # Delete todo
    delete_response = client.delete(f'/api/todos/{todo_id}')
    assert delete_response.status_code == 200
    
    # Verify deleted
    get_response = client.get('/api/todos')
    todos = json.loads(get_response.data)
    assert all(t['id'] != todo_id for t in todos)
