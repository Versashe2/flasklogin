# Gestor de contactos -  Flask & MYSQL

En el archivo App.py estan la conexion a la base de datos, la configurarcion para las peticiones http de GET y POST de nuestra app, las rutas a los distintos templates y el manego del usuario y su sesion.
En la carpeta templates estan todos los documentos html para las distintas vistas de la aplicacion web.

## Index

Devuelve el archivo index.html

```python
@app.route('/')
def Index():
    return render_template('index.html')
```

### add_contact 

Hace la peticion para agregar un contacto.
Los valores de pasados a la query son levantados del formulario en dashboard.html.
Con el manejo de sesion asignamos el id correspondiente para que el contacto quede relacionado a un usuario

```python
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
```

```html
<form action="/add_contact" method="POST">
    <input type="text" name="fullname" placeholder="Nombre">
    <input type="text" name="phone" placeholder="Teléfono">
    <input type="text" name="email" placeholder="Email">
    <button type="submit">
        Save
    </button>
</form>
```

### get_contact

Busca el contacto que vamos a editar y lo llevan en el formulario para que agregue nuevos valores

```python
@app.route('/edit/<id>')
def get_contact(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT *FROM contacts WHERE id = %s' , [id])
    data =cur.fetchall()
    return render_template('edit-contact.html', contact =data[0])
```


```html
<form action="/update/{{contact.0}}" method="POST">
    <input type="text" name="fullname" placeholder="Fullname" value="{{ contact.1 }}">
    <input type="text" name="phone" placeholder="Phone" value="{{ contact.2 }}">
    <input type="text" name="email" placeholder="Email" value="{{ contact.3 }}">
    <button type="submit">
        Save
    </button>    
</form> 
```

### update_contact

de la informacion en el formulario de editar contacto enviamos el formulario al a base de datos

```python
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
```

### delete_contact

selecciona el contacto a borrar obtenemos el id de la tabla en el dashboard donde lo visualizamos

```python
@app.route('/delete/<string:id>')
def delete_contact(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM contacts WHERE id = {0}'.format(id))
    mysql.connection.commit()
    flash('Contact Removed Succesfully')
    return redirect(url_for('dashboard'))
```


```html
<tbody>
    {% for contact in contacts %}
    <tr>
        <td>{{ contact.1}}</td>
        <td>{{ contact.2}}</td>
        <td>{{ contact.3}}</td>
        <td>
            <a href="/edit/{{contact.0}}">Editar</a>
            <a href="/delete/{{contact.0}}">Borrar</a>
        </td>
    </tr>
    {% endfor %}
</tbody>
```


### register

Esta funcion responde a las peticiones get y post. Get devuevle la vista de register y post envia el formulario para registar usuario

```python
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
```


```html
<form action="/register" method="POST">
    <input type="text" name="user" placeholder="user">
    <input type="text" name="password" placeholder="password">
    <button type="submit">
      Register
    </button>
</form>
```

### login_user

Esta funcion responde a las peticiones get y post. Get devuevle la vista de login.html y post envia el formulario para logear al usuario si la contraseña ingresada corresponde con la guardada en la base de datos, guardamos en el objeto sesion la info del dicho usuario


```python
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
```


```html
<form action="/login" method="POST">
    <input type="text" name="user" placeholder="user">
    <input type="text" name="password" placeholder="password">
    <button type="submit">
      Login
    </button>
</form>
```


### is_logged_in

esta funcion confirma que sea verdadero el valor logged_in en el objeto session

```python
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
            if 'logged_in' in session:
                return f(*args, **kwargs)
            else:
                flash('Unauthorized Please Login', 'danger')
                return redirect(url_for('login.html'))
    return wrap
```

### dashboard

a esta ruta solo se puede acceder si el usuario esta logeado y lo redirecciona al dashboard donde vera sus contactos

```python
@app.route('/dashboard')
@is_logged_in
def dashboard():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM contacts WHERE usuarioId = %s', [session['id']])
    data = cur.fetchall()
    print(session)
    return render_template('dashboard.html', contacts = data)
```

### logout

dispara la accionde cerrar la sesion del usuario

```python
@app.route('/logout')
def logout():
    session.clear()
    flash('You are now logged out','success')
    return redirect(url_for('login_user'))

```