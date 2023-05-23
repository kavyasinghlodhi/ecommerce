from flask import Flask, request, render_template, redirect, session
from distutils.log import debug
from fileinput import filename
import sqlite3
import os
from flask_bcrypt import Bcrypt

app = Flask(__name__)
conn = sqlite3.connect('online.db',check_same_thread=False)
from werkzeug.utils import secure_filename
UPLOAD_FOLDER = './static/img/products'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
bcrypt = Bcrypt(app)
app.secret_key = "anythig"


@app.route('/')
def home():
    result = conn.execute('Select * from products')
    items=result.fetchall()
    return render_template('index.html', items=items)
    
@app.route('/products')
def products():
    result = conn.execute('Select * from products')
    items=result.fetchall()
    return render_template('products.html', items=items)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/logout')
def logout():
    if session.get("loggedin") != "true":
        return redirect("/login")
    session.clear()
    return redirect('/')

@app.route('/admin/add', methods=['GET', 'POST'])
def admin_add():
    if session.get('email') == 'admin@admin.com' and bcrypt.check_password_hash(session.get('pass'), 'k@bbu') == True:
        if request.method == 'POST':
            result = request.form
            result_ = conn.execute(f"""select * from products where name='{result['name']}'""")
            asd = len(result_.fetchall())
            if asd==0:
                f = request.files.get('img')
                filename = secure_filename(f.filename)
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                conn.execute(f'''insert into products (NAME,DESC,IMAGE,PRICE) values ('{result['name']}','{result['desc']}','{result['file']}','{result['price']}')''')
                conn.commit()
                return render_template('admin-add.html', result="Product Added Successfully.")
            else:
                return render_template("admin-add.html", result="Please enter a different product name.")
        else:
            return render_template('admin-add.html')
    else:
        return redirect('/')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if session.get('email') != 'admin@admin.com' and bcrypt.check_password_hash(session.get('pass'), 'k@bbu') != True:
        return redirect("/")
    result = conn.execute(f"select * from orders")
    data_ = result.fetchall()
    if len(data_) > 0:
        items = []
        i = 0
        total = 0
        for row in data_:
            result_ = conn.execute(f'''select * from products where name='{row[3]}' ''')
            comple = data_[i][5]
            name = data_[i][1]
            email = data_[i][2]
            address = data_[i][4]
            i+=1
            data = result_.fetchone()
            data_2 = []
            data_2.append(i)
            data_2.append(data[1])
            data_2.append(data[2])
            data_2.append(data[3])
            data_2.append(data[4])
            data_2.append(comple)
            data_2.append(name)
            data_2.append(email)
            data_2.append(address)
            items.append(data_2)
            total+=int(data[4])
        return render_template("admin.html",items=items, total=total)
    else:
        return render_template("admin.html", comment="No order...")
@app.route('/product/<name>', methods=['GET', 'POST'])
def product(name):
    a = "None"
    result = conn.execute(f"select * from products where name='{name}'")
    items=result.fetchone()
    found_wish = ""
    if session.get('loggedin') == 'true':
        result_4 = conn.execute(f'select * from wishlist where user="{session.get("email")}"')
        for row in result_4:
            if row[2] == name:
                found_wish = "True"
    else:
        found_wish = "login"

    if request.method == 'POST':
        if session.get("loggedin") == "true":
            result_ = conn.execute(f"""select * from bag where user='{session.get("email")}' """)
            data = result_.fetchall()
            # return f"""select * from bag where user='{session.get("email")}'"""
            if len(data) == 0:
                conn.execute(f'''insert into bag (user,product) values ('{session.get("email")}','{name}')''')
                conn.commit()
                return render_template('product.html', items=items, comment="Item Added to Bag...")
            else:
                a = "Fal;"
                for item in data:
                    if item[2]==name:
                        a = "true"
                    else:
                        a = "false"
                if a=="true":
                    return render_template('product.html', items=items, comment="Item Already Added...", name=name, found_wish=found_wish)
                else:
                    conn.execute(f'''insert into bag (user,product) values ('{session.get("email")}','{name}')''')
                    conn.commit()
                    return render_template('product.html', items=items, comment="Item Added to Bag...", name=name, found_wish=found_wish)
        else:
            return redirect("/login")
    else:
        return render_template('product.html', items=items, comment="", name=name, found_wish=found_wish) 
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        result = request.form
        # pw_hash = result['pass']

        # result = bcrypt.check_password_hash("DB SE VALUE", pw_hash) # returns True
        result_ = conn.execute(f"""select * from users where email='{result['email']}'""")
        data = result_.fetchone()
        asd = len(data)
        if asd>0:
            pwd = data[3]
            pwd2 = result['pass']
            if bcrypt.check_password_hash(pwd, pwd2) == True:
                session['email'] = data[2]
                session['name'] = data[1]
                session['pass'] = data[3]
                session['loggedin'] = 'true'
                return redirect("/")
            else:
                return render_template("login.html", result="Please enter correct Credentials")
                
        else:
            return render_template("login.html", result="Account does not exist.")
        
    else:
        return render_template("login.html")
    
