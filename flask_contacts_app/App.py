from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from functools import wraps



app = Flask(__name__)

#MySql Connection 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flaskcontacts'
mysql = MySQL(app)


#settings
app.secret_key = 'mysecretkey'


@app.route('/')
def Index():
    return render_template('index.html')

    
@app.route('/add_contact' , methods=['POST'])
def add_contact():
    if request.method == 'POST':
        fullname = request.form ['fullname']
        phone = request.form ['phone']
        email = request.form ['email']
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO contacts (fullname, phone , email, usuarioId) VALUES (%s, %s, %s, %s)',
        (fullname, phone, email, session['id']))
        mysql.connection.commit()
        flash('Contact Added Succesfully')
        return redirect(url_for('dashboard'))

@app.route('/edit/<id>')
def get_contact(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT *FROM contacts WHERE id = %s' , [id])
    data =cur.fetchall()
    return render_template('edit-contact.html', contact =data[0])


@app.route('/update/<id>', methods = ['POST'])
def update_contact(id):
  if request.method == 'POST':
    fullname = request.form['fullname']
    phone = request.form['phone']
    email = request.form['email']
    cur = mysql.connection.cursor()
    cur.execute("""
      UPDATE contacts
      SET fullname = %s,
          email = %s,
          phone = %s
      WHERE id = %s    
    """, (fullname, email, phone, id))
    mysql.connection.commit()
    flash('Contact Updated Succesfully')
    return redirect(url_for('dashboard'))


@app.route('/delete/<string:id>')
def delete_contact(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM contacts WHERE id = {0}'.format(id))
    mysql.connection.commit()
    flash('Contact Removed Succesfully')
    return redirect(url_for('dashboard'))


@app.route('/register', methods = ['GET','POST'])
def register_user():
    
    if request.method == 'POST':
        user = request.form['user']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO usuarios (user, password) VALUES (%s, %s)',
        (user, password))
        mysql.connection.commit()
        flash('User Registered Succesfully')
        return render_template('login.html')

    return render_template('register.html',form=request.form)



@app.route('/login', methods = ['GET', 'POST'])
def login_user():
    if request.method == 'POST':
       
        user = request.form ['user']
        password_candidate = request.form ['password']
        cur = mysql.connection.cursor()
        result = cur.execute('SELECT * FROM usuarios WHERE user = %s' , [user])
        
        if result > 0:
            
            data = cur.fetchone()
            print(data)
            password = data[2]           

        
            if password_candidate == password:
                #
                    session['logged_in'] = True
                    session ['user'] = user
                    session['id'] = data[0]
                    flash('Has iniciado sesion', 'success')
                    app.logger.info('PASSWORD_MATCHED')
                    return redirect(url_for('dashboard'))

            else:
                    app.logger.info('PASSWORD NOT MATCHED')
                    error = 'Invalid login'
                    return render_template('login.html', error=error)
                
            cur.close()

        else: 
                app.logger.info('NO USER')
                error = 'Username not found'
                return render_template('login.html', error=error)

        
    return render_template('login.html')

def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
            if 'logged_in' in session:
                return f(*args, **kwargs)
            else:
                flash('Unauthorized Please Login', 'danger')
                return redirect(url_for('login.html'))
    return wrap

@app.route('/dashboard')
@is_logged_in
def dashboard():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM contacts WHERE usuarioId = %s', [session['id']])
    data = cur.fetchall()
    print(session)
    return render_template('dashboard.html', contacts = data)
   

#LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    flash('You are now logged out','success')
    return redirect(url_for('login_user'))

    

if __name__ == "__main__":
    app.run(port = 3000, debug = True)


