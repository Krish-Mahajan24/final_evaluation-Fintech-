from flask import Flask, render_template, redirect, request, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy 
import os 
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user 
from flask_bcrypt import Bcrypt 
from flask_cors import CORS 


basedir = os.path.abspath(os.path.dirname(__file__)) 

app = Flask(__name__) 
CORS(app) 


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + \
    os.path.join(basedir, "app.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["SECRET_KEY"] = "Your secret key" 


db = SQLAlchemy(app) 

bcrypt = Bcrypt(app) 
login_manager = LoginManager() 
login_manager.init_app(app) 
login_manager.login_view = "login" 


class User(db.Model, UserMixin): 
    __tablename__ = "user" 
    id = db.Column(db.Integer, primary_key=True) 
    username = db.Column(db.String(30), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True) 
    password_hash = db.Column(db.String(100), nullable=False) 
    mobile = db.Column(db.String(15), nullable=True) 
    role = db.Column(db.String(10), nullable=False, default='user') 
    transactions = db.relationship('Transaction', backref='user', lazy=True)
    
    ROLE_CHOICES = {
        'user': 'Regular User',
        'admin': 'Administrator'
    }
   
    def set_password(self, password): 
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
   
    def check_password(self, password): 
        return bcrypt.check_password_hash(self.password_hash, password)
        
    def is_admin_user(self):
        return self.role == 'admin'


class Transaction(db.Model):
    __tablename__ = "transactions"
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


@login_manager.user_loader 
def load_user(user_id): 
    return db.session.get(User, int(user_id)) 

with app.app_context(): 
    db.create_all() 


@app.route("/") 
@app.route("/index")
def home(): 
    print("User Authenticated:", current_user.is_authenticated)
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"]) 
def login(): 
    if request.method == "POST": 
        if request.is_json:
            data = request.get_json()
            username = data.get("username")
            password = data.get("password")
            role = data.get("role", "user")
        else:
            username = request.form.get("username")
            password = request.form.get("password")
            role = request.form.get("role", "user")

        user = User.query.filter_by(username=username, role=role).first()

        if user and user.check_password(password): 
            login_user(user) 
            if request.is_json:
                return jsonify({
                    "status": "success",
                    "message": "Login successful!",
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "role": user.role
                    }
                })
            flash("Login successful!", "success") 
            return redirect(url_for("home")) 
        
        if request.is_json:
            return jsonify({
                "status": "error",
                "message": "Invalid credentials!"
            }), 401
        flash("Invalid credentials!", "danger") 
    return render_template("login.html") 


@app.route("/signup", methods=["GET", "POST"]) 
def signup(): 
    if request.method == "POST": 
        if request.is_json:
            data = request.get_json()
            username = data.get("username")
            email = data.get("email")
            password = data.get("password")
            confirm_password = data.get("confirm_password")
            mobile = data.get("mobile", None)
        else:
            username = request.form.get("username")
            email = request.form.get("email")
            password = request.form.get("password")
            confirm_password = request.form.get("confirm_password")
            mobile = request.form.get("mobile", None)

        if password != confirm_password: 
            if request.is_json:
                return jsonify({
                    "status": "error",
                    "message": "Passwords do not match!"
                }), 400
            flash("Passwords do not match!", "danger") 
            return redirect(url_for("signup")) 

        if User.query.filter_by(email=email).first(): 
            if request.is_json:
                return jsonify({
                    "status": "error",
                    "message": "Email already exists!"
                }), 400
            flash("Email already exists!", "danger") 
            return redirect(url_for("signup"))
            
        if User.query.filter_by(username=username).first():
            if request.is_json:
                return jsonify({
                    "status": "error",
                    "message": "Username already exists!"
                }), 400
            flash("Username already exists!", "danger")
            return redirect(url_for("signup"))
            
        new_user = User(
            username=username,
            email=email,
            mobile=mobile,
            role='user'
        ) 
        new_user.set_password(password) 
        db.session.add(new_user) 
        db.session.commit() 

        if request.is_json:
            return jsonify({
                "status": "success",
                "message": "Registration successful!",
                "user": {
                    "id": new_user.id,
                    "username": new_user.username,
                    "email": new_user.email,
                    "role": new_user.role
                }
            })
        flash("Registration successful! Please log in.", "success") 
        return redirect(url_for("login")) 
    
    return render_template("signup.html") 


@app.route('/dashboard')
def dashboard():
    transactions = Transaction.query.order_by(Transaction.date.desc()).all()
    return render_template('dashboard.html', transactions=transactions)


@app.route('/add', methods=['GET', 'POST'])
def add_transaction():
    if request.method == 'POST':
        transaction_type = request.form['type']
        category = request.form['category']
        amount = float(request.form['amount'])
        date = request.form['date']
        description = request.form['description']
        
        new_transaction = Transaction(
            type=transaction_type,
            category=category,
            amount=amount,
            date=date,
            description=description,
            user_id=1  # Default user_id since we're removing login
        )
        
        db.session.add(new_transaction)
        db.session.commit()
        
        return redirect(url_for('dashboard'))
    
    return render_template('tracker.html')


