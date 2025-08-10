from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime
import secrets

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='fan')  # 'admin' or 'fan'
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    events = db.relationship('Event', backref='admin', lazy=True, cascade='all, delete-orphan')
    bookings = db.relationship('Booking', backref='fan', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set the user's password"""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        """Check if the provided password matches the hashed password"""
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Check if the user is an admin"""
        return self.role == 'admin'
    
    def is_fan(self):
        """Check if the user is a fan"""
        return self.role == 'fan'
    
    def to_dict(self):
        """Convert the user object to a dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<User {self.email}>'

class Event(db.Model):
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    event_date = db.Column(db.Date, nullable=False, index=True)
    unique_url = db.Column(db.String(255), unique=True, nullable=False, index=True)
    is_published = db.Column(db.Boolean, default=False, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    time_slots = db.relationship('TimeSlot', backref='event', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, **kwargs):
        super(Event, self).__init__(**kwargs)
        # Generate a unique URL if not provided
        if not self.unique_url:
            self.unique_url = self.generate_unique_url()
    
    def generate_unique_url(self):
        """Generate a unique URL for the event"""
        return secrets.token_urlsafe(16)
    
    def to_dict(self):
        """Convert the event object to a dictionary"""
        return {
            'id': self.id,
            'admin_id': self.admin_id,
            'title': self.title,
            'description': self.description,
            'event_date': self.event_date.isoformat() if self.event_date else None,
            'unique_url': self.unique_url,
            'is_published': self.is_published,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def to_public_dict(self):
        """Convert the event object to a dictionary for public view"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'event_date': self.event_date.isoformat() if self.event_date else None,
            'unique_url': self.unique_url
        }
    
    def __repr__(self):
        return f'<Event {self.title}>'

class TimeSlot(db.Model):
    __tablename__ = 'time_slots'
    
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'), nullable=False, index=True)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    is_booked = db.Column(db.Boolean, default=False, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    booking = db.relationship('Booking', backref='time_slot', uselist=False, cascade='all, delete-orphan')
    
    # Constraints
    __table_args__ = (
        db.CheckConstraint('start_time < end_time', name='check_start_before_end'),
        db.UniqueConstraint('event_id', 'start_time', 'end_time', name='unique_event_time_slot'),
    )
    
    def to_dict(self):
        """Convert the time slot object to a dictionary"""
        return {
            'id': self.id,
            'event_id': self.event_id,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'is_booked': self.is_booked,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def to_public_dict(self):
        """Convert the time slot object to a dictionary for public view"""
        return {
            'id': self.id,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None
        }
    
    def __repr__(self):
        return f'<TimeSlot {self.start_time} - {self.end_time}>'

class Booking(db.Model):
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    time_slot_id = db.Column(db.Integer, db.ForeignKey('time_slots.id', ondelete='CASCADE'), unique=True, nullable=False, index=True)
    fan_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    fan_name = db.Column(db.String(255), nullable=False)
    fan_email = db.Column(db.String(255), nullable=False)
    fan_phone = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Constraints
    __table_args__ = (
        db.UniqueConstraint('time_slot_id', name='unique_time_slot_booking'),
    )
    
    def to_dict(self):
        """Convert the booking object to a dictionary"""
        return {
            'id': self.id,
            'time_slot_id': self.time_slot_id,
            'fan_id': self.fan_id,
            'fan_name': self.fan_name,
            'fan_email': self.fan_email,
            'fan_phone': self.fan_phone,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Booking {self.id}>'