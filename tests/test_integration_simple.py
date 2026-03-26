"""
Simple integration tests for Todo API
"""
import pytest
import json
import tempfile
import os

@pytest.fixture
def client():
    """Create a test client"""
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

def test_simple_workflow(client):
    """Test basic workflow without complex fixtures"""
    
    # Create todo
    response = client.post('/api/todos',
                          data=json.dumps({'title': 'Integration Test'}),
                          content_type='application/json')
    assert response.status_code == 201
    todo_data = json.loads(response.data)
    todo_id = todo_data['id']
    
    # Get all todos
    response = client.get('/api/todos')
    assert response.status_code == 200
    todos = json.loads(response.data)
    assert len(todos) >= 1
    
    # Update todo
    response = client.patch(f'/api/todos/{todo_id}',
                           data=json.dumps({'title': 'Updated'}),
                           content_type='application/json')
    assert response.status_code == 200
    
    # Complete todo
    response = client.patch(f'/api/todos/{todo_id}/complete',
                           data=json.dumps({'completed': True}),
                           content_type='application/json')
    assert response.status_code == 200
    
    # Check stats
    response = client.get('/api/stats')
    assert response.status_code == 200
    stats = json.loads(response.data)
    assert stats['completed'] >= 1
    
    # Delete todo
    response = client.delete(f'/api/todos/{todo_id}')
    assert response.status_code == 200

def test_multiple_operations(client):
    """Test multiple operations in sequence"""
    
    # Create multiple todos
    todo_ids = []
    for i in range(3):
        response = client.post('/api/todos',
                              data=json.dumps({'title': f'Todo {i}'}),
                              content_type='application/json')
        assert response.status_code == 201
        todo_ids.append(json.loads(response.data)['id'])
    
    # Delete all
    for todo_id in todo_ids:
        response = client.delete(f'/api/todos/{todo_id}')
        assert response.status_code == 200
    
    # Verify all deleted
    response = client.get('/api/todos')
    todos = json.loads(response.data)
    assert all(t['id'] not in todo_ids for t in todos)
