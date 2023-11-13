from flask import Flask, render_template, request,redirect, url_for,session
from flask_mysqldb import MySQL


app = Flask(__name__)
app.config['SECRET_KEY']='test'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'demo'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
 
mysql = MySQL(app)


@app.route("/")
def main():
    if session.get('id') == None:
        return redirect(url_for('login'))
    return render_template("main.html")

@app.route("/login", methods=('GET', 'POST'))
def login():
    if request.method=="GET":
        return render_template("login.html")
    if request.method=="POST":
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM user WHERE username = %s',(username,))
        user = cursor.fetchone()
        row = cursor.rowcount
        if row == 0:
            error = "No User!"
        else:           
            if password == user['password']:      
                session['id'] = user['id']
                session['nickname'] = user['nickname']  
                cursor.close()            
                return redirect(url_for("main"))
            else:
                error = "Wrong Password!"
        cursor.close()
        return render_template("login.html", error = error)


@app.route('/add')
def add():
    return render_template("add.html")

@app.route('/finish', methods=('GET', 'POST'))
def finish(temp):
    cursor = mysql.connection.cursor()
    
    if temp == add:
        p_name = request.form('p_name')
        p_type = request.form('p_type')
        qty  = request.form('qty')
        remark = request.form('remark')
        
        
        cursor.execute('INSERT INTO product(product_name, product_type, qty, remark, ) , (%s,%s,%s,%s)',(p_name,p_type,qty,remark))
    cursor.close()
    return render_template("finish.html")



@app.route('/search')
def search():
    cursor = mysql.connection.cursor()
    cursor.close()
    return render_template("list.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))



if __name__ == '__main__':
    app.run(debug=True)