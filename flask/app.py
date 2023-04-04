from flask import Flask, render_template, request, session, redirect, url_for
import redis

app = Flask(__name__)
app.secret_key = 'secret_key'
redis_host = 'localhost'
redis_port = 6379
redis_password = ''

# Initialize Redis connection
redis_conn = redis.StrictRedis(
    host=redis_host, port=redis_port, password=redis_password, decode_responses=True
)

@app.route('/', methods=['GET'])
def home():
    # Check if user is logged in
    if 'username' in session:
        username = session['username']
        return render_template('home.html', username=username)
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Check if user is already logged in
    if 'username' in session:
        return redirect(url_for('home'))

    # Handle login form submission
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if username and password are valid
        user_data = redis_conn.hgetall('users:{}'.format(username))
        if user_data and user_data['password'] == password:
            # Save username in session
            session['username'] = username
            return redirect(url_for('home'))
        else:
            error = 'Invalid credentials. Please try again.'
            return render_template('login.html', error=error)

    # Display login form
    else:
        return render_template('login.html')

@app.route('/logout')
def logout():
    # Clear session and redirect to login page
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Check if user is already logged in
    if 'username' in session:
        return redirect(url_for('home'))

    # Handle registration form submission
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if username already exists
        if redis_conn.hexists('users:{}'.format(username), 'password'):
            error = 'Username already taken. Please choose a different username.'
            return render_template('register.html', error=error)

        # Create new user
        user_data = {'username': username, 'password': password}
        redis_conn.hmset('users:{}'.format(username), user_data)

        # Save username in session
        session['username'] = username

        return redirect(url_for('home'))

    # Display registration form
    else:
        return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True)
