from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
app = Flask(__name__)

@app.route('/')
def redirect_login():
    return redirect(url_for('login'))

@app.route('/login')
def login():
   return render_template('login.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
   global name
   if request.method == 'POST':
      name = request.form.get('name')      

   if name:
       return render_template('dashboard.html', name = name)
   elif "dashboard" in request.url:
       return render_template('dashboard.html', name = name)
   else:
       return redirect(url_for('login'))


if __name__ == '__main__':
   app.run()