from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import os
from datetime import datetime
import uuid
import secrets

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def init_db():
    """Initialize the database with all required tables"""
    conn = sqlite3.connect('skillswap.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            location TEXT,
            profile_photo TEXT,
            is_public INTEGER DEFAULT 1,
            availability TEXT,
            is_admin INTEGER DEFAULT 0,
            is_banned INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Skills offered table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS skills_offered (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            skill_name TEXT NOT NULL,
            description TEXT,
            is_approved INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Skills wanted table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS skills_wanted (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            skill_name TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Swap requests table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS swap_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            requester_id INTEGER,
            provider_id INTEGER,
            offered_skill_id INTEGER,
            wanted_skill TEXT,
            message TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (requester_id) REFERENCES users (id),
            FOREIGN KEY (provider_id) REFERENCES users (id),
            FOREIGN KEY (offered_skill_id) REFERENCES skills_offered (id)
        )
    ''')
    
    # Ratings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            swap_request_id INTEGER,
            rater_id INTEGER,
            rated_id INTEGER,
            rating INTEGER CHECK (rating >= 1 AND rating <= 5),
            feedback TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (swap_request_id) REFERENCES swap_requests (id),
            FOREIGN KEY (rater_id) REFERENCES users (id),
            FOREIGN KEY (rated_id) REFERENCES users (id)
        )
    ''')
    
    # Platform messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS platform_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_id INTEGER,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (admin_id) REFERENCES users (id)
        )
    ''')
    
    # Rooms table for group messaging
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            creator_id INTEGER,
            is_public INTEGER DEFAULT 1,
            room_code TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (creator_id) REFERENCES users (id)
        )
    ''')
    
    # Room members table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS room_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_id INTEGER,
            user_id INTEGER,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (room_id) REFERENCES rooms (id),
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE(room_id, user_id)
        )
    ''')
    
    # Room messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS room_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_id INTEGER,
            user_id INTEGER,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (room_id) REFERENCES rooms (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create default admin user if not exists
    cursor.execute('SELECT * FROM users WHERE username = ?', ('admin',))
    if not cursor.fetchone():
        admin_password = generate_password_hash('admin123')
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, name, is_admin)
            VALUES (?, ?, ?, ?, ?)
        ''', ('admin', 'admin@skillswap.com', admin_password, 'Administrator', 1))
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect('skillswap.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    """Home page"""
    conn = get_db_connection()
    
    # Get recent platform messages
    messages = conn.execute('''
        SELECT pm.*, u.name as admin_name
        FROM platform_messages pm
        JOIN users u ON pm.admin_id = u.id
        ORDER BY pm.created_at DESC
        LIMIT 3
    ''').fetchall()
    
    # Get some featured skills
    featured_skills = conn.execute('''
        SELECT so.skill_name, u.name, u.location
        FROM skills_offered so
        JOIN users u ON so.user_id = u.id
        WHERE u.is_public = 1 AND u.is_banned = 0 AND so.is_approved = 1
        ORDER BY RANDOM()
        LIMIT 6
    ''').fetchall()
    
    conn.close()
    return render_template('index.html', messages=messages, featured_skills=featured_skills)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']
        location = request.form.get('location', '')
        
        conn = get_db_connection()
        
        # Check if user already exists
        if conn.execute('SELECT id FROM users WHERE username = ? OR email = ?', (username, email)).fetchone():
            flash('Username or email already exists!')
            conn.close()
            return render_template('register.html')
        
        # Create new user
        password_hash = generate_password_hash(password)
        conn.execute('''
            INSERT INTO users (username, email, password_hash, name, location)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, email, password_hash, name, location))
        
        conn.commit()
        conn.close()
        
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            if user['is_banned']:
                flash('Your account has been banned. Please contact admin.')
                return render_template('login.html')
            
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['is_admin'] = user['is_admin']
            
            if user['is_admin']:
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    """User dashboard"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Check if user is admin - redirect to admin dashboard
    conn = get_db_connection()
    user = conn.execute('SELECT is_admin FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    
    if user and user['is_admin']:
        conn.close()
        return redirect(url_for('admin_dashboard'))
    
    user_id = session['user_id']
    
    # Get user's skills offered
    skills_offered = conn.execute('''
        SELECT * FROM skills_offered WHERE user_id = ? ORDER BY created_at DESC
    ''', (user_id,)).fetchall()
    
    # Get user's skills wanted
    skills_wanted = conn.execute('''
        SELECT * FROM skills_wanted WHERE user_id = ? ORDER BY created_at DESC
    ''', (user_id,)).fetchall()
    
    # Get pending swap requests (received)
    pending_requests = conn.execute('''
        SELECT sr.*, u.name as requester_name, so.skill_name as offered_skill
        FROM swap_requests sr
        JOIN users u ON sr.requester_id = u.id
        JOIN skills_offered so ON sr.offered_skill_id = so.id
        WHERE sr.provider_id = ? AND sr.status = 'pending'
        ORDER BY sr.created_at DESC
    ''', (user_id,)).fetchall()
    
    # Get sent swap requests
    sent_requests = conn.execute('''
        SELECT sr.*, u.name as provider_name, so.skill_name as offered_skill
        FROM swap_requests sr
        JOIN users u ON sr.provider_id = u.id
        JOIN skills_offered so ON sr.offered_skill_id = so.id
        WHERE sr.requester_id = ?
        ORDER BY sr.created_at DESC
    ''', (user_id,)).fetchall()
    
    # Get user's rooms
    user_rooms = conn.execute('''
        SELECT r.*, rm.joined_at, u.name as creator_name,
               (SELECT COUNT(*) FROM room_members WHERE room_id = r.id) as member_count
        FROM rooms r
        JOIN room_members rm ON r.id = rm.room_id
        JOIN users u ON r.creator_id = u.id
        WHERE rm.user_id = ?
        ORDER BY rm.joined_at DESC
    ''', (user_id,)).fetchall()
    
    conn.close()
    
    return render_template('dashboard.html', 
                         skills_offered=skills_offered,
                         skills_wanted=skills_wanted,
                         pending_requests=pending_requests,
                         sent_requests=sent_requests,
                         user_rooms=user_rooms)

@app.route('/profile')
def profile():
    """User profile"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    user_id = session['user_id']
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()

    # Swaps completed (as requester or provider)
    swaps_completed = conn.execute('''
        SELECT COUNT(*) as count FROM swap_requests
        WHERE (requester_id = ? OR provider_id = ?) AND status = 'accepted'
    ''', (user_id, user_id)).fetchone()['count']

    # Most requested skills (skills offered by user, most requested by others)
    most_requested_skills = conn.execute('''
        SELECT so.skill_name, COUNT(sr.id) as request_count
        FROM skills_offered so
        LEFT JOIN swap_requests sr ON sr.offered_skill_id = so.id
        WHERE so.user_id = ?
        GROUP BY so.skill_name
        ORDER BY request_count DESC
        LIMIT 3
    ''', (user_id,)).fetchall()

    # Average feedback score (ratings received)
    avg_feedback = conn.execute('''
        SELECT AVG(rating) as avg FROM ratings WHERE rated_id = ?
    ''', (user_id,)).fetchone()['avg']

    # Busiest day/time (hour with most swaps completed)
    busiest = conn.execute('''
        SELECT strftime('%w', updated_at) as day, strftime('%H', updated_at) as hour, COUNT(*) as cnt
        FROM swap_requests
        WHERE (requester_id = ? OR provider_id = ?) AND status = 'accepted'
        GROUP BY day, hour
        ORDER BY cnt DESC
        LIMIT 1
    ''', (user_id, user_id)).fetchone()
    busiest_day = None
    busiest_hour = None
    if busiest:
        days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        busiest_day = days[int(busiest['day'])]
        busiest_hour = f"{int(busiest['hour']):02d}:00"

    conn.close()
    
    return render_template('profile.html', user=user,
        swaps_completed=swaps_completed,
        most_requested_skills=most_requested_skills,
        avg_feedback=avg_feedback,
        busiest_day=busiest_day,
        busiest_hour=busiest_hour
    )

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    """Edit user profile"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    user_id = session['user_id']
    
    if request.method == 'POST':
        name = request.form['name']
        location = request.form.get('location', '')
        availability = request.form.get('availability', '')
        is_public = 1 if request.form.get('is_public') else 0
        
        # Handle profile photo upload
        profile_photo = None
        if 'profile_photo' in request.files:
            file = request.files['profile_photo']
            if file and file.filename:
                filename = secure_filename(f"{user_id}_{file.filename}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                profile_photo = filename
        
        # Update user profile
        if profile_photo:
            conn.execute('''
                UPDATE users SET name = ?, location = ?, availability = ?, 
                is_public = ?, profile_photo = ? WHERE id = ?
            ''', (name, location, availability, is_public, profile_photo, user_id))
        else:
            conn.execute('''
                UPDATE users SET name = ?, location = ?, availability = ?, 
                is_public = ? WHERE id = ?
            ''', (name, location, availability, is_public, user_id))
        
        conn.commit()
        conn.close()
        
        flash('Profile updated successfully!')
        return redirect(url_for('profile'))
    
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    
    return render_template('edit_profile.html', user=user)

@app.route('/add_skill_offered', methods=['POST'])
def add_skill_offered():
    """Add a skill offered"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    skill_name = request.form['skill_name']
    description = request.form.get('description', '')
    
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO skills_offered (user_id, skill_name, description)
        VALUES (?, ?, ?)
    ''', (session['user_id'], skill_name, description))
    conn.commit()
    conn.close()
    
    flash('Skill added successfully!')
    return redirect(url_for('dashboard'))

@app.route('/add_skill_wanted', methods=['POST'])
def add_skill_wanted():
    """Add a skill wanted"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    skill_name = request.form['skill_name']
    description = request.form.get('description', '')
    
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO skills_wanted (user_id, skill_name, description)
        VALUES (?, ?, ?)
    ''', (session['user_id'], skill_name, description))
    conn.commit()
    conn.close()
    
    flash('Skill wanted added successfully!')
    return redirect(url_for('dashboard'))

@app.route('/browse_skills')
def browse_skills():
    """Browse available skills"""
    search = request.args.get('search', '')
    
    conn = get_db_connection()
    
    if search:
        skills = conn.execute('''
            SELECT so.*, u.name, u.location, u.profile_photo
            FROM skills_offered so
            JOIN users u ON so.user_id = u.id
            WHERE u.is_public = 1 AND u.is_banned = 0 AND so.is_approved = 1
            AND (so.skill_name LIKE ? OR so.description LIKE ?)
            ORDER BY so.created_at DESC
        ''', (f'%{search}%', f'%{search}%')).fetchall()
    else:
        skills = conn.execute('''
            SELECT so.*, u.name, u.location, u.profile_photo
            FROM skills_offered so
            JOIN users u ON so.user_id = u.id
            WHERE u.is_public = 1 AND u.is_banned = 0 AND so.is_approved = 1
            ORDER BY so.created_at DESC
        ''').fetchall()
    
    conn.close()
    
    return render_template('browse_skills.html', skills=skills, search=search)

@app.route('/request_swap/<int:skill_id>')
def request_swap(skill_id):
    """Request a skill swap"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    skill = conn.execute('''
        SELECT so.*, u.name, u.location
        FROM skills_offered so
        JOIN users u ON so.user_id = u.id
        WHERE so.id = ?
    ''', (skill_id,)).fetchone()
    
    # Get user's skills wanted
    my_skills_wanted = conn.execute('''
        SELECT * FROM skills_wanted WHERE user_id = ?
    ''', (session['user_id'],)).fetchall()
    
    conn.close()
    
    return render_template('request_swap.html', skill=skill, my_skills_wanted=my_skills_wanted)

@app.route('/send_swap_request', methods=['POST'])
def send_swap_request():
    """Send a swap request"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    offered_skill_id = request.form['offered_skill_id']
    wanted_skill = request.form['wanted_skill']
    message = request.form.get('message', '')
    
    conn = get_db_connection()
    
    # Get provider ID from skill
    skill = conn.execute('SELECT user_id FROM skills_offered WHERE id = ?', (offered_skill_id,)).fetchone()
    
    if skill and skill['user_id'] != session['user_id']:
        conn.execute('''
            INSERT INTO swap_requests (requester_id, provider_id, offered_skill_id, wanted_skill, message)
            VALUES (?, ?, ?, ?, ?)
        ''', (session['user_id'], skill['user_id'], offered_skill_id, wanted_skill, message))
        conn.commit()
        flash('Swap request sent successfully!')
    else:
        flash('Cannot send swap request!')
    
    conn.close()
    return redirect(url_for('browse_skills'))

@app.route('/handle_swap_request/<int:request_id>/<action>')
def handle_swap_request(request_id, action):
    """Accept or reject a swap request"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if action not in ['accept', 'reject']:
        flash('Invalid action!')
        return redirect(url_for('dashboard'))
    
    conn = get_db_connection()
    
    # Verify the request belongs to current user
    swap_request = conn.execute('''
        SELECT * FROM swap_requests WHERE id = ? AND provider_id = ?
    ''', (request_id, session['user_id'])).fetchone()
    
    if swap_request:
        status = 'accepted' if action == 'accept' else 'rejected'
        conn.execute('''
            UPDATE swap_requests SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (status, request_id))
        conn.commit()
        flash(f'Swap request {status}!')
    else:
        flash('Request not found!')
    
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/delete_swap_request/<int:request_id>')
def delete_swap_request(request_id):
    """Delete a swap request (only if pending)"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    # Verify the request belongs to current user and is pending
    swap_request = conn.execute('''
        SELECT * FROM swap_requests WHERE id = ? AND requester_id = ? AND status = 'pending'
    ''', (request_id, session['user_id'])).fetchone()
    
    if swap_request:
        conn.execute('DELETE FROM swap_requests WHERE id = ?', (request_id,))
        conn.commit()
        flash('Swap request deleted!')
    else:
        flash('Cannot delete this request!')
    
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/rate_user/<int:swap_id>')
def rate_user(swap_id):
    """Rate a user after swap"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    # Get swap details
    swap = conn.execute('''
        SELECT sr.*, u1.name as requester_name, u2.name as provider_name
        FROM swap_requests sr
        JOIN users u1 ON sr.requester_id = u1.id
        JOIN users u2 ON sr.provider_id = u2.id
        WHERE sr.id = ? AND sr.status = 'accepted'
        AND (sr.requester_id = ? OR sr.provider_id = ?)
    ''', (swap_id, session['user_id'], session['user_id'])).fetchone()
    
    if not swap:
        flash('Swap not found or not authorized!')
        conn.close()
        return redirect(url_for('dashboard'))
    
    # Check if already rated
    existing_rating = conn.execute('''
        SELECT * FROM ratings WHERE swap_request_id = ? AND rater_id = ?
    ''', (swap_id, session['user_id'])).fetchone()
    
    conn.close()
    
    if existing_rating:
        flash('You have already rated this swap!')
        return redirect(url_for('dashboard'))
    
    return render_template('rate_user.html', swap=swap)

