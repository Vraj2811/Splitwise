from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from datetime import datetime,timedelta
import calendar
import os
import random

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'default_secret_key_for_development')
DATABASE = './database.db'

# BASE_DIR = os.path.join('/home', 'site', 'wwwroot')  # Persistent path
# DATABASE = os.path.join(BASE_DIR, 'data.db')

# app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DATABASE}"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            unique_key TEXT UNIQUE NOT NULL
        )
    ''')

    # Create Groups table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            name TEXT NOT NULL,
            group_no TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(unique_key)
        )
    ''')

    # Create Expenses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            payed_by TEXT NOT NULL,
            payed_to TEXT,
            group_id TEXT,
            amount REAL NOT NULL,
            date TEXT NOT NULL,
            expense_id TEXT,
            description TEXT,
            FOREIGN KEY (group_id) REFERENCES groups(group_no)
        )
    ''')
    
    conn.commit()
    conn.close()


@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user_id'] = user['id']
            session['name'] = user['name']
            session['unique_key'] = user['unique_key']
            flash(f"Welcome, {user['name']}!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password.", "danger")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        unique_key = ''.join([str(random.randint(0, 9)) for _ in range(10)])
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (name, email, password, unique_key) VALUES (?, ?, ?, ?)',
                           (name, email, password, unique_key))
            conn.commit()
            conn.close()
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Email already exists.", "danger")
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch user's groups
    cursor.execute('SELECT group_no, name FROM groups WHERE user_id = ?', (session['unique_key'],))
    groups = []
    for group in cursor.fetchall():
        cursor.execute('SELECT COUNT(*) FROM groups WHERE group_no = ?', (group[0],))
        member_count = cursor.fetchone()[0]
        groups.append({'group_no': group[0], 'name': group[1], 'member_count': member_count})


    # Get the first and last date of the current month
    today = datetime.today()
    start_date = today.replace(day=1).strftime('%Y-%m-%d')  # First day of the month
    last_day = calendar.monthrange(today.year, today.month)[1]  # Get last day of the month
    end_date = today.replace(day=last_day).strftime('%Y-%m-%d')

    # Fetch total personal expenses for this month
    cursor.execute(
        'SELECT SUM(amount) FROM expenses WHERE payed_by = ? AND payed_to IS NULL AND date BETWEEN ? AND ?',
        (session['unique_key'], start_date, end_date)
    )
    total_expenses_month = round(cursor.fetchone()[0] or 0, 2)

    # Fetch last 5 personal expenses
    cursor.execute(
        'SELECT date, description, amount FROM expenses WHERE payed_by = ? AND payed_to IS NULL ORDER BY date DESC LIMIT 5',
        (session['unique_key'],)
    )
    recent_expenses = cursor.fetchall()  

    conn.close()

    return render_template('dashboard.html', groups=groups, 
                           recent_expenses=recent_expenses,
                           total_expenses_month=total_expenses_month)

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

@app.route('/create_group', methods=['POST'])
def create_group():
    if 'user_id' not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for('login'))

    group_name = request.form['group_name']
    member_ids = request.form['member_ids'].split(',')

    unique_grp = ''.join([str(random.randint(0, 9)) for _ in range(10)])
    
    # Validate member IDs
    conn = get_db_connection()
    cursor = conn.cursor()

    # Add group to the database
    cursor.execute('INSERT INTO groups (user_id, name, group_no) VALUES (?, ?,?)', (session['unique_key'], group_name, unique_grp))
    conn.commit()

    # Check if each member_id exists in the users table
    for member_id in member_ids:
        cursor.execute('SELECT * FROM users WHERE unique_key = ?', (member_id,))
        user = cursor.fetchone()
        if user:
            cursor.execute('INSERT INTO groups (user_id, name, group_no) VALUES (?, ?,?)', (member_id, group_name, unique_grp))
    
    conn.commit()
    conn.close()

    flash(f"Group '{group_name}' created successfully!", "success")
    return redirect(url_for('dashboard'))

@app.route('/group/<string:group_id>')
def group_page(group_id):
    if 'user_id' not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for('login'))

    # Get group information
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT unique_key, name FROM users")
    users = cursor.fetchall()
    user_map = {user[0]: user[1] for user in users}


    cursor.execute('SELECT * FROM groups WHERE group_no = ?', (group_id,))
    group = cursor.fetchone()

    if not group:
        flash("Group not found.", "danger")
        return redirect(url_for('dashboard'))

    # Get members of the group
    cursor.execute('SELECT users.name,users.unique_key FROM users,groups WHERE users.unique_key = groups.user_id AND groups.group_no = ?', (group_id,))
    members = cursor.fetchall()

    # Get expenses related to this group (if any)
    cursor.execute('SELECT * FROM expenses WHERE group_id = ?', (group_id,))
    expenses = cursor.fetchall()

    conn.close()

    expense_table = {}
    for expense in expenses:
        expense_table[expense[6]] = {
            'Amount': 0.00,  # Initialize with float
            'Date': expense[5],
            'Description': expense[7],
            'Paid By': user_map[expense[1]],
            'Split Between': set(),
            'Expense ID': expense[6]
        }

    for expense in expenses:
        expense_table[expense[6]]['Amount'] = round(expense_table[expense[6]]['Amount'] + expense[4], 2)
        
        if expense[2] is None:
            expense_table[expense[6]]['Split Between'].add((user_map[expense[1]], round(expense[4], 2)))
        else:
            expense_table[expense[6]]['Split Between'].add((user_map[expense[2]], round(expense[4], 2)))

    # Calculate total group expenses
    total_group_expense = round(sum(expense[4] for expense in expenses),2)  # Assuming amount is at index 4

    # Send the expense_table to the template
    return render_template('group_page.html', 
                        group=group, 
                        members=members, 
                        expenses=expenses, 
                        expense_table=expense_table,
                        total_group_expense=total_group_expense,
                        calculate_amount_owed=calculate_amount_owed)


@app.route('/add_members/<string:group_no>', methods=['POST'])
def add_members(group_no):
    if 'user_id' not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for('login'))

    member_id = request.form['member_id']

    # Check if the member exists
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE unique_key = ?', (member_id,))
    member = cursor.fetchone()

    if not member:
        flash("Member not found.", "danger")
        conn.close()
        return redirect(url_for('group_page', group_id=group_no))

    # Add member to the group
    cursor.execute('SELECT * FROM groups WHERE group_no = ? AND user_id = ?', (group_no, member_id))
    group_member = cursor.fetchone()

    if group_member:
        flash("Member is already part of this group.", "warning")
    else:
        group_name = cursor.execute('SELECT name FROM groups WHERE group_no = ?', (group_no,)).fetchone()[0]
        cursor.execute('INSERT INTO groups (user_id, group_no, name) VALUES (?, ?, ?)', 
                       (member_id, group_no, group_name))
        conn.commit()
        flash(f"{member['name']} has been added to the group.", "success")

    conn.close()
    return redirect(url_for('group_page', group_id=group_no))

@app.route('/record_payment', methods=['POST'])
def record_payment():
    if 'user_id' not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for('login'))

    amount = request.form['amount']
    description = request.form['description']
    payed_by = session['unique_key']
    date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Insert the record into the expenses table
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO expenses (payed_by, amount, description, date)
        VALUES (?, ?, ?, ?)
    ''', (payed_by, amount, description, date))
    conn.commit()
    conn.close()

    flash("Payment recorded successfully!", "success")
    return redirect(url_for('dashboard'))

