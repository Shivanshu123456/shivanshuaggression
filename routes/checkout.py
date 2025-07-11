from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import os
import csv
from werkzeug.utils import secure_filename
from datetime import datetime

checkout_bp = Blueprint('checkout', __name__)
UPLOAD_FOLDER = 'static/uploads'
CSV_LOG = 'data/checkout_logs.csv'

# Ensure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.dirname(CSV_LOG), exist_ok=True)

@checkout_bp.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'user_name' not in session:
        return redirect(url_for('login'))

    user_name = session['user_name']
    user_role = session.get('user_role', 'user')

    if request.method == 'POST':
        tool_id = request.form.get('tool_id')
        material_name = request.form.get('material_name')
        issued_to = request.form.get('issued_to')
        issued_by = request.form.get('issued_by')
        quantity = request.form.get('quantity')
        issue_date = request.form.get('issue_date')
        return_date = request.form.get('return_date')
        file = request.files.get('file')

        if not (tool_id and material_name and issued_to and issued_by and quantity and issue_date):
            flash("All required fields must be filled!", "danger")
            return redirect(url_for('checkout.checkout'))

        file_name = ""
        if file and file.filename:
            file_name = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, file_name))

        save_checkout_to_csv({
            "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "tool_id": tool_id,
            "material_name": material_name,
            "issued_to": issued_to,
            "issued_by": issued_by,
            "quantity": quantity,
            "issue_date": issue_date,
            "return_date": return_date,
            "file_name": file_name
        })

        flash("Checkout submitted successfully!", "success")
        return redirect(url_for('checkout.checkout'))

    logs = []
    if user_role == 'admin':
        logs = load_checkout_logs()

    return render_template('checkout.html',
                           user_name=user_name,
                           user_role=user_role,
                           logs=logs)

def save_checkout_to_csv(entry):
    file_exists = os.path.isfile(CSV_LOG)
    with open(CSV_LOG, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=entry.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(entry)

def load_checkout_logs():
    if not os.path.isfile(CSV_LOG):
        return []

    with open(CSV_LOG, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