@app.route('/submit_rating', methods=['POST'])
def submit_rating():
    """Submit a rating"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    swap_id = request.form['swap_id']
    rating = request.form['rating']
    feedback = request.form.get('feedback', '')
    
    conn = get_db_connection()
    
    # Get swap details to determine who to rate
    swap = conn.execute('''
        SELECT * FROM swap_requests WHERE id = ? AND status = 'accepted'
        AND (requester_id = ? OR provider_id = ?)
    ''', (swap_id, session['user_id'], session['user_id'])).fetchone()
    
    if swap:
        # Determine who to rate (the other person in the swap)
        rated_id = swap['provider_id'] if swap['requester_id'] == session['user_id'] else swap['requester_id']
        
        conn.execute('''
            INSERT INTO ratings (swap_request_id, rater_id, rated_id, rating, feedback)
            VALUES (?, ?, ?, ?, ?)
        ''', (swap_id, session['user_id'], rated_id, rating, feedback))
        conn.commit()
        flash('Rating submitted successfully!')
    else:
        flash('Invalid swap request!')
    
    conn.close()
    return redirect(url_for('dashboard'))

# Admin routes
@app.route('/admin')
def admin_dashboard():
    """Admin dashboard"""
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Access denied!')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    # Get statistics
    stats = {
        'total_users': conn.execute('SELECT COUNT(*) as count FROM users WHERE is_admin = 0').fetchone()['count'],
        'total_skills': conn.execute('SELECT COUNT(*) as count FROM skills_offered').fetchone()['count'],
        'pending_swaps': conn.execute('SELECT COUNT(*) as count FROM swap_requests WHERE status = "pending"').fetchone()['count'],
        'completed_swaps': conn.execute('SELECT COUNT(*) as count FROM swap_requests WHERE status = "accepted"').fetchone()['count']
    }
    
    # Get unapproved skills
    unapproved_skills = conn.execute('''
        SELECT so.*, u.name, u.username
        FROM skills_offered so
        JOIN users u ON so.user_id = u.id
        WHERE so.is_approved = 0
        ORDER BY so.created_at DESC
    ''').fetchall()
    
    # Get recent swap requests
    recent_swaps = conn.execute('''
        SELECT sr.*, u1.name as requester_name, u2.name as provider_name, so.skill_name
        FROM swap_requests sr
        JOIN users u1 ON sr.requester_id = u1.id
        JOIN users u2 ON sr.provider_id = u2.id
        JOIN skills_offered so ON sr.offered_skill_id = so.id
        ORDER BY sr.created_at DESC
        LIMIT 10
    ''').fetchall()
    
    conn.close()
    
    return render_template('admin_dashboard.html', stats=stats, 
                         unapproved_skills=unapproved_skills, recent_swaps=recent_swaps)

@app.route('/admin/users')
def admin_users():
    """Admin user management"""
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Access denied!')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    users = conn.execute('''
        SELECT u.*, 
               (SELECT AVG(rating) FROM ratings WHERE rated_id = u.id) as avg_rating,
               (SELECT COUNT(*) FROM ratings WHERE rated_id = u.id) as rating_count
        FROM users u 
        WHERE u.is_admin = 0
        ORDER BY u.created_at DESC
    ''').fetchall()
    conn.close()
    
    return render_template('admin_users.html', users=users)

@app.route('/admin/ban_user/<int:user_id>')
def admin_ban_user(user_id):
    """Ban/unban a user"""
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Access denied!')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    
    if user and not user['is_admin']:
        new_status = 0 if user['is_banned'] else 1
        conn.execute('UPDATE users SET is_banned = ? WHERE id = ?', (new_status, user_id))
        conn.commit()
        action = 'banned' if new_status else 'unbanned'
        flash(f'User {action} successfully!')
    else:
        flash('Cannot ban this user!')
    
    conn.close()
    return redirect(url_for('admin_users'))

@app.route('/admin/approve_skill/<int:skill_id>')
def admin_approve_skill(skill_id):
    """Approve/reject a skill"""
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Access denied!')
        return redirect(url_for('login'))
    
    action = request.args.get('action', 'approve')
    
    conn = get_db_connection()
    
    if action == 'approve':
        conn.execute('UPDATE skills_offered SET is_approved = 1 WHERE id = ?', (skill_id,))
        flash('Skill approved!')
    elif action == 'reject':
        conn.execute('DELETE FROM skills_offered WHERE id = ?', (skill_id,))
        flash('Skill rejected and removed!')
    
    conn.commit()
    conn.close()
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/messages')
def admin_messages():
    """Admin platform messages"""
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Access denied!')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    messages = conn.execute('''
        SELECT pm.*, u.name
        FROM platform_messages pm
        JOIN users u ON pm.admin_id = u.id
        ORDER BY pm.created_at DESC
    ''').fetchall()
    conn.close()
    
    return render_template('admin_messages.html', messages=messages)

@app.route('/admin/send_message', methods=['POST'])
def admin_send_message():
    """Send platform-wide message"""
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Access denied!')
        return redirect(url_for('login'))
    
    title = request.form['title']
    message = request.form['message']
    
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO platform_messages (admin_id, title, message)
        VALUES (?, ?, ?)
    ''', (session['user_id'], title, message))
    conn.commit()
    conn.close()
    
    flash('Message sent successfully!')
    return redirect(url_for('admin_messages'))

@app.route('/admin/delete_message/<int:message_id>')
def admin_delete_message(message_id):
    """Delete platform message"""
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Access denied!')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    conn.execute('DELETE FROM platform_messages WHERE id = ?', (message_id,))
    conn.commit()
    conn.close()
    
    flash('Message deleted successfully!')
    return redirect(url_for('admin_messages'))

@app.route('/admin/reports')
def admin_reports():
    """Admin reports"""
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Access denied!')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    # User activity report
    user_activity = conn.execute('''
        SELECT u.name, u.username, u.created_at,
               (SELECT COUNT(*) FROM skills_offered WHERE user_id = u.id) as skills_offered,
               (SELECT COUNT(*) FROM skills_wanted WHERE user_id = u.id) as skills_wanted,
               (SELECT COUNT(*) FROM swap_requests WHERE requester_id = u.id OR provider_id = u.id) as total_swaps,
               (SELECT AVG(rating) FROM ratings WHERE rated_id = u.id) as avg_rating
        FROM users u
        WHERE u.is_admin = 0
        ORDER BY u.created_at DESC
    ''').fetchall()
    
    # Swap statistics
    swap_stats = conn.execute('''
        SELECT 
            COUNT(*) as total_requests,
            SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
            SUM(CASE WHEN status = 'accepted' THEN 1 ELSE 0 END) as accepted,
            SUM(CASE WHEN status = 'rejected' THEN 1 ELSE 0 END) as rejected
        FROM swap_requests
    ''').fetchone()
    
    # Top skills
    top_skills = conn.execute('''
        SELECT skill_name, COUNT(*) as count
        FROM skills_offered
        WHERE is_approved = 1
        GROUP BY skill_name
        ORDER BY count DESC
        LIMIT 10
    ''').fetchall()
    
    conn.close()
    
    return render_template('admin_reports.html', 
                         user_activity=user_activity,
                         swap_stats=swap_stats,
                         top_skills=top_skills)

# Room and messaging routes
@app.route('/rooms')
def rooms():
    """List all public rooms"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    # Get all public rooms
    public_rooms = conn.execute('''
        SELECT r.*, u.name as creator_name,
               (SELECT COUNT(*) FROM room_members WHERE room_id = r.id) as member_count,
               (SELECT COUNT(*) FROM room_members WHERE room_id = r.id AND user_id = ?) as is_member
        FROM rooms r
        JOIN users u ON r.creator_id = u.id
        WHERE r.is_public = 1
        ORDER BY r.created_at DESC
    ''', (session['user_id'],)).fetchall()
    
    conn.close()
    
    return render_template('rooms.html', public_rooms=public_rooms)