# Record Payment Route
@app.route('/record_grp_payment/<string:group_no>', methods=['POST'])
def record_grp_payment(group_no):
    amount = request.form.get('amount')
    description = request.form.get('description')
    split_members = request.form.getlist('split_members')  # List of selected member IDs
    split_type = request.form.get('split_type')

    random_id = ''.join([str(random.randint(0, 9)) for _ in range(10)])
    payed_by = session['unique_key']

    if not amount or not description or not split_members or not split_type:
        flash("All fields are required!", "danger")
        return redirect(url_for('group_page', group_id=group_no))
    
    amount = float(amount)  # Convert amount to float

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Process split logic
    if split_type == "equally":
        share_amount = amount / len(split_members)
        
        # Calculate rounded down and up amounts
        amounts = []
        total_rounded = 0
        remainder = amount  # Track the remaining amount to be distributed

        # Distribute the amount, rounding each share
        for i in range(len(split_members)):
            if i < len(split_members) - 1:
                rounded_share = round(share_amount, 2)  # For most members, round normally
                amounts.append(rounded_share)
                total_rounded += rounded_share
                remainder -= rounded_share
            else:
                # Last member takes whatever remains
                amounts.append(round(remainder, 2))
                total_rounded += remainder
                remainder = 0

        # Ensure the total matches the original amount (due to rounding errors)
        # Adjust the last member's share if needed
        if total_rounded != amount:
            diff = amount - total_rounded
            amounts[-1] += diff

        # Assign the calculated amounts to the members
        for idx, member_id in enumerate(split_members):
            if member_id == payed_by:
                cursor.execute(
                    "INSERT INTO expenses (payed_by, amount, date, expense_id, description, group_id) VALUES (?, ?, ?, ?, ?, ?)",
                    (payed_by, amounts[idx], datetime.now().strftime('%Y-%m-%d %H:%M:%S'), random_id, description, group_no)
                )
            else:
                cursor.execute(
                    "INSERT INTO expenses (payed_by, payed_to, amount, date, expense_id, description, group_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (payed_by, member_id, amounts[idx], datetime.now().strftime('%Y-%m-%d %H:%M:%S'), random_id, description, group_no)
                )

    elif split_type == "by_amount":
        for i in range(len(split_members)):
            member_id = split_members[i]
            if member_id == payed_by:
                amount_now = request.form.get('share_or_amount_'+str(member_id))
                cursor.execute(
                    "INSERT INTO expenses (payed_by, amount, date, expense_id, description, group_id) VALUES (?, ?, ?, ?, ?, ?)",
                    (payed_by, amount_now, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), random_id, description, group_no)
                )
            else:
                amount_now = request.form.get('share_or_amount_'+str(member_id))
                cursor.execute(
                    "INSERT INTO expenses (payed_by, payed_to, amount, date, expense_id, description, group_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (payed_by, member_id, amount_now, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), random_id, description, group_no)
                )

    elif split_type == "by_share":
        total_shares = sum(int(request.form.get('share_or_amount_' + str(member_id), 0)) for member_id in split_members)

        if total_shares == 0:
            flash("Total shares cannot be zero!", "danger")
            return redirect(url_for('group_page', group_id=group_no))

        # Compute individual amounts before rounding
        amounts = []
        total_rounded = 0
        remainder = amount  # Track the remaining amount

        for i, member_id in enumerate(split_members):
            shares = int(request.form.get('share_or_amount_' + str(member_id), 0))
            share_amount = (shares / total_shares) * amount

            if i < len(split_members) - 1:
                rounded_amount = round(share_amount, 2)
                amounts.append((member_id, rounded_amount))
                total_rounded += rounded_amount
                remainder -= rounded_amount
            else:
                # Assign the remainder to the last member to correct rounding errors
                rounded_amount = round(remainder, 2)
                amounts.append((member_id, rounded_amount))
                total_rounded += rounded_amount
                remainder = 0

        # If there is any rounding difference, adjust the last member's amount
        if total_rounded != amount:
            diff = amount - total_rounded
            amounts[-1] = (amounts[-1][0], amounts[-1][1] + diff)

        # Insert into the database

        date=  datetime.now().strftime('%Y-%m-%d %H:%M:%S')


        for member_id, final_amount in amounts:
            if member_id == payed_by:
                cursor.execute(
                    "INSERT INTO expenses (payed_by, amount, date, expense_id, description, group_id) VALUES (?, ?, ?, ?, ?, ?)",
                    (payed_by, final_amount,date, random_id, description, group_no)
                )
            else:
                cursor.execute(
                    "INSERT INTO expenses (payed_by, payed_to, amount, date, expense_id, description, group_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (payed_by, member_id, final_amount,date, random_id, description, group_no)
                )

    conn.commit()
    conn.close()

    flash("Payment recorded successfully!", "success")

    return redirect(url_for('group_page', group_id=group_no))

