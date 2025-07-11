from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
from datetime import datetime
from functools import wraps
import os
import logging
import csv

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# ✅ Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['SESSION_PERMANENT'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # 30 mins

# ✅ Setup folders
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('submissions', exist_ok=True)
HEALTH_LOG_FILE = 'submissions/health_logs.csv'
MAINTENANCE_LOG_FILE = 'submissions/maintenance_logs.csv'
ENERGY_LOG_FILE = 'submissions/energy_logs.csv'
TOOL_LOG_FILE = 'submissions/tool_logs.csv'

# ✅ Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ Context Processor
@app.context_processor
def inject_globals():
    return {
        'now': datetime.utcnow(),
        'user_role': session.get('role', 'guest'),
        'user_name': session.get('username', 'Guest'),
        'current_route': request.endpoint
    }

# ✅ Decorators
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in session:
            flash('Login required', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('Admin access only', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated

# ✅ Routes
@app.route('/')
def home():
    return redirect(url_for('dashboard')) if 'username' in session else redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        staff_no = request.form.get('staff_no')
        if staff_no:
            session['username'] = staff_no.title() if staff_no.lower() != 'admin' else 'Admin'
            session['role'] = 'admin' if staff_no.lower() == 'admin' else 'staff'
            flash(f"Welcome {session['username']}!", 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid credentials', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    user = session.get('username')
    role = session.get('role')
    health_logs = []
    maintenance_logs = []
    energy_logs = []
    tool_logs = []

    if request.method == 'POST':
        form_type = request.form.get("form_type")
        now_str = datetime.now().strftime('%d-%m-%Y %H:%M')

        if form_type == "maintenance":
            note = request.form.get('maintenanceNotes')
            with open(MAINTENANCE_LOG_FILE, mode='a', newline='') as f:
                csv.writer(f).writerow([user, note, now_str])

        elif form_type == "health":
            status = request.form.get('status')
            note = request.form.get('note')
            with open(HEALTH_LOG_FILE, mode='a', newline='') as f:
                csv.writer(f).writerow([note, status, now_str])

        elif form_type == "energy":
            units = request.form.get('units')
            note = request.form.get('note')
            with open(ENERGY_LOG_FILE, mode='a', newline='') as f:
                csv.writer(f).writerow([user, units, note, now_str])

        elif form_type == "tool":
            tool_id = request.form.get('tool_id')
            note = request.form.get('note', '')
            with open(TOOL_LOG_FILE, mode='a', newline='') as f:
                csv.writer(f).writerow([user, tool_id, note, now_str])

        return redirect(url_for('dashboard'))

    if os.path.exists(MAINTENANCE_LOG_FILE):
        with open(MAINTENANCE_LOG_FILE, mode='r') as f:
            reader = csv.reader(f)
            maintenance_logs = [
                {'user': row[0], 'note': row[1], 'date': row[2]}
                for row in reader if role == 'admin' or row[0] == user
            ]

    if role == 'admin' and os.path.exists(HEALTH_LOG_FILE):
        with open(HEALTH_LOG_FILE, mode='r') as f:
            reader = csv.reader(f)
            health_logs = [{'note': row[0], 'status': row[1], 'date': row[2]} for row in reader]

    if os.path.exists(ENERGY_LOG_FILE):
        with open(ENERGY_LOG_FILE, mode='r') as f:
            reader = csv.reader(f)
            energy_logs = [
                {'user': row[0], 'units': row[1], 'note': row[2], 'date': row[3]}
                for row in reader if role == 'admin' or row[0] == user
            ]

    if os.path.exists(TOOL_LOG_FILE):
        with open(TOOL_LOG_FILE, mode='r') as f:
            reader = csv.reader(f)
            tool_logs = [
                {'user': row[0], 'tool_id': row[1], 'note': row[2], 'date': row[3]}
                for row in reader if role == 'admin' or row[0] == user
            ]

    return render_template(
        'dashboard.html',
        maintenance_logs=maintenance_logs,
        health_logs=health_logs,
        energy_logs=energy_logs,
        tool_logs=tool_logs
    )

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if request.method == 'POST':
        tool_id = request.form.get('tool_id')
        flash(f'Tool {tool_id} checked out successfully.', 'success')
    return render_template('checkout.html')

@app.route('/safety', methods=['GET', 'POST'])
@login_required
def safety():
    if request.method == 'POST':
        flash('Safety report submitted.', 'success')
    return render_template('safety.html')

@app.route('/reports')
@login_required
def reports():
    return render_template('reports.html')

@app.route('/upload', methods=['POST'])
@login_required
def upload():
    file = request.files.get('file')
    if not file or file.filename == '':
        flash('No file selected', 'danger')
        return redirect(request.url)
    path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(path)
    flash('File uploaded successfully.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/download/<filename>')
@login_required
def download_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)

@app.route('/api/status')
def api_status():
    return jsonify({"status": "ok", "user": session.get('username', 'Guest')})

@app.route('/health', methods=['GET', 'POST'])
@login_required
def health_page():
    if request.method == 'POST':
        feedback = request.form.get('feedback')
        print("Health Feedback Submitted:", feedback)
        flash("Health feedback submitted.", "success")
        return redirect(url_for('dashboard'))
    return render_template('health_form.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    logger.exception("Server Error: %s", e)
    return render_template('500.html'), 500
from flask import render_template
@app.route('/submit_tab_data', methods=['POST'])
def submit_tab_data():
    category = request.form.get('category')
    details = request.form.get('details')
    
    if category and details:
        filename = f"{category}_log.csv"
        filepath = os.path.join('logs', filename)
        os.makedirs('logs', exist_ok=True)
        with open(filepath, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([datetime.now().isoformat(), details])
        flash(f"{category.capitalize()} log submitted.", "success")
    else:
        flash("Invalid submission.", "danger")
    return redirect(url_for('dashboard'))





if __name__ == '__main__':
    app.run(debug=True, port=5000)
