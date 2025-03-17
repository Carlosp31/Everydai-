from datetime import datetime, timezone
from database import db
from sqlalchemy.dialects.mysql import JSON

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    provider = db.Column(db.String(50), nullable=False)
    provider_id = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    profile_pic = db.Column(db.String(255))
    created_at = db.Column(db.TIMESTAMP, default=lambda: datetime.now(timezone.utc))

    inventories = db.relationship('Inventory', backref='user', lazy=True)
    wish_lists = db.relationship('WishList', backref='user', lazy=True)  # Corregido nombre de backref
    preferences = db.relationship('UserPreference', backref='user', lazy=True)

class Domain(db.Model):
    __tablename__ = 'domains'

    id = db.Column(db.Integer, primary_key=True)
    domain_name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)

    inventories = db.relationship('Inventory', backref='domain', lazy=True)
    wish_lists = db.relationship('WishList', backref='domain', lazy=True)  # Corregido nombre de backref

class Inventory(db.Model):
    __tablename__ = 'inventories'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    domain_id = db.Column(db.Integer, db.ForeignKey('domains.id'), nullable=False)
    items = db.Column(JSON)
    created_at = db.Column(db.TIMESTAMP, default=lambda: datetime.now(timezone.utc))

class WishList(db.Model):
    __tablename__ = 'wish_list'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    domain_id = db.Column(db.Integer, db.ForeignKey('domains.id'), nullable=False)
    wish_items = db.Column(JSON)  # Corregido nombre de columna
    created_at = db.Column(db.TIMESTAMP, default=lambda: datetime.now(timezone.utc))

class UserPreference(db.Model):
    __tablename__ = 'user_preferences'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    domain_id = db.Column(db.Integer, db.ForeignKey('domains.id'), nullable=False)
    preference = db.Column(JSON, nullable=False)
    extracted_at = db.Column(db.TIMESTAMP, default=lambda: datetime.now(timezone.utc))
