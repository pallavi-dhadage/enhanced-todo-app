from flask import Flask, jsonify, request, g
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime
from contextlib import closing

app = Flask(__name__)
CORS(app)  # Enable CORS for all origins

# Database setup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE = os.path.join(BASE_DIR, 'data', 'todos.db')

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    os.makedirs(os.path.dirname(DATABASE), exist_ok=True)
    with closing(sqlite3.connect(DATABASE)) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                priority TEXT DEFAULT 'medium',
                category TEXT DEFAULT 'General',
                due_date DATE,
                completed BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

app.teardown_appcontext(close_db)

@app.route('/')
def index():
    return jsonify({
        'name': 'Todo API',
        'version': '1.0.0',
        'endpoints': [
            'GET /health',
            'GET /api/todos',
            'POST /api/todos',
            'DELETE /api/todos/<id>',
            'PATCH /api/todos/<id>/complete',
            'GET /api/stats',
            'GET /api/todos/categories'
        ]
    })

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'database': 'connected',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/todos', methods=['GET'])
def get_todos():
    try:
        db = get_db()
        todos = db.execute('SELECT * FROM todos ORDER BY created_at DESC').fetchall()
        return jsonify([dict(todo) for todo in todos])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/todos', methods=['POST'])
def create_todo():
    try:
        data = request.get_json()
        title = data.get('title')
        if not title:
            return jsonify({'error': 'Title required'}), 400
        
        db = get_db()
        cursor = db.execute('''
            INSERT INTO todos (title, description, priority, category, due_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            title,
            data.get('description', ''),
            data.get('priority', 'medium'),
            data.get('category', 'General'),
            data.get('due_date')
        ))
        db.commit()
        
        return jsonify({
            'id': cursor.lastrowid,
            'title': title,
            'message': 'Todo created successfully'
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    try:
        db = get_db()
        db.execute('DELETE FROM todos WHERE id = ?', (todo_id,))
        db.commit()
        return jsonify({'message': 'Todo deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/todos/<int:todo_id>/complete', methods=['PATCH'])
def complete_todo(todo_id):
    try:
        data = request.get_json()
        completed = data.get('completed', True)
        db = get_db()
        db.execute('UPDATE todos SET completed = ? WHERE id = ?', (1 if completed else 0, todo_id))
        db.commit()
        return jsonify({'message': 'Todo status updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        db = get_db()
        stats = db.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN completed = 0 THEN 1 ELSE 0 END) as pending,
                SUM(CASE WHEN completed = 1 THEN 1 ELSE 0 END) as completed,
                SUM(CASE WHEN priority = 'high' AND completed = 0 THEN 1 ELSE 0 END) as high_priority,
                COUNT(DISTINCT category) as categories
            FROM todos
        ''').fetchone()
        
        return jsonify({
            'total': stats['total'] or 0,
            'pending': stats['pending'] or 0,
            'completed': stats['completed'] or 0,
            'high_priority': stats['high_priority'] or 0,
            'categories': stats['categories'] or 0
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/todos/categories', methods=['GET'])
def get_categories():
    try:
        db = get_db()
        categories = db.execute('''
            SELECT category, COUNT(*) as count 
            FROM todos 
            WHERE category IS NOT NULL AND category != ''
            GROUP BY category 
            ORDER BY count DESC
        ''').fetchall()
        return jsonify([dict(cat) for cat in categories]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Initialize database
init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