@app.route('/create_room', methods=['POST'])
def create_room():
    """Create a new room"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    name = request.form['name']
    description = request.form.get('description', '')
    is_public = 1 if request.form.get('is_public') else 0
    
    # Generate unique room code
    room_code = secrets.token_urlsafe(8).upper()
    
    conn = get_db_connection()
    
    # Ensure room code is unique
    while True:
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM rooms WHERE room_code = ?', (room_code,))
        if not cursor.fetchone():
            break
        room_code = secrets.token_urlsafe(8).upper()
    
    # Create room
    cursor.execute('''
        INSERT INTO rooms (name, description, creator_id, is_public, room_code)
        VALUES (?, ?, ?, ?, ?)
    ''', (name, description, session['user_id'], is_public, room_code))
    
    room_id = cursor.lastrowid
    
    # Add creator as member
    conn.execute('''
        INSERT INTO room_members (room_id, user_id)
        VALUES (?, ?)
    ''', (room_id, session['user_id']))
    
    conn.commit()
    conn.close()
    
    flash(f'Room created successfully! Room code: {room_code}')
    return redirect(url_for('room_detail', room_id=room_id))

@app.route('/room/<int:room_id>')
def room_detail(room_id):
    """Room detail and chat"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    # Get room details
    room = conn.execute('''
        SELECT r.*, u.name as creator_name,
               (SELECT COUNT(*) FROM room_members WHERE room_id = r.id) as member_count
        FROM rooms r
        JOIN users u ON r.creator_id = u.id
        WHERE r.id = ?
    ''', (room_id,)).fetchone()
    
    if not room:
        flash('Room not found!')
        conn.close()
        return redirect(url_for('rooms'))
    
    # Check if user is member
    is_member = conn.execute('''
        SELECT id FROM room_members WHERE room_id = ? AND user_id = ?
    ''', (room_id, session['user_id'])).fetchone()
    
    if not is_member and not room['is_public']:
        flash('Access denied to this private room!')
        conn.close()
        return redirect(url_for('rooms'))
    
    # Get room messages
    messages = conn.execute('''
        SELECT rm.*, u.name, u.profile_photo
        FROM room_messages rm
        JOIN users u ON rm.user_id = u.id
        WHERE rm.room_id = ?
        ORDER BY rm.created_at ASC
    ''', (room_id,)).fetchall()
    
    # Get room members
    members = conn.execute('''
        SELECT u.id, u.name, u.username, u.profile_photo, rm.joined_at,
               (SELECT AVG(rating) FROM ratings WHERE rated_id = u.id) as rating
        FROM room_members rm
        JOIN users u ON rm.user_id = u.id
        WHERE rm.room_id = ?
        ORDER BY rm.joined_at ASC
    ''', (room_id,)).fetchall()
    
    conn.close()
    
    return render_template('room_detail.html', room=room, messages=messages, 
                         members=members, is_member=is_member)