@app.route('/bag', methods=['GET', 'POST'])
def bag():
    if session.get("loggedin") != "true":
        return redirect("/login")
    result = conn.execute(f"select * from bag where user='{session.get('email')}'")
    items = []
    total = 0
    for row in result:
        result_ = conn.execute(f'''select * from products where name="{row[2]}"''')
        data = result_.fetchone()
        total+=int(data[4])
        items.append(data)
    return render_template("bag.html",items=items, total = total)
    

@app.route('/wishlist', methods=['GET', 'POST'])
def wishlist():
    if session.get("loggedin") != "true":
        return redirect("/login")
    result = conn.execute(f"select * from wishlist where user='{session.get('email')}'")
    items = []
    total = 0
    for row in result:
        result_ = conn.execute(f'''select * from products where name="{row[2]}"''')
        data = result_.fetchone()
        total+=int(data[4])
        items.append(data)
    return render_template("wishlist.html",items=items, total = total)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        result = request.form
        pw_hash = bcrypt.generate_password_hash(result['pass']).decode("utf-8")
        result_ = conn.execute(f"""select * from users where email='{result['email']}'""")
        asd = len(result_.fetchall())
        if asd==0:
            conn.execute(f"""insert into users (name,email,password) values ('{result['name']}','{result['email']}',"{pw_hash}")""")
            conn.commit()
            return redirect("/login")
        else:
            return render_template("register.html", result="Email already in use. Please try with different email.")
            
    else:
        return render_template("register.html")
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if session.get("loggedin") != "true":
        return redirect("/login")
    result = conn.execute(f"select * from bag where user='{session.get('email')}'")
    items = []
    total = 0
    for row in result:
        result_ = conn.execute(f'''select * from products where name="{row[2]}"''')
        data = result_.fetchone()
        total+=int(data[4])
        items.append(data)
    result_3 = conn.execute(f"select * from users where email='{session.get('email')}'")
    data_4 = result_3.fetchone()
    if request.method == "POST":
        result_2 = request.form
        for item in items:
            conn.execute(f"""insert into orders (name,email,products,address,completed) values ('{session.get('name')}','{session.get('email')}',"{item[1]}","{result_2['address']+", "+result_2['city']+", "+result_2['state']}", "no")""")
            conn.commit()
        for item in items:
            conn.execute(f"""delete from bag where user='{session.get("email")}'""")
            conn.commit()
        conn.execute(f"""update users set address="{result_2['address']}", city="{result_2['city']}", state="{result_2['state']}" where email='{session.get("email")}' """)
        conn.commit()
        return render_template('order-success.html')
    else:    
        return render_template("checkout.html",items=items, total = total, addre = data_4)

@app.route('/orders', methods=['GET', 'POST'])
def orders():
    if session.get("loggedin") != "true":
        return redirect("/login")
    result = conn.execute(f"select * from orders where email='{session.get('email')}'")
    data_ = result.fetchall()
    items = []
    total = 0
    i = 0
    for row in data_:
        result_ = conn.execute(f'''select * from products where name="{row[3]}"''')
        comple = data_[i][5]
        data = result_.fetchone()
        data_2 = []
        data_2.append(data[0])
        data_2.append(data[1])
        data_2.append(data[2])
        data_2.append(data[3])
        data_2.append(data[4])
        data_2.append(comple)
        total+=int(data[4])
        items.append(data_2)
        i+=1
    return render_template("orders.html",items=items, total = total)

