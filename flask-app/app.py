from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

# Database configuration
DATABASE = '/app/data/todos.db'

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with enhanced schema"""
    with get_db() as conn:
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

@app.context_processor
def utility_processor():
    def now():
        return datetime.now().strftime('%Y-%m-%d')
    return dict(now=now)

@app.route('/')
def index():
    """Home page - show all todos with filters"""
    # Get filter parameters
    priority_filter = request.args.get('priority', 'all')
    category_filter = request.args.get('category', 'all')
    status_filter = request.args.get('status', 'all')
    search_query = request.args.get('search', '')
    
    # Build query
    query = 'SELECT * FROM todos WHERE 1=1'
    params = []
    
    if priority_filter != 'all':
        query += ' AND priority = ?'
        params.append(priority_filter)
    
    if category_filter != 'all':
        query += ' AND category = ?'
        params.append(category_filter)
    
    if status_filter == 'completed':
        query += ' AND completed = 1'
    elif status_filter == 'pending':
        query += ' AND completed = 0'
    
    if search_query:
        query += ' AND (title LIKE ? OR description LIKE ?)'
        params.append(f'%{search_query}%')
        params.append(f'%{search_query}%')
    
    query += ' ORDER BY priority DESC, due_date ASC, created_at DESC'
    
    with get_db() as conn:
        todos = conn.execute(query, params).fetchall()
        # Get unique categories for filter dropdown
        categories = conn.execute('SELECT DISTINCT category FROM todos').fetchall()
    
    return render_template('index.html', 
                         todos=todos, 
                         categories=[c[0] for c in categories],
                         priority_filter=priority_filter,
                         category_filter=category_filter,
                         status_filter=status_filter,
                         search_query=search_query)

@app.route('/add', methods=['POST'])
def add_todo():
    """Add a new todo with enhanced fields"""
    title = request.form.get('title')
    description = request.form.get('description', '')
    priority = request.form.get('priority', 'medium')
    category = request.form.get('category', 'General')
    due_date = request.form.get('due_date', '')
    
    if title:
        with get_db() as conn:
            conn.execute('''
                INSERT INTO todos (title, description, priority, category, due_date)
                VALUES (?, ?, ?, ?, ?)
            ''', (title, description, priority, category, due_date if due_date else None))
            conn.commit()
    
    return redirect(url_for('index'))

@app.route('/complete/<int:todo_id>')
def complete_todo(todo_id):
    """Mark todo as complete"""
    with get_db() as conn:
        conn.execute('UPDATE todos SET completed = 1 WHERE id = ?', (todo_id,))
        conn.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:todo_id>')
def delete_todo(todo_id):
    """Delete a todo"""
    with get_db() as conn:
        conn.execute('DELETE FROM todos WHERE id = ?', (todo_id,))
        conn.commit()
    return redirect(url_for('index'))

@app.route('/edit/<int:todo_id>', methods=['GET', 'POST'])
def edit_todo(todo_id):
    """Edit an existing todo"""
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        priority = request.form.get('priority')
        category = request.form.get('category')
        due_date = request.form.get('due_date')
        
        with get_db() as conn:
            conn.execute('''
                UPDATE todos 
                SET title=?, description=?, priority=?, category=?, due_date=?
                WHERE id=?
            ''', (title, description, priority, category, due_date, todo_id))
            conn.commit()
        return redirect(url_for('index'))
    
    with get_db() as conn:
        todo = conn.execute('SELECT * FROM todos WHERE id = ?', (todo_id,)).fetchone()
    return render_template('edit.html', todo=todo)

# API Endpoints
@app.route('/api/todos', methods=['GET'])
def api_get_todos():
    """Get all todos as JSON"""
    with get_db() as conn:
        todos = conn.execute('SELECT * FROM todos ORDER BY created_at DESC').fetchall()
    return jsonify([dict(todo) for todo in todos])

@app.route('/api/todos', methods=['POST'])
def api_add_todo():
    """Add todo via API"""
    data = request.get_json()
    title = data.get('title')
    if title:
        with get_db() as conn:
            cur = conn.execute('''
                INSERT INTO todos (title, description, priority, category, due_date)
                VALUES (?, ?, ?, ?, ?)
                RETURNING id
            ''', (title, data.get('description', ''), 
                  data.get('priority', 'medium'), 
                  data.get('category', 'General'),
                  data.get('due_date', None)))
            todo_id = cur.lastrowid
            conn.commit()
        return jsonify({'success': True, 'id': todo_id}), 201
    return jsonify({'error': 'Title required'}), 400

@app.route('/api/stats', methods=['GET'])
def api_get_stats():
    """Get todo statistics"""
    with get_db() as conn:
        stats = conn.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN completed = 0 THEN 1 ELSE 0 END) as pending,
                SUM(CASE WHEN completed = 1 THEN 1 ELSE 0 END) as completed,
                SUM(CASE WHEN priority = 'high' AND completed = 0 THEN 1 ELSE 0 END) as high_priority_pending,
                COUNT(DISTINCT category) as categories
            FROM todos
        ''').fetchone()
    
    return jsonify({
        'total': stats['total'],
        'pending': stats['pending'],
        'completed': stats['completed'],
        'high_priority_pending': stats['high_priority_pending'],
        'categories': stats['categories']
    })

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
