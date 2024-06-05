# app/routes.py

from app import app, db
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from app.models import User, Property
from werkzeug.security import generate_password_hash, check_password_hash


from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import app, db
from app.models import User, Property, Booking
from datetime import date

@app.route('/')
@app.route('/index')
def index():
    if current_user.is_authenticated:
        return render_template('home.html', username=current_user.username)
    else:
        return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, email=email, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('User registered successfully!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/profile/<int:user_id>', methods=['GET', 'POST'])
@login_required
def profile(user_id):
    user = User.query.get(user_id)
    if user == current_user:
        if request.method == 'POST':
            user.username = request.form['username']
            user.email = request.form['email']
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('profile', user_id=user.id))
        return render_template('profile.html', user=user)
    else:
        flash('You are not authorized to access this profile.', 'danger')
        return redirect(url_for('index'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

# Property CRUD Routes
@app.route('/properties', methods=['GET'])
def properties():
    location = request.args.get('location')
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')
    name = request.args.get('name')

    query = Property.query

    if location:
        query = query.filter(Property.address.contains(location))
    if min_price:
        query = query.filter(Property.price >= float(min_price))
    if max_price:
        query = query.filter(Property.price <= float(max_price))
    if name:
        query = query.filter(Property.name.contains(name))

    properties = query.all()

    return render_template('properties.html', properties=properties)

@app.route('/property/new', methods=['GET', 'POST'])
@login_required
def new_property():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        image_url = request.form['image_url']
        address = request.form['address']
        amenities = request.form.getlist('amenities')
        price = request.form['price']
        availability_status = request.form.get('availability_status') == 'on'

        # Check if image_url is provided
        if not image_url:
            flash('Please provide an image URL for the property.', 'danger')
            return redirect(url_for('new_property'))

        new_property = Property(
            name=name,
            description=description,
            image_url=image_url,
            address=address,
            amenities=amenities,
            price=price,
            availability_status=availability_status,
            owner_id=current_user.id
        )

        db.session.add(new_property)
        db.session.commit()
        flash('Property created successfully!', 'success')
        return redirect(url_for('properties'))
    return render_template('new_property.html')


@app.route('/property/<int:id>')
def view_property(id):
    property = Property.query.get(id)
    return render_template('view_property.html', property=property)

@app.route('/property/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_property(id):
    property = Property.query.get(id)
    if property.owner_id != current_user.id:  # Change here
        flash('You are not authorized to edit this property.', 'danger')
        return redirect(url_for('properties'))

    if request.method == 'POST':
        property.name = request.form['name']
        property.description = request.form['description']
        property.image_url = request.form['image_url']
        property.address = request.form['address']
        property.amenities = request.form.getlist('amenities')
        property.price = request.form['price']
        property.availability_status = request.form.get('availability_status') == 'on'

        db.session.commit()
        flash('Property updated successfully!', 'success')
        return redirect(url_for('view_property', id=property.id))

    return render_template('edit_property.html', property=property)

@app.route('/property/<int:id>/delete', methods=['POST'])
@login_required
def delete_property(id):
    property = Property.query.get(id)
    if property.owner_id != current_user.id:
        flash('You are not authorized to delete this property.', 'danger')
        return redirect(url_for('properties'))

    db.session.delete(property)
    db.session.commit()
    flash('Property deleted successfully!', 'success')
    return redirect(url_for('properties'))

@app.route('/profile/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_profile(user_id):
    user = User.query.get(user_id)
    if user == current_user:
        db.session.delete(user)
        db.session.commit()
        flash('Profile deleted successfully!', 'success')
        logout_user()
        return redirect(url_for('index'))
    else:
        flash('You are not authorized to delete this profile.', 'danger')
        return redirect(url_for('index'))

# New Booking Routes
@app.route('/property/<int:id>/book', methods=['GET', 'POST'])
@login_required
def book_property(id):
    property = Property.query.get_or_404(id)
    if request.method == 'POST':
        booking_date = request.form['booking_date']
        booking = Booking(user_id=current_user.id, property_id=property.id, booking_date=booking_date)
        db.session.add(booking)
        db.session.commit()
        flash('Property booked successfully!', 'success')
        return redirect(url_for('profile', user_id=current_user.id))
    return render_template('new_booking.html', property=property)

@app.route('/profile/<int:user_id>/bookings')
@login_required
def user_bookings(user_id):
    user = User.query.get_or_404(user_id)
    if user != current_user:
        flash('You are not authorized to view these bookings.', 'danger')
        return redirect(url_for('index'))
    bookings = Booking.query.filter_by(user_id=user_id).all()
    return render_template('user_bookings.html', bookings=bookings)
from flask import render_template, request, redirect, url_for
from app import app, db
from app.models import Property, Review
from app.forms import ReviewForm
from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from app import app, db
from app.models import Property, Review
from app.forms import ReviewForm

@app.route('/property/<int:property_id>/reviews', methods=['GET', 'POST'])
@login_required
def property_reviews(property_id):
    property = Property.query.get_or_404(property_id)
    form = ReviewForm()

    if form.validate_on_submit() and property.owner_id != current_user.id:
        new_review = Review(
            property_id=property_id,
            user_id=current_user.id,  # Assuming you're using Flask-Login for user authentication
            rating=form.rating.data,
            comment=form.comment.data
        )
        db.session.add(new_review)
        db.session.commit()
        flash('Review submitted successfully!', 'success')
        return redirect(url_for('property_reviews', property_id=property_id))

    reviews = Review.query.filter_by(property_id=property_id).all()
    return render_template('property_reviews.html', property=property, reviews=reviews, form=form)


@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    properties = Property.query.filter(Property.name.ilike(f'%{query}%')).all()
    return render_template('search_results.html', query=query, properties=properties)