@app.route('/join_room/<int:room_id>')
def join_room(room_id):
    """Join a room"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    # Check if room exists and is public
    room = conn.execute('SELECT * FROM rooms WHERE id = ? AND is_public = 1', (room_id,)).fetchone()
    
    if not room:
        flash('Room not found or is private!')
        conn.close()
        return redirect(url_for('rooms'))
    
    # Check if already member
    existing = conn.execute('''
        SELECT id FROM room_members WHERE room_id = ? AND user_id = ?
    ''', (room_id, session['user_id'])).fetchone()
    
    if existing:
        flash('You are already a member of this room!')
    else:
        conn.execute('''
            INSERT INTO room_members (room_id, user_id)
            VALUES (?, ?)
        ''', (room_id, session['user_id']))
        conn.commit()
        flash('Successfully joined the room!')
    
    conn.close()
    return redirect(url_for('room_detail', room_id=room_id))

@app.route('/join_room_by_code', methods=['POST'])
def join_room_by_code():
    """Join a room using room code"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    room_code = request.form['room_code'].upper().strip()
    
    conn = get_db_connection()
    
    # Find room by code
    room = conn.execute('''
        SELECT r.*, u.username as creator_name
        FROM rooms r
        JOIN users u ON r.creator_id = u.id
        WHERE r.room_code = ?
    ''', (room_code,)).fetchone()
    
    if not room:
        flash('Invalid room code. Please check and try again.', 'error')
        return redirect(url_for('rooms'))
    
    # Check if user is already a member
    existing_member = conn.execute('''
        SELECT id FROM room_members 
        WHERE room_id = ? AND user_id = ?
    ''', (room['id'], session['user_id'])).fetchone()
    
    if existing_member:
        flash('You are already a member of this room!')
        return redirect(url_for('room_detail', room_id=room['id']))
    
    # Add user to room
    conn.execute('''
        INSERT INTO room_members (room_id, user_id)
        VALUES (?, ?)
    ''', (room['id'], session['user_id']))
    
    conn.commit()
    conn.close()
    
    flash(f'Successfully joined "{room["name"]}"!')
    return redirect(url_for('room_detail', room_id=room['id']))

