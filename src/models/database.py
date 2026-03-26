from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import bcrypt
from sqlalchemy import Index, event
from sqlalchemy.ext.hybrid import hybrid_property

db = SQLAlchemy()

class User(db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    _password_hash = db.Column('password', db.String(128), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    todos = db.relationship('Todo', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    @hybrid_property
    def password(self):
        return self._password_hash
    
    @password.setter
    def password(self, plaintext):
        self._password_hash = bcrypt.hashpw(plaintext.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, plaintext):
        return bcrypt.checkpw(plaintext.encode('utf-8'), self._password_hash.encode('utf-8'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }

class Todo(db.Model):
    """Todo model with enhanced features"""
    __tablename__ = 'todos'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    priority = db.Column(db.String(20), default='medium')
    category = db.Column(db.String(100), default='General')
    due_date = db.Column(db.Date)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_todos_user_completed', 'user_id', 'completed'),
        Index('idx_todos_due_date', 'due_date'),
        Index('idx_todos_priority', 'priority'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'category': self.category,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'completed': self.completed,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

# Database event listeners
@event.listens_for(Todo, 'before_insert')
def todo_before_insert(mapper, connection, target):
    """Set default values before insert"""
    if not target.priority:
        target.priority = 'medium'
    if not target.category:
        target.category = 'General'

# Create indexes on database
def create_indexes():
    """Create additional indexes for performance"""
    with db.engine.connect() as conn:
        conn.execute('CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_todos_user_priority ON todos(user_id, priority) WHERE completed = false')
        conn.commit()
