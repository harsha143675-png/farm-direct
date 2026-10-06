from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import check_password_hash
import database as db
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Initialize database schema and pre-seed data
db.init_db()

@app.context_processor
def inject_user():
    user = None
    if 'user_id' in session:
        user = db.get_user_by_id(session['user_id'])
    return dict(current_user=user)

# ----------------- HOME & PUBLIC PAGES -----------------

@app.route('/')
def index():
    stats = db.get_stats()
    recent_crops = db.get_all_crops()[:6]
    recent_demands = db.get_all_demands()[:4]
    return render_template('index.html', stats=stats, recent_crops=recent_crops, recent_demands=recent_demands)

@app.route('/crops')
def marketplace():
    query = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip()
    location = request.args.get('location', '').strip()
    crops = db.get_all_crops(search_query=query, category=category, location_query=location)
    return render_template('marketplace.html', crops=crops, search_query=query, category=category, location=location)

@app.route('/crop/<int:crop_id>')
def crop_detail(crop_id):
    crop = db.get_crop_by_id(crop_id)
    if not crop:
        flash("Crop listing not found.", "error")
        return redirect(url_for('marketplace'))
    
    # Calculate savings compared to market price
    savings_per_unit = 0
    savings_percentage = 0
    if crop['estimated_market_price'] and crop['estimated_market_price'] > crop['price']:
        savings_per_unit = round(crop['estimated_market_price'] - crop['price'], 2)
        savings_percentage = round((savings_per_unit / crop['estimated_market_price']) * 100)

    return render_template('crop_detail.html', crop=crop, savings=savings_per_unit, savings_pct=savings_percentage)

# ----------------- FARMER AUTH & DASHBOARD -----------------

@app.route('/farmer/login', methods=['GET', 'POST'])
def farmer_login():
    if request.method == 'POST':
        action = request.form.get('action') # 'login' or 'register'

        if action == 'register':
            name = request.form.get('name', '').strip()
            phone = request.form.get('phone', '').strip()
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            state = request.form.get('state', '').strip()
            district = request.form.get('district', '').strip()
            city_village = request.form.get('city_village', '').strip()
            address = request.form.get('address', '').strip()

            if not (name and phone and email and password and city_village):
                flash("Please fill in all mandatory fields.", "error")
                return render_template('farmer_login.html', active_tab='register')

            existing = db.get_user_by_email(email)
            if existing:
                flash("Email already registered. Please sign in.", "error")
                return render_template('farmer_login.html', active_tab='login')

            user_id = db.create_user(
                role='farmer',
                name=name,
                phone=phone,
                email=email,
                password=password,
                state=state,
                district=district,
                city_village=city_village,
                address=address
            )
            session['user_id'] = user_id
            session['role'] = 'farmer'
            session['user_name'] = name
            flash(f"Welcome {name}! Your farmer account has been created successfully.", "success")
            return redirect(url_for('farmer_dashboard'))

        else: # login
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')

            user = db.get_user_by_email(email)
            if user and user['role'] == 'farmer' and check_password_hash(user['password_hash'], password):
                session['user_id'] = user['id']
                session['role'] = user['role']
                session['user_name'] = user['name']
                flash(f"Welcome back, {user['name']}!", "success")
                return redirect(url_for('farmer_dashboard'))
            else:
                flash("Invalid farmer credentials or account does not exist.", "error")
                return render_template('farmer_login.html', active_tab='login')

    return render_template('farmer_login.html', active_tab='login')

@app.route('/farmer/dashboard')
def farmer_dashboard():
    if 'user_id' not in session or session.get('role') != 'farmer':
        flash("Please log in as a farmer to access your dashboard.", "error")
        return redirect(url_for('farmer_login'))

    farmer_id = session['user_id']
    farmer = db.get_user_by_id(farmer_id)
    my_crops = db.get_farmer_crops(farmer_id)
    inquiries = db.get_farmer_inquiries(farmer_id)
    consumer_demands = db.get_all_demands()

    return render_template('farmer_dashboard.html', farmer=farmer, crops=my_crops, inquiries=inquiries, demands=consumer_demands)

