# app/models.py
from app import db
from datetime import datetime
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(128))
    bio = db.Column(db.String(255))
    profile_picture = db.Column(db.String(255))

    # Define the relationship between User and Property
    properties = db.relationship('Property', back_populates='owner')
    bookings = db.relationship('Booking', back_populates='user')

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Property(db.Model):
    __tablename__ = 'property'

    id = db.Column(db.Integer, primary_key=True)  # Use 'id' instead of 'property_id'
    name = db.Column(db.String(100))
    description = db.Column(db.Text)
    price = db.Column(db.Float)
    image_url = db.Column(db.String(255))
    address = db.Column(db.String(255))
    amenities = db.Column(db.ARRAY(db.String))  # Assuming amenities is an array of strings
    availability_status = db.Column(db.Boolean)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # Define the relationship between Property and User
    owner = db.relationship('User', back_populates='properties')
    bookings = db.relationship('Booking', back_populates='property')

class Booking(db.Model):
    __tablename__ = 'booking'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    booking_date = db.Column(db.Date, nullable=False)

    # Relationships
    user = db.relationship('User', back_populates='bookings')
    property = db.relationship('Property', back_populates='bookings')

    def __repr__(self):
        return f'<Booking {self.id}>'

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=False)
    user = db.relationship('User', backref=db.backref('reviews', lazy=True))
    property = db.relationship('Property', backref=db.backref('reviews', lazy=True))