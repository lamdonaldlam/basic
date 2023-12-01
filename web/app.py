from flask import Flask, render_template, request,redirect, url_for,session, send_file
from flask_mysqldb import MySQL
from io import BytesIO
from fpdf import FPDF


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
    return render_template("add.html",product='', status='add')

@app.route('/modify/<path:id>')
def modify(id):
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM product WHERE id=%s',(id,))
    product = cursor.fetchone()
    cursor.close()
    return render_template("add.html",product=product, status='modify')

@app.route('/finish', methods=('GET', 'POST'))
def finish():
    cursor = mysql.connection.cursor()
    
    status = request.form['type']
    p_name = request.form['p_name']
    p_type = request.form['p_type']
    qty  = request.form['qty']
    remark = request.form.get('remark')
    
        
    if status=='add':        
        cursor.execute('INSERT INTO product(product_name, product_type, qty, remark, last_modify_by) VALUES(%s,%s,%s,%s,%s)',(p_name,p_type,qty,remark,session['id']))
    if status=='modify':
        id=request.form['p_id']
        cursor.execute('UPDATE product SET product_name=%s, product_type=%s, qty=%s, remark=%s, last_modify_by=%s WHERE id=%s',(p_name,p_type,qty,remark,session['id'],id))
    mysql.connection.commit()
    cursor.close()
    return render_template("finish.html")



@app.route('/search')
def search():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT id, product_name, product_type,qty FROM product')
    product_table = cursor.fetchall()
    cursor.close()
    return render_template("list.html", items=product_table)

@app.route('/search/pdf/<path:id>')
def pdf(id):
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM product WHERE id=%s',(id,))
    product_table = cursor.fetchone()
    pdf=FPDF('P','mm','A4')
    pdf.add_page()
    pdf.set_font('helvetica','',16)
    pdf.cell(120,10,'Name:'+product_table['product_name'])
    pdf.cell(120,10,'Type:'+product_table['product_type'])
    filename= 'Product'+str(product_table['id'])+'.pdf'
    pdf.output(filename)
    cursor.close()
    return pdf.output(filename)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))



if __name__ == '__main__':
    app.run(debug=True)