@app.route('/farmer/crop/add', methods=['POST'])
def add_crop_post():
    if 'user_id' not in session or session.get('role') != 'farmer':
        flash("Unauthorized", "error")
        return redirect(url_for('farmer_login'))

    farmer_id = session['user_id']
    farmer = db.get_user_by_id(farmer_id)

    crop_name = request.form.get('crop_name', '').strip()
    category = request.form.get('category', 'Vegetables')
    price = float(request.form.get('price', 0))
    unit = request.form.get('unit', 'kg')
    quantity = float(request.form.get('quantity', 0))
    harvest_date = request.form.get('harvest_date', '')
    description = request.form.get('description', '').strip()
    market_price = float(request.form.get('estimated_market_price') or (price * 1.4))
    
    # Simple emoji icon mapping based on crop name
    crop_lower = crop_name.lower()
    emoji = "🌾"
    if "tomato" in crop_lower: emoji = "🍅"
    elif "potato" in crop_lower: emoji = "🥔"
    elif "onion" in crop_lower: emoji = "🧅"
    elif "chilli" in crop_lower or "chili" in crop_lower: emoji = "🌶️"
    elif "banana" in crop_lower: emoji = "🍌"
    elif "mango" in crop_lower: emoji = "🥭"
    elif "grape" in crop_lower: emoji = "🍇"
    elif "apple" in crop_lower: emoji = "🍎"
    elif "rice" in crop_lower: emoji = "🌾"
    elif "wheat" in crop_lower: emoji = "🍞"
    elif "corn" in crop_lower or "maize" in crop_lower: emoji = "🌽"
    elif "carrot" in crop_lower: emoji = "🥕"
    elif "coconut" in crop_lower: emoji = "🥥"
    elif "honey" in crop_lower: emoji = "🍯"
    elif category == "Fruits": emoji = "🍎"
    elif category == "Vegetables": emoji = "🥬"

    location = f"{farmer['city_village']}, {farmer['district']} ({farmer['state']})" if farmer['district'] else farmer['city_village']

    db.add_crop(
        farmer_id=farmer_id,
        crop_name=crop_name,
        category=category,
        price=price,
        unit=unit,
        quantity=quantity,
        harvest_date=harvest_date,
        description=description,
        location=location,
        market_price=market_price,
        emoji=emoji
    )

    flash(f"Crop '{crop_name}' has been listed directly for consumers!", "success")
    return redirect(url_for('farmer_dashboard'))

@app.route('/farmer/crop/delete/<int:crop_id>', methods=['POST'])
def delete_crop_route(crop_id):
    if 'user_id' not in session or session.get('role') != 'farmer':
        return redirect(url_for('farmer_login'))
    db.delete_crop(crop_id, session['user_id'])
    flash("Crop listing removed.", "success")
    return redirect(url_for('farmer_dashboard'))

@app.route('/farmer/crop/toggle/<int:crop_id>', methods=['POST'])
def toggle_crop_status(crop_id):
    if 'user_id' not in session or session.get('role') != 'farmer':
        return redirect(url_for('farmer_login'))
    new_status = request.form.get('status', 'available')
    db.update_crop_status(crop_id, session['user_id'], new_status)
    flash("Crop status updated.", "success")
    return redirect(url_for('farmer_dashboard'))

# ----------------- CONSUMER AUTH & DASHBOARD -----------------