@app.route('/markasdelivered/<name>', methods=['GET', 'POST'])
def markasdelivered(name):
    if session.get('email') != 'admin@admin.com' and bcrypt.check_password_hash(session.get('pass'), 'k@bbu') != True:
        return redirect("/")
    result = conn.execute(f"UPDATE orders SET completed = 'yes' where id='{name}'")
    conn.commit()
    return redirect("/admin")

@app.route('/markasundelivered/<name>', methods=['GET', 'POST'])
def markasundelivered(name):
    if session.get('email') != 'admin@admin.com' and bcrypt.check_password_hash(session.get('pass'), 'k@bbu') != True:
        return redirect("/")
    result = conn.execute(f"UPDATE orders SET completed = 'no' where id='{name}'")
    conn.commit()
    return redirect("/admin")

@app.route('/account', methods=['GET', 'POST'])
def account_():
    if session.get("loggedin") != "true":
        return redirect("/login")
    if session.get("loggedin") == "true":
        return render_template("account.html")
    else:
        return redirect("/login")

@app.route('/delete/<name>', methods=['GET', 'POST'])
def delete(name):
    if session.get('email') != 'admin@admin.com' and bcrypt.check_password_hash(session.get('pass'), 'k@bbu') != True:
        return redirect("/")
    result = conn.execute(f"delete from products where id='{name}'")
    conn.commit()
    return redirect("/admin/products")


@app.route('/admin/products', methods=['GET', 'POST'])
def admin_products():
    if session.get('email') != 'admin@admin.com' and bcrypt.check_password_hash(session.get('pass'), 'k@bbu') != True:
        return redirect("/")
    result = conn.execute(f"select * from products")
    items = []
    total = 0
    for row in result:
        result_ = conn.execute(f'''select * from products where name="{row[1]}"''')
        data = result_.fetchone()
        total+=int(data[4])
        items.append(data)
    return render_template("admin-products.html",items=items, total = total)

@app.route('/change-password', methods=['GET', 'POST'])
def change_pass():
    if session.get("loggedin") != "true":
        return redirect("/login")
    if request.method == 'POST':
        result = request.form
        # pw_hash = result['pass']
        pw_hash = bcrypt.generate_password_hash(result['npass']).decode("utf-8")
        # result = bcrypt.check_password_hash("DB SE VALUE", pw_hash) # returns True
        result_ = conn.execute(f"""select * from users where email='{result['email']}'""")
        data = result_.fetchone()
        if data==None:
            return render_template("change-password.html", result="No such user")
        elif len(data)>0:
            pwd = data[3]
            pwd2 = result['pass']
            if bcrypt.check_password_hash(pwd, pwd2) == True:
                result = conn.execute(f"UPDATE users SET password = '{pw_hash}' where email='{data[2]}'")
                conn.commit()
                return render_template("change-password.html", result="Password Changed Successfully")
            else:
                return render_template("change-password.html", result="Please enter correct Credentials")
                
        else:
            return render_template("change-password.html", result="Account does not exist.")
        
    else:
        return render_template("change-password.html")
    
@app.route('/wishlist/add/<name>', methods=['GET', 'POST'])
def wishlist_add(name):
    if session.get("loggedin") != "true":
        return redirect("/login")
    conn.execute(f"""insert into wishlist (user,product) values ('{session.get("email")}','{name}')""")
    conn.commit()
    return redirect(f"/product/{name}")

@app.route('/wishlist/remove/<name>', methods=['GET', 'POST'])
def wishlist_remove(name):
    if session.get("loggedin") != "true":
        return redirect("/login")
    conn.execute(f"""delete from wishlist where user='{session.get("email")}' and product='{name}'""")
    conn.commit()
    return redirect(f"/product/{name}")

@app.route('/wishlist/remove_/<name>', methods=['GET', 'POST'])
def wishlist_remove_(name):
    if session.get("loggedin") != "true":
        return redirect("/login")
    conn.execute(f"""delete from wishlist where user='{session.get("email")}' and product='{name}'""")
    conn.commit()
    return redirect(f"/wishlist")

if __name__ == '__main__':
    app.run(debug=True)