@app.route('/invite_user_to_room', methods=['POST'])
def invite_user_to_room():
    """Invite a user to room (room creator only)"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    room_id = request.form['room_id']
    username = request.form['username'].strip()
    
    conn = get_db_connection()
    
    # Check if current user is room creator
    room = conn.execute('''
        SELECT creator_id FROM rooms WHERE id = ?
    ''', (room_id,)).fetchone()
    
    if not room or room['creator_id'] != session['user_id']:
        flash('Only room creators can invite users.', 'error')
        return redirect(url_for('room_detail', room_id=room_id))
    
    # Find user to invite
    user_to_invite = conn.execute('''
        SELECT id, username FROM users WHERE username = ? AND is_banned = 0
    ''', (username,)).fetchone()
    
    if not user_to_invite:
        flash('User not found or is banned.', 'error')
        return redirect(url_for('room_detail', room_id=room_id))
    
    # Check if user is already a member
    existing_member = conn.execute('''
        SELECT id FROM room_members 
        WHERE room_id = ? AND user_id = ?
    ''', (room_id, user_to_invite['id'])).fetchone()
    
    if existing_member:
        flash(f'{username} is already a member of this room.', 'info')
        return redirect(url_for('room_detail', room_id=room_id))
    
    # Add user to room
    conn.execute('''
        INSERT INTO room_members (room_id, user_id)
        VALUES (?, ?)
    ''', (room_id, user_to_invite['id']))
    
    conn.commit()
    conn.close()
    
    flash(f'{username} has been added to the room!')
    return redirect(url_for('room_detail', room_id=room_id))

@app.route('/send_message', methods=['POST'])
def send_message():
    """Send a message to a room"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    room_id = request.form['room_id']
    message = request.form['message']
    
    conn = get_db_connection()
    
    # Check if user is member
    is_member = conn.execute('''
        SELECT id FROM room_members WHERE room_id = ? AND user_id = ?
    ''', (room_id, session['user_id'])).fetchone()
    
    if is_member:
        conn.execute('''
            INSERT INTO room_messages (room_id, user_id, message)
            VALUES (?, ?, ?)
        ''', (room_id, session['user_id'], message))
        conn.commit()
    
    conn.close()
    return redirect(url_for('room_detail', room_id=room_id))