@app.route('/consumer/login', methods=['GET', 'POST'])
def consumer_login():
    if request.method == 'POST':
        action = request.form.get('action') # 'login' or 'register'

        if action == 'register':
            name = request.form.get('name', '').strip()
            phone = request.form.get('phone', '').strip()
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            state = request.form.get('state', '').strip()
            district = request.form.get('district', '').strip()
            city_village = request.form.get('city_village', '').strip()
            address = request.form.get('address', '').strip()

            if not (name and phone and email and password and city_village):
                flash("Please fill in all mandatory fields.", "error")
                return render_template('consumer_login.html', active_tab='register')

            existing = db.get_user_by_email(email)
            if existing:
                flash("Email already registered. Please sign in.", "error")
                return render_template('consumer_login.html', active_tab='login')

            user_id = db.create_user(
                role='consumer',
                name=name,
                phone=phone,
                email=email,
                password=password,
                state=state,
                district=district,
                city_village=city_village,
                address=address
            )
            session['user_id'] = user_id
            session['role'] = 'consumer'
            session['user_name'] = name
            flash(f"Welcome {name}! Your consumer account has been created.", "success")
            return redirect(url_for('consumer_dashboard'))

        else: # login
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')

            user = db.get_user_by_email(email)
            if user and user['role'] == 'consumer' and check_password_hash(user['password_hash'], password):
                session['user_id'] = user['id']
                session['role'] = user['role']
                session['user_name'] = user['name']
                flash(f"Welcome back, {user['name']}!", "success")
                return redirect(url_for('consumer_dashboard'))
            else:
                flash("Invalid consumer credentials or account does not exist.", "error")
                return render_template('consumer_login.html', active_tab='login')

    return render_template('consumer_login.html', active_tab='login')

@app.route('/consumer/dashboard')
def consumer_dashboard():
    if 'user_id' not in session or session.get('role') != 'consumer':
        flash("Please log in as a consumer to access your dashboard.", "error")
        return redirect(url_for('consumer_login'))

    consumer_id = session['user_id']
    consumer = db.get_user_by_id(consumer_id)
    my_demands = db.get_consumer_demands(consumer_id)
    my_inquiries = db.get_consumer_inquiries(consumer_id)
    
    # Pre-fetch crops matching consumer's district/city if possible, or all available
    local_crops = db.get_all_crops(location_query=consumer['district'] or consumer['city_village'])
    all_crops = db.get_all_crops()

    return render_template('consumer_dashboard.html', 
                           consumer=consumer, 
                           my_demands=my_demands, 
                           my_inquiries=my_inquiries,
                           local_crops=local_crops,
                           all_crops=all_crops)

@app.route('/consumer/demand/add', methods=['POST'])
def add_demand_post():
    if 'user_id' not in session or session.get('role') != 'consumer':
        flash("Please log in as a consumer.", "error")
        return redirect(url_for('consumer_login'))

    consumer_id = session['user_id']
    consumer = db.get_user_by_id(consumer_id)

    crop_name = request.form.get('crop_name', '').strip()
    category = request.form.get('category', 'Vegetables')
    target_price = float(request.form.get('target_price') or 0)
    quantity = float(request.form.get('quantity', 1))
    unit = request.form.get('unit', 'kg')
    location = request.form.get('location', '').strip() or f"{consumer['city_village']}, {consumer['district'] or consumer['state']}"
    notes = request.form.get('notes', '').strip()

    db.add_demand(consumer_id, crop_name, category, target_price, quantity, unit, location, notes)
    flash(f"Your requirement for '{crop_name}' has been posted! Farmers can now reach out directly.", "success")
    return redirect(url_for('consumer_dashboard'))

# ----------------- DIRECT CONNECT & INQUIRIES -----------------

@app.route('/crop/<int:crop_id>/inquire', methods=['POST'])
def submit_inquiry(crop_id):
    crop = db.get_crop_by_id(crop_id)
    if not crop:
        flash("Crop not found.", "error")
        return redirect(url_for('marketplace'))

    # Allow logged in consumer or capture direct details
    consumer_id = session.get('user_id')
    if not consumer_id or session.get('role') != 'consumer':
        flash("Please log in as a consumer to send a direct inquiry to the farmer.", "error")
        return redirect(url_for('consumer_login'))

    message = request.form.get('message', '').strip()
    contact_phone = request.form.get('contact_phone', '').strip()
    quantity_needed = float(request.form.get('quantity_needed', 1))

    db.add_inquiry(
        crop_id=crop_id,
        consumer_id=consumer_id,
        farmer_id=crop['farmer_id'],
        message=message,
        contact_phone=contact_phone,
        quantity_needed=quantity_needed
    )

    flash("Direct inquiry sent to farmer! The farmer has received your contact details.", "success")
    return redirect(url_for('crop_detail', crop_id=crop_id))

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been signed out successfully.", "info")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
