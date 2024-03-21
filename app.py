from flask import Flask, render_template, request, redirect, session
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Connect to MySQL database
db = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    database='e_commerce'
)

# Create cursor
cursor = db.cursor()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Extract form data
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Insert user data into database
        cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, password))
        db.commit()

        # Redirect to login page
        return redirect('/login')
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Extract form data
        username = request.form['username']
        password = request.form['password']

        # Check if username and password match database records
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()

        if user:
            # Set session variable to keep user logged in
            session['username'] = username
            return redirect('/dashboard')
        else:
            # Provide error message for invalid login
            error = 'Invalid username or password. Please try again.'
            return render_template('login.html', error=error)
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        # Fetch procuct from database
        cursor.execute("SELECT * FROM products")
        products=cursor.fetchall()
        return render_template('dashboard.html', username=session['username'], products=products)
    else:
        return redirect('/login')

# Cart route
@app.route('/view_cart')
def view_cart():
    if 'username' in session:
        # Fetch cart items from database for the current user
        username = session['username']
        cursor.execute("SELECT cart.product_id, products.name, cart.quantity, products.price FROM cart JOIN products ON cart.product_id = products.id WHERE user_id = (SELECT id FROM users WHERE username = %s)", (username,))
        cart_items = cursor.fetchall()
        # print(cart_items)

        # Calculate total amount
        total = sum(item[3] * item[2] for item in cart_items)
        # print(total)

        return render_template('view_cart.html', username=username, cart=cart_items, total=total)
    else:
        return redirect('/login')
    
# Add to cart
@app.route('/add_to_cart',methods =['post'])
def add_to_cart():
    if 'username' in session:
        product_id = request.form['product_id']
        # print(product_id)

        username = session['username']
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        user_id = cursor.fetchone()[0]
        # print(user_id)

        cursor.execute("SELECT id, quantity FROM cart WHERE user_id = %s AND product_id =%s ", (user_id, product_id))
        cart_item = cursor.fetchone()
        print(cart_item)
    
        # geting prise also
        cursor.execute("SELECT price FROM products WHERE id = %s", (product_id,))
        product_price = cursor.fetchone()[0]
        # print(product_price)

        if cart_item:
            cart_id , quantity = cart_item
            quantity += 1
            # print (quantity)
            cursor.execute("UPDATE cart SET quantity = %s WHERE id = %s AND product_id = %s", (quantity,cart_id, product_id))


        else:
        # insert to db
            # print(product_price)
            cursor.execute("INSERT INTO cart (user_id, product_id, quantity, product_price) VALUES (%s, %s, %s, %s)", (user_id, product_id, 1, product_price)) 
            # cursor.execute("INSERT INTO cart (product_price) VALUES ( %s)", (product_price)) 


        db.commit()
        return redirect('/dashboard')

# Logout route
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')
    

if __name__ == '__main__':
    app.run(debug=True)