@app.route('/leave_room/<int:room_id>')
def leave_room(room_id):
    """Leave a room"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    # Check if room exists
    room = conn.execute('SELECT * FROM rooms WHERE id = ?', (room_id,)).fetchone()
    
    if not room:
        flash('Room not found!')
        conn.close()
        return redirect(url_for('rooms'))
    
    # Check if user is the creator
    if room['creator_id'] == session['user_id']:
        flash('Room creators cannot leave their own rooms!')
        conn.close()
        return redirect(url_for('room_detail', room_id=room_id))
    
    # Check if user is member
    is_member = conn.execute('''
        SELECT id FROM room_members WHERE room_id = ? AND user_id = ?
    ''', (room_id, session['user_id'])).fetchone()
    
    if not is_member:
        flash('You are not a member of this room!')
    else:
        # Remove user from room
        conn.execute('''
            DELETE FROM room_members WHERE room_id = ? AND user_id = ?
        ''', (room_id, session['user_id']))
        conn.commit()
        flash('Successfully left the room!')
    
    conn.close()
    return redirect(url_for('rooms'))

@app.route('/delete_room/<int:room_id>', methods=['POST'])
def delete_room(room_id):
    """Delete a room (creator only)"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    # Check if room exists and user is the creator
    room = conn.execute('''
        SELECT creator_id, name FROM rooms WHERE id = ?
    ''', (room_id,)).fetchone()
    
    if not room:
        flash('Room not found!')
        conn.close()
        return redirect(url_for('rooms'))
    
    if room['creator_id'] != session['user_id']:
        flash('Only room creators can delete their rooms!')
        conn.close()
        return redirect(url_for('room_detail', room_id=room_id))
    
    # Delete all related data in the correct order (due to foreign key constraints)
    # Delete room messages first
    conn.execute('DELETE FROM room_messages WHERE room_id = ?', (room_id,))
    
    # Delete room members
    conn.execute('DELETE FROM room_members WHERE room_id = ?', (room_id,))
    
    # Finally delete the room itself
    conn.execute('DELETE FROM rooms WHERE id = ?', (room_id,))
    
    conn.commit()
    conn.close()
    
    flash(f'Room "{room["name"]}" has been deleted successfully!')
    return redirect(url_for('rooms'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