@app.route('/delete_expense/<group_no>/<expense_id>', methods=['POST'])
def delete_expense(group_no, expense_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Delete the expense
    cursor.execute('DELETE FROM expenses WHERE group_id = ? AND expense_id = ?', (group_no, expense_id))

    conn.commit()
    conn.close()

    flash("Expense deleted successfully!", "success")

    return redirect(url_for('group_page', group_id=group_no))

# Example function to calculate amount owed
def calculate_amount_owed(payer_id, payee_id,group_no):
    # Get group information
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM expenses WHERE group_id = ?', (group_no,))
    expenses = cursor.fetchall()

    conn.close()

    answer = 0

    for expense in expenses:
        if (expense[1] == payer_id) & (expense[2] == payee_id):
            answer += expense[4]
        
        if (expense[2] == payer_id) & (expense[1] == payee_id):
            answer -= expense[4]

    return max(answer,0)

@app.route('/tracker', methods=['GET'])
def tracker():
    if 'user_id' not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Filtering logic
    params = [session['unique_key']]
    time_filter = request.args.get('timeframe', 'all')
    today = datetime.today()

    start_date = None
    end_date = None

    if time_filter == "this_month":
        start_date = today.replace(day=1).strftime('%Y-%m-%d')  # First day of the month
        last_day = calendar.monthrange(today.year, today.month)[1]  # Get last day of the month
        future_day = min(last_day + 1, calendar.monthrange(today.year, today.month)[1])  # Ensure it doesn't exceed month
        end_date = today.replace(day=future_day).strftime('%Y-%m-%d')  # Last day + 1 (or max last day)
    elif time_filter == "prev_month":
        first_day_last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
        last_day_last_month = (today.replace(day=1) - timedelta(days=1))
        start_date = first_day_last_month.strftime('%Y-%m-%d')  # First day of last month
        end_date = last_day_last_month.strftime('%Y-%m-%d')  # Last day of last month
    elif time_filter == "custom":
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

    date_filter = " AND expense_id IS NULL"
    if start_date:
        date_filter += " AND date >= ?"
        params.append(start_date)
    if end_date:
        date_filter += " AND date <= ?"
        params.append(end_date)

    # Fetch total expenses for selected timeframe (only for individual expenses)
    cursor.execute(f'SELECT SUM(amount) FROM expenses WHERE payed_by = ? {date_filter}', params)
    total_expenses = round(cursor.fetchone()[0] or 0, 2)

    # Fetch expenses grouped by description for selected timeframe
    cursor.execute(f'SELECT description, SUM(amount) FROM expenses WHERE payed_by = ? {date_filter} GROUP BY description', params)
    expense_summary = {row[0]: row[1] for row in cursor.fetchall()}

    # Fetching list of expenses for selected timeframe
    cursor.execute(f'SELECT date, amount, description FROM expenses WHERE payed_by = ? {date_filter}', params)
    expenses = cursor.fetchall()

    # Fetching how much the user owes (No Date Filter)
    cursor.execute('''
        SELECT u.name, e.payed_to, SUM(e.amount) 
        FROM expenses e
        JOIN users u ON e.payed_to = u.unique_key
        WHERE e.payed_by = ? AND e.payed_to IS NOT NULL
        GROUP BY e.payed_to
    ''', [session['unique_key']])
    owe_to = {f"{row[0]} (ID: {row[1]})": row[2] for row in cursor.fetchall()}

    # Fetching how much is owed to the user (No Date Filter)
    cursor.execute('''
        SELECT u.name, e.payed_by, SUM(e.amount) 
        FROM expenses e
        JOIN users u ON e.payed_by = u.unique_key
        WHERE e.payed_to = ? AND e.payed_by IS NOT NULL
        GROUP BY e.payed_by
    ''', [session['unique_key']])
    owed_by = {f"{row[0]} (ID: {row[1]})": row[2] for row in cursor.fetchall()}

    conn.close()

    return render_template('tracker.html', 
                           total_expenses=total_expenses, 
                           expense_summary=expense_summary, 
                           expenses=expenses, 
                           owe_to=owe_to, 
                           owed_by=owed_by, 
                           time_filter=time_filter)


@app.route('/delete_expenses/<string:date>', methods=['POST'])
def delete_expenses(date):
    if 'user_id' not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Delete the expense for the logged-in user
    cursor.execute('DELETE FROM expenses WHERE payed_by = ? AND date = ?', (session['unique_key'], date))
    conn.commit()
    conn.close()

    flash("Expense deleted successfully.", "success")
    return redirect(url_for('dashboard'))

@app.route('/vraj_only')
def vraj_only():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()
    return render_template('users.html', users=users)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000,debug = True)