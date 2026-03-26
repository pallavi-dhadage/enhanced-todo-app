import React, { useState, useEffect } from 'react';

function App() {
  const [todos, setTodos] = useState([]);
  const [stats, setStats] = useState({});
  const [categories, setCategories] = useState([]);
  const [newTodo, setNewTodo] = useState({
    title: '',
    description: '',
    priority: 'medium',
    category: '',
    due_date: ''
  });
  const [editingTodo, setEditingTodo] = useState(null);
  const [filter, setFilter] = useState({
    priority: 'all',
    category: 'all',
    status: 'all',
    search: ''
  });
  const [showSidebar, setShowSidebar] = useState(true);
  const [loading, setLoading] = useState(true);

  const API_URL = "http://localhost:5000/api"

  // Load data
  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [todosRes, statsRes, categoriesRes] = await Promise.all([
        fetch(API_URL + "/todos"),
        fetch(API_URL + "/stats"),
        fetch(API_URL + "/todos/categories")
      ]);
      setTodos(await todosRes.json());
      setStats(await statsRes.json());
      setCategories(await categoriesRes.json());
    } catch (error) {
      console.error("Error loading data:", error);
    }
    setLoading(false);
  };

  // Create todo
  const createTodo = async (e) => {
    e.preventDefault();
    if (!newTodo.title.trim()) return;

    try {
      await fetch(API_URL + "/todos", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newTodo)
      });
      setNewTodo({
        title: '',
        description: '',
        priority: 'medium',
        category: '',
        due_date: ''
      });
      loadData();
    } catch (error) {
      console.error("Error creating todo:", error);
      alert("Failed to add task. Make sure backend is running on port 5000");
    }
  };

  // Update todo
  const updateTodo = async (id, updatedTodo) => {
    try {
      await fetch(API_URL + "/todos/" + id, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(updatedTodo)
      });
      setEditingTodo(null);
      loadData();
    } catch (error) {
      console.error("Error updating todo:", error);
    }
  };

  // Complete todo
  const completeTodo = async (id, completed) => {
    try {
      await fetch(API_URL + "/todos/" + id + "/complete", {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ completed: !completed })
      });
      loadData();
    } catch (error) {
      console.error("Error completing todo:", error);
    }
  };

  // Delete todo
  const deleteTodo = async (id) => {
    if (!window.confirm("Are you sure you want to delete this task?")) return;
    
    try {
      await fetch(API_URL + "/todos/" + id, {
        method: "DELETE"
      });
      loadData();
    } catch (error) {
      console.error("Error deleting todo:", error);
    }
  };

  // Filter todos
  const filteredTodos = todos.filter(todo => {
    if (filter.priority !== 'all' && todo.priority !== filter.priority) return false;
    if (filter.category !== 'all' && todo.category !== filter.category) return false;
    if (filter.status === 'completed' && !todo.completed) return false;
    if (filter.status === 'pending' && todo.completed) return false;
    if (filter.search && !todo.title.toLowerCase().includes(filter.search.toLowerCase())) return false;
    return true;
  });

  const getPriorityColor = (priority) => {
    switch(priority) {
      case 'high': return { bg: '#fee2e2', color: '#dc2626', icon: '🔴' };
      case 'medium': return { bg: '#fef9c3', color: '#ca8a04', icon: '🟡' };
      case 'low': return { bg: '#dcfce7', color: '#16a34a', icon: '🟢' };
      default: return { bg: '#f3f4f6', color: '#6b7280', icon: '⚪' };
    }
  };

  const styles = {
    app: {
      display: 'flex',
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    },
    sidebar: {
      width: showSidebar ? '280px' : '60px',
      backgroundColor: 'white',
      boxShadow: '2px 0 8px rgba(0,0,0,0.1)',
      transition: 'width 0.3s',
      overflow: 'hidden'
    },
    sidebarToggle: {
      padding: '20px',
      textAlign: 'center',
      cursor: 'pointer',
      fontSize: '24px',
      borderBottom: '1px solid #eee'
    },
    sidebarContent: {
      padding: '20px'
    },
    statsCard: {
      backgroundColor: '#f8f9fa',
      padding: '15px',
      marginBottom: '15px',
      borderRadius: '10px',
      textAlign: 'center'
    },
    main: {
      flex: 1,
      padding: '20px',
      overflowY: 'auto'
    },
    header: {
      backgroundColor: 'white',
      borderRadius: '10px',
      padding: '20px',
      marginBottom: '20px',
      textAlign: 'center'
    },
    formContainer: {
      backgroundColor: 'white',
      padding: '20px',
      marginBottom: '20px',
      borderRadius: '10px'
    },
    formGroup: {
      marginBottom: '15px'
    },
    input: {
      width: '100%',
      padding: '10px',
      border: '1px solid #ddd',
      borderRadius: '5px',
      fontSize: '14px'
    },
    textarea: {
      width: '100%',
      padding: '10px',
      border: '1px solid #ddd',
      borderRadius: '5px',
      fontSize: '14px',
      minHeight: '80px'
    },
    select: {
      width: '100%',
      padding: '10px',
      border: '1px solid #ddd',
      borderRadius: '5px',
      fontSize: '14px'
    },
    button: {
      backgroundColor: '#667eea',
      color: 'white',
      padding: '12px 24px',
      border: 'none',
      borderRadius: '5px',
      cursor: 'pointer',
      fontSize: '16px',
      fontWeight: 'bold'
    },
    filterBar: {
      backgroundColor: 'white',
      padding: '15px',
      marginBottom: '20px',
      borderRadius: '10px',
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
      gap: '10px'
    },
    todoCard: {
      backgroundColor: 'white',
      padding: '15px',
      marginBottom: '10px',
      borderRadius: '10px',
      transition: 'transform 0.2s',
      cursor: 'pointer'
    },
    todoHeader: {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      marginBottom: '10px'
    },
    todoTitle: {
      fontSize: '18px',
      fontWeight: 'bold',
      display: 'flex',
      alignItems: 'center',
      gap: '10px'
    },
    todoMeta: {
      display: 'flex',
      gap: '10px',
      flexWrap: 'wrap',
      marginTop: '10px'
    },
    badge: {
      padding: '4px 8px',
      borderRadius: '5px',
      fontSize: '12px',
      fontWeight: 'bold'
    }
  };

  return (
    <div style={styles.app}>
      {/* Sidebar */}
      <div style={styles.sidebar}>
        <div style={styles.sidebarToggle} onClick={() => setShowSidebar(!showSidebar)}>
          {showSidebar ? '◀' : '▶'}
        </div>
        {showSidebar && (
          <div style={styles.sidebarContent}>
            <h3>Statistics</h3>
            <div style={styles.statsCard}>
              <div style={{ fontSize: '28px', fontWeight: 'bold', color: '#3b82f6' }}>{stats.total || 0}</div>
              <div>Total Tasks</div>
            </div>
            <div style={styles.statsCard}>
              <div style={{ fontSize: '28px', fontWeight: 'bold', color: '#eab308' }}>{stats.pending || 0}</div>
              <div>Pending</div>
            </div>
            <div style={styles.statsCard}>
              <div style={{ fontSize: '28px', fontWeight: 'bold', color: '#22c55e' }}>{stats.completed || 0}</div>
              <div>Completed</div>
            </div>
            <div style={styles.statsCard}>
              <div style={{ fontSize: '28px', fontWeight: 'bold', color: '#ef4444' }}>{stats.high_priority || 0}</div>
              <div>High Priority</div>
            </div>
            
            <h3 style={{ marginTop: '20px' }}>Categories</h3>
            {categories.map(cat => (
              <div key={cat.category} style={{ ...styles.statsCard, padding: '10px' }}>
                <div style={{ fontWeight: 'bold' }}>{cat.category}</div>
                <div style={{ fontSize: '12px', color: '#666' }}>{cat.count} tasks</div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Main Content */}
      <div style={styles.main}>
        <div style={styles.header}>
          <h1 style={{ margin: 0, color: '#667eea' }}>Todo Manager</h1>
          <p>Organize your tasks efficiently</p>
        </div>

        {/* Add Task Form */}
        <div style={styles.formContainer}>
          <h3>Add New Task</h3>
          <form onSubmit={createTodo}>
            <div style={styles.formGroup}>
              <input
                type="text"
                placeholder="Task title *"
                value={newTodo.title}
                onChange={(e) => setNewTodo({...newTodo, title: e.target.value})}
                style={styles.input}
                required
              />
            </div>
            <div style={styles.formGroup}>
              <textarea
                placeholder="Description"
                value={newTodo.description}
                onChange={(e) => setNewTodo({...newTodo, description: e.target.value})}
                style={styles.textarea}
              />
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '10px', marginBottom: '15px' }}>
              <select
                value={newTodo.priority}
                onChange={(e) => setNewTodo({...newTodo, priority: e.target.value})}
                style={styles.select}
              >
                <option value="high">🔴 High Priority</option>
                <option value="medium">🟡 Medium Priority</option>
                <option value="low">🟢 Low Priority</option>
              </select>
              <input
                type="text"
                placeholder="Category"
                value={newTodo.category}
                onChange={(e) => setNewTodo({...newTodo, category: e.target.value})}
                style={styles.input}
              />
              <input
                type="date"
                value={newTodo.due_date}
                onChange={(e) => setNewTodo({...newTodo, due_date: e.target.value})}
                style={styles.input}
              />
            </div>
            <button type="submit" style={styles.button}>Add Task</button>
          </form>
        </div>

        {/* Filters */}
        <div style={styles.filterBar}>
          <select value={filter.priority} onChange={(e) => setFilter({...filter, priority: e.target.value})} style={styles.select}>
            <option value="all">All Priorities</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
          <select value={filter.category} onChange={(e) => setFilter({...filter, category: e.target.value})} style={styles.select}>
            <option value="all">All Categories</option>
            {categories.map(cat => <option key={cat.category} value={cat.category}>{cat.category}</option>)}
          </select>
          <select value={filter.status} onChange={(e) => setFilter({...filter, status: e.target.value})} style={styles.select}>
            <option value="all">All</option>
            <option value="pending">Pending</option>
            <option value="completed">Completed</option>
          </select>
          <input
            type="text"
            placeholder="Search..."
            value={filter.search}
            onChange={(e) => setFilter({...filter, search: e.target.value})}
            style={styles.input}
          />
          <button onClick={() => setFilter({priority: 'all', category: 'all', status: 'all', search: ''})} style={{...styles.button, backgroundColor: '#6b7280'}}>
            Clear
          </button>
        </div>

        {/* Todo List */}
        {loading ? (
          <div style={{ textAlign: 'center', color: 'white' }}>Loading...</div>
        ) : filteredTodos.length === 0 ? (
          <div style={{ textAlign: 'center', color: 'white', padding: '40px' }}>No tasks found! Add your first task above.</div>
        ) : (
          filteredTodos.map(todo => {
            const priorityStyle = getPriorityColor(todo.priority);
            return (
              <div key={todo.id} style={styles.todoCard}>
                <div style={styles.todoHeader}>
                  <div style={styles.todoTitle}>
                    <button onClick={() => completeTodo(todo.id, todo.completed)} style={{ fontSize: '24px', background: 'none', border: 'none', cursor: 'pointer' }}>
                      {todo.completed ? '✅' : '○'}
                    </button>
                    <span style={{ textDecoration: todo.completed ? 'line-through' : 'none' }}>{todo.title}</span>
                  </div>
                  <div>
                    <button onClick={() => setEditingTodo(todo)} style={{ marginRight: '10px', background: 'none', border: 'none', cursor: 'pointer', fontSize: '18px' }}>✏️</button>
                    <button onClick={() => deleteTodo(todo.id)} style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: '18px' }}>🗑️</button>
                  </div>
                </div>
                {todo.description && <div style={{ color: '#666', marginBottom: '10px' }}>{todo.description}</div>}
                <div style={styles.todoMeta}>
                  <span style={{ ...styles.badge, backgroundColor: priorityStyle.bg, color: priorityStyle.color }}>{priorityStyle.icon} {todo.priority}</span>
                  {todo.category && <span style={{ ...styles.badge, backgroundColor: '#e9d5ff', color: '#7c3aed' }}>📁 {todo.category}</span>}
                  {todo.due_date && <span style={{ ...styles.badge, backgroundColor: '#dbeafe', color: '#2563eb' }}>📅 {todo.due_date}</span>}
                  <span style={{ ...styles.badge, backgroundColor: '#f3f4f6', color: '#6b7280' }}>🕒 Created: {new Date(todo.created_at).toLocaleDateString()}</span>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}

export default App;
