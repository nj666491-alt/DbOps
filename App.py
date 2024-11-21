from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql

app = Flask(__name__)
app.secret_key = '123456'

def get_db_connection():
    conn = pymysql.connect(
        host='localhost', 
        user='root', 
        password='r00t@123**//', 
        db='spclg'
    )
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phno = request.form['phno']
        pwd = request.form['pwd']

        hashed_pwd = generate_password_hash(pwd, method='sha256')

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM users WHERE phno = %s", (phno,))
            existing_user = cursor.fetchone()

            if existing_user:
                flash('Phone number already registered.', 'danger')
                return redirect(url_for('register'))

            cursor.execute(
                "INSERT INTO users (name, email, phno, pwd) VALUES (%s, %s, %s, %s)",
                (name, email, phno, hashed_pwd)
            )
            conn.commit()

            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))

        except Exception as e:
            flash(f'Error: {e}', 'danger')
        finally:
            conn.close()

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phno = request.form['phno']
        pwd = request.form['pwd']

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM users WHERE phno = %s", (phno,))
            user = cursor.fetchone()

            if user:
                if check_password_hash(user[4], pwd):  
                    session['user_id'] = user[0]  
                    session['user_name'] = user[1]  
                    flash('Login successful!', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    flash('Invalid password', 'danger')
            else:
                flash('Phone number not found', 'danger')

        except Exception as e:
            flash(f'Error: {e}', 'danger')
        finally:
            conn.close()

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('You need to log in first', 'danger')
        return redirect(url_for('login'))

    return render_template('dashboard.html', name=session['user_name'])

@app.route('/logout')
def logout():
    session.clear()  
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM admin WHERE username = %s", (username,))
            admin = cursor.fetchone()

            if admin and check_password_hash(admin[2], password):  
                session['admin_id'] = admin[0]
                flash('Admin login successful!', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid username or password', 'danger')

        except Exception as e:
            flash(f'Error: {e}', 'danger')
        finally:
            conn.close()

    return render_template('admin.html')

@app.route('/admin/dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if 'admin_id' not in session:
        flash('Admin access required', 'danger')
        return redirect(url_for('admin_login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        if 'add_user' in request.form:
            name = request.form['name']
            email = request.form['email']
            phno = request.form['phno']
            pwd = request.form['pwd']
            hashed_pwd = generate_password_hash(pwd, method='sha256')

            try:
                cursor.execute(
                    "INSERT INTO users (name, email, phno, pwd) VALUES (%s, %s, %s, %s)",
                    (name, email, phno, hashed_pwd)
                )
                conn.commit()
                flash('User added successfully!', 'success')
            except Exception as e:
                flash(f'Error: {e}', 'danger')

        elif 'delete_user' in request.form:
            user_id = request.form['delete_user']
            try:
                cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
                conn.commit()
                flash('User deleted successfully!', 'success')
            except Exception as e:
                flash(f'Error: {e}', 'danger')

        elif 'update_user' in request.form:
            user_id = request.form['user_id']
            name = request.form['name']
            email = request.form['email']
            phno = request.form['phno']
            pwd = request.form['pwd']

            hashed_pwd = generate_password_hash(pwd, method='sha256') if pwd else None

            if hashed_pwd:
                cursor.execute(
                    "UPDATE users SET name = %s, email = %s, phno = %s, pwd = %s WHERE id = %s",
                    (name, email, phno, hashed_pwd, user_id)
                )
            else:
                cursor.execute(
                    "UPDATE users SET name = %s, email = %s, phno = %s WHERE id = %s",
                    (name, email, phno, user_id)
                )

            conn.commit()
            flash('User updated successfully!', 'success')

    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    conn.close()
    return render_template('admin_dashboard.html', users=users)

@app.route('/admin/logout')
def admin_logout():
    session.clear()  
    flash('Admin logged out.', 'info')
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
    app.run(debug=True)
