from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import datetime
import re
from datetime import timedelta
from database import create_tables
from config import logger
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os

class Invoice:
    def __init__(self, invoice_number, customer_id, items, total_amount, issue_date=None, due_date=None, user_id=None):
        self.invoice_number = invoice_number
        self.customer_id = customer_id
        self.items = items
        self.total_amount = total_amount
        self.issue_date = issue_date if issue_date else datetime.date.today().strftime('%Y-%m-%d')
        self.due_date = due_date
        self.user_id = user_id

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

@app.route('/invoices/new')
@login_required
def new_invoice():
    return render_template('new_invoice.html')

@app.route('/invoices/create', methods=['POST'])
@login_required
def create_invoice():
    try:
        # Get form data
        customer_name = request.form['customer_name']
        customer_email = request.form['customer_email']
        invoice_number = request.form['invoice_number']
        issue_date = request.form['issue_date']
        due_date = request.form['due_date']
        
        # Process items
        items = []
        total_amount = 0
        i = 0
        while f'items[{i}][name]' in request.form:
            item = {
                'name': request.form[f'items[{i}][name]'],
                'quantity': int(request.form[f'items[{i}][quantity]']),
                'price': float(request.form[f'items[{i}][price]'])
            }
            item_total = item['quantity'] * item['price']
            total_amount += item_total
            items.append(item)
            i += 1

        # Save to database
        conn = sqlite3.connect('invoice_system.db')
        cursor = conn.cursor()
        
        # Insert invoice
        cursor.execute("""
            INSERT INTO invoices (invoice_number, customer, issue_date, due_date, total_amount, user_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (invoice_number, customer_name, issue_date, due_date, total_amount, session['user_id']))
        
        # Insert invoice items
        for item in items:
            cursor.execute("""
                INSERT INTO invoice_items (invoice_number, item_name, quantity, price)
                VALUES (?, ?, ?, ?)
            """, (invoice_number, item['name'], item['quantity'], item['price']))
        
        conn.commit()
        
        flash('Invoice created successfully!')
        return redirect(url_for('invoices'))
    
    except Exception as e:
        logger.error(f"Error creating invoice: {str(e)}")
        flash('Error creating invoice')
        return redirect(url_for('new_invoice'))
    finally:
        conn.close()
