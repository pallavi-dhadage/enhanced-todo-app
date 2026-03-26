"""
Integration tests for the Todo API
"""
import pytest
import json
import time

def test_full_workflow(client):
    """Test complete workflow from creation to deletion"""
    
    # 1. Create multiple todos
    todos_created = []
    for i in range(3):
        response = client.post('/api/todos',
                              data=json.dumps({
                                  'title': f'Integration Test Todo {i}',
                                  'priority': 'high' if i == 0 else 'medium',
                                  'category': f'Category{i}'
                              }),
                              content_type='application/json')
        assert response.status_code == 201
        todo_id = json.loads(response.data)['id']
        todos_created.append(todo_id)
    
    # 2. Get all todos and verify count
    response = client.get('/api/todos')
    todos = json.loads(response.data)
    assert len(todos) >= 3
    
    # 3. Update a todo
    update_response = client.patch(f'/api/todos/{todos_created[0]}',
                                   data=json.dumps({'title': 'Updated Title'}),
                                   content_type='application/json')
    assert update_response.status_code == 200
    
    # 4. Complete a todo
    complete_response = client.patch(f'/api/todos/{todos_created[0]}/complete',
                                     data=json.dumps({'completed': True}),
                                     content_type='application/json')
    assert complete_response.status_code == 200
    
    # 5. Check stats
    stats_response = client.get('/api/stats')
    stats = json.loads(stats_response.data)
    assert stats['total'] >= 3
    assert stats['completed'] >= 1
    
    # 6. Delete todos
    for todo_id in todos_created:
        delete_response = client.delete(f'/api/todos/{todo_id}')
        assert delete_response.status_code == 200
    
    # 7. Verify all deleted
    final_response = client.get('/api/todos')
    final_todos = json.loads(final_response.data)
    for todo_id in todos_created:
        assert all(t['id'] != todo_id for t in final_todos)

def test_concurrent_operations(client, sample_todo):
    """Test multiple operations in sequence"""
    
    # Create todo
    response = client.post('/api/todos',
                          data=json.dumps({'title': 'Concurrent Test'}),
                          content_type='application/json')
    todo_id = json.loads(response.data)['id']
    
    # Update multiple times
    for i in range(3):
        response = client.patch(f'/api/todos/{todo_id}',
                               data=json.dumps({'title': f'Update {i}'}),
                               content_type='application/json')
        assert response.status_code == 200
    
    # Complete and delete
    client.patch(f'/api/todos/{todo_id}/complete',
                data=json.dumps({'completed': True}),
                content_type='application/json')
    client.delete(f'/api/todos/{todo_id}')
    
    # Verify deleted
    response = client.get('/api/todos')
    todos = json.loads(response.data)
    assert all(t['id'] != todo_id for t in todos)

def test_error_handling(client):
    """Test error handling scenarios"""
    
    # Test invalid JSON
    response = client.post('/api/todos',
                          data='invalid json',
                          content_type='application/json')
    # Should return error
    assert response.status_code in [400, 500]
    
    # Test missing title
    response = client.post('/api/todos',
                          data=json.dumps({'description': 'No title'}),
                          content_type='application/json')
    assert response.status_code == 400
    
    # Test empty title
    response = client.post('/api/todos',
                          data=json.dumps({'title': ''}),
                          content_type='application/json')
    assert response.status_code == 400

def test_database_persistence(client):
    """Test that data persists between requests"""
    
    # Create todo
    response = client.post('/api/todos',
                          data=json.dumps({'title': 'Persistent Todo'}),
                          content_type='application/json')
    todo_id = json.loads(response.data)['id']
    
    # Make multiple requests
    for _ in range(5):
        response = client.get('/api/todos')
        todos = json.loads(response.data)
        assert any(t['id'] == todo_id for t in todos)
    
    # Clean up
    client.delete(f'/api/todos/{todo_id}')