@app.route('/edit/<int:transaction_id>', methods=['GET', 'POST'])
def edit_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    
    if request.method == 'POST':
        transaction.type = request.form['type']
        transaction.category = request.form['category']
        transaction.amount = float(request.form['amount'])
        transaction.date = request.form['date']
        transaction.description = request.form['description']
        
        db.session.commit()
        flash('Transaction updated successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('edit_transaction.html', transaction=transaction)


@app.route('/delete/<int:transaction_id>', methods=['POST'])
def delete_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    
    db.session.delete(transaction)
    db.session.commit()
    flash('Transaction deleted successfully!', 'success')
    return redirect(url_for('dashboard'))


@app.route('/api/transactions', methods=['GET'])
def get_all_transactions():
    transactions = Transaction.query.order_by(Transaction.date.desc()).all()
    transaction_list = []
    for transaction in transactions:
        transaction_dict = {
            'id': transaction.id,
            'type': transaction.type,
            'category': transaction.category,
            'category_name': transaction.category,
            'amount': transaction.amount,
            'date': transaction.date,
            'description': transaction.description,
            'user_id': transaction.user_id
        }
        transaction_list.append(transaction_dict)
    return jsonify(transaction_list)


@app.route('/api/transactions/<int:transaction_id>', methods=['GET'])
def get_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    return jsonify({
        'id': transaction.id,
        'type': transaction.type,
        'category': transaction.category,
        'category_name': transaction.category,
        'amount': transaction.amount,
        'date': transaction.date,
        'description': transaction.description,
        'user_id': transaction.user_id
    })


@app.route('/api/transactions', methods=['POST'])
def create_transaction():
    try:
        data = request.get_json()
        new_transaction = Transaction(
            type=data['type'],
            category=data['category'],
            amount=float(data['amount']),
            date=data['date'],
            description=data.get('description', ''),
            user_id=1  # Default user_id since we're removing login
        )
        db.session.add(new_transaction)
        db.session.commit()
        return jsonify({
            'message': 'Transaction created successfully',
            'transaction': {
                'id': new_transaction.id,
                'type': new_transaction.type,
                'category': new_transaction.category,
                'amount': new_transaction.amount,
                'date': new_transaction.date,
                'description': new_transaction.description,
                'user_id': new_transaction.user_id
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@app.route('/api/transactions/<int:transaction_id>', methods=['PUT'])
def update_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    
    try:
        data = request.get_json()
        transaction.type = data['type']
        transaction.category = data['category']
        transaction.amount = float(data['amount'])
        transaction.date = data['date']
        transaction.description = data.get('description', transaction.description)
        
        db.session.commit()
        return jsonify({
            'message': 'Transaction updated successfully',
            'transaction': {
                'id': transaction.id,
                'type': transaction.type,
                'category': transaction.category,
                'amount': transaction.amount,
                'date': transaction.date,
                'description': transaction.description,
                'user_id': transaction.user_id
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@app.route('/api/transactions/<int:transaction_id>', methods=['DELETE'])
def delete_transaction_api(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    
    try:
        db.session.delete(transaction)
        db.session.commit()
        return jsonify({'message': 'Transaction deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@app.route('/templates/<template_name>')
def serve_template(template_name):
    return render_template(template_name)

@app.route('/logout')
def logout():
    logout_user()
    flash('You have been successfully logged out!', 'success')
    return redirect(url_for('home'))



@app.route("/tracker") 
def tracker(): 
    return render_template("tracker.html") 

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/credit") 
def credit(): 
    return render_template("credit.html") 


@app.route("/investing") 
def investing(): 
    return render_template("investing.html") 


@app.route("/networth") 
def networth(): 
    return render_template("networth.html") 


@app.route("/retire") 
def retire(): 
    return render_template("retire.html") 

@app.route("/help")
def help():
    return render_template("help.html")


@app.route("/api/login", methods=["POST"])
def api_login():
    if request.method == "POST":
        try:
            data = request.get_json()
            username = data.get("username")
            password = data.get("password")
            role = data.get("role", "user")

            if not username or not password:
                return jsonify({
                    "status": "error",
                    "message": "Username and password are required"
                }), 400

            user = User.query.filter_by(username=username, role=role).first()

            if user and user.check_password(password):
                login_user(user)
                return jsonify({
                    "status": "success",
                    "message": "Login successful!",
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "role": user.role
                    }
                }), 200
            else:
                return jsonify({
                    "status": "error",
                    "message": "Invalid credentials!"
                }), 401
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 500


@app.route('/api/categories', methods=['GET'])
def get_categories():
    categories = [
        {"id": "Salary", "name": "Salary"},
        {"id": "Investments", "name": "Investments"},
        {"id": "Food", "name": "Food"},
        {"id": "Transportation", "name": "Transportation"},
        {"id": "Housing", "name": "Housing"},
        {"id": "Utilities", "name": "Utilities"},
        {"id": "Entertainment", "name": "Entertainment"},
        {"id": "Shopping", "name": "Shopping"},
        {"id": "Other", "name": "Other"},
    ]
    return jsonify(categories)


@app.route('/api/summary', methods=['GET'])
@app.route('/api/summary/', methods=['GET'])
def get_summary():
    try:
        transactions = Transaction.query.all()
        total_income = sum(float(t.amount) for t in transactions if t.type == 'Income')
        total_expenses = sum(float(t.amount) for t in transactions if t.type == 'Expense')
        total_balance = total_income - total_expenses
        return jsonify({
            'total_income': total_income,
            'total_expenses': total_expenses,
            'total_balance': total_balance
        })
    except Exception as e:
        print('Error in /api/summary:', e)
        return jsonify({
            'total_income': 0,
            'total_expenses': 0,
            'total_balance': 0,
            'error': str(e)
        }), 500


if __name__ == "__main__": 
    app.run(debug=True)

