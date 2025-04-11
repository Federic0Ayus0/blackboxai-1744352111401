from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from datetime import timedelta
from database import create_tables
from config import logger
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management and flash messages
app.permanent_session_lifetime = timedelta(minutes=60)  # Session expires after 60 minutes

# Initialize database
try:
    create_tables()
    logger.info("Database initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize database: {str(e)}")

# Login decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        try:
            conn = sqlite3.connect('invoice_system.db')
            cursor = conn.cursor()
            cursor.execute("SELECT id, password_hash FROM users WHERE email = ?", (email,))
            user = cursor.fetchone()
            
            if user and check_password_hash(user[1], password):
                session['user_id'] = user[0]
                flash('Logged in successfully!')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid email or password')
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            flash('An error occurred during login')
        finally:
            conn.close()
            
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    try:
        conn = sqlite3.connect('invoice_system.db')
        cursor = conn.cursor()
        
        # Get recent invoices
        cursor.execute("""
            SELECT invoice_number, customer, issue_date, total_amount 
            FROM invoices 
            WHERE user_id = ? 
            ORDER BY issue_date DESC LIMIT 5
        """, (session['user_id'],))
        recent_invoices = cursor.fetchall()
        
        # Get recent quotations
        cursor.execute("""
            SELECT quotation_number, customer, issue_date, total_amount 
            FROM quotations 
            WHERE user_id = ? 
            ORDER BY issue_date DESC LIMIT 5
        """, (session['user_id'],))
        recent_quotations = cursor.fetchall()
        
        return render_template('dashboard.html', 
                             invoices=recent_invoices, 
                             quotations=recent_quotations)
    except Exception as e:
        logger.error(f"Dashboard error: {str(e)}")
        flash('Error loading dashboard data')
        return redirect(url_for('index'))
    finally:
        conn.close()

@app.route('/invoices')
@login_required
def invoices():
    try:
        conn = sqlite3.connect('invoice_system.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT invoice_number, customer, issue_date, due_date, total_amount 
            FROM invoices 
            WHERE user_id = ?
            ORDER BY issue_date DESC
        """, (session['user_id'],))
        invoices = cursor.fetchall()
        return render_template('invoices.html', invoices=invoices)
    except Exception as e:
        logger.error(f"Invoices listing error: {str(e)}")
        flash('Error loading invoices')
        return redirect(url_for('dashboard'))
    finally:
        conn.close()

@app.route('/quotations')
@login_required
def quotations():
    try:
        conn = sqlite3.connect('invoice_system.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT quotation_number, customer, issue_date, expiry_date, total_amount 
            FROM quotations 
            WHERE user_id = ?
            ORDER BY issue_date DESC
        """, (session['user_id'],))
        quotations = cursor.fetchall()
        return render_template('quotations.html', quotations=quotations)
    except Exception as e:
        logger.error(f"Quotations listing error: {str(e)}")
        flash('Error loading quotations')
        return redirect(url_for('dashboard'))
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True, port=8000)
