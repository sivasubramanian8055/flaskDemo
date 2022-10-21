from flask import Flask, render_template, request, redirect, url_for, flash, session
from typing import List
from flask_sqlalchemy import SQLAlchemy
import datetime
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = (
    "postgresql+psycopg2://postgres:postgres@Localhost:5438/postgres"
)
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
db = SQLAlchemy(app)

class Users(db.Model):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    account_type = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    balance = db.Column(db.Integer, nullable=False, default=0)
    street = db.Column(db.String)
    city = db.Column(db.String)
    state = db.Column(db.String)
    zip = db.Column(db.String)
    ph_no = db.Column(db.Integer)
    dob = db.Column(db.Date)
    is_account_active = db.Column(db.Boolean)

    @classmethod
    def get_user(cls, id: int) -> List['Users']:
        if(id == 0):
            users = db.session.query(Users).all()[1:]
            users.sort()
        else:
            users = db.session.query(Users).get(id)
        return users
    
    def __repr__(self) -> str:
        return (
            '<Users('
            f'id={self.id}, '
            f'name={self.name}, '
            f'account_type={account_type}, '
            f'password={self.password}, '
            f'balance={self.balance}, '
            f'street={self.street}, '
            f'city={self.city}, '
            f'state={self.state}, '
            f'zip={self.zip}, '
            f'ph_no={self.ph_no}, '
            f'dob={self.dob},'
            f'is_account_active={self.is_account_active}'
            ')>'
        )

    def __lt__(self, other):
        return self.id < other.id

class Transactions(db.Model):
    """A python representation of the venue street address."""
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer , db.ForeignKey('users.id'))
    trans_type = db.Column(db.String)
    trans_amount = db.Column(db.Integer)
    beneficiary = db.Column(db.Integer)
    withdraw_time = db.Column(db.DateTime, default=datetime.datetime.utcnow())

    @classmethod
    def get_transactions(cls, id: int) -> List['Transactions']:

        transactions = db.session.query(
            Transactions,
        ).filter(
            (Transactions.user_id == id) | (Transactions.beneficiary == id)
        ).all()
        return transactions

    @classmethod
    def __repr__(self) -> str:
        return (
            '<Transactions('
            f'id={self.id}, '
            f'user_id={self.user_id}, '
            f'trans_type={self.trans_type},'
            f'trans_amount={self.trans_amount},'
            f'beneficiary={self.beneficiary},'
            f'withdraw_time={self.withdraw_time}'
            ')>'
        )

@app.route('/login', methods=['GET'])
def login() -> str:
    return render_template('login.html')

@app.route('/signup', methods=['GET'])
def register() -> str:
    return render_template('signup.html')

@app.route('/home', methods=['GET'])
def home() -> str:
    user = Users.get_user(session["id"])
    return render_template('home.html', balance = user.balance)

@app.route('/deposit', methods=['GET'])
def deposit() -> str:
    return render_template('deposit.html')

@app.route('/withdraw', methods=['GET'])
def withdraw() -> str:
    return render_template('withdraw.html')

@app.route('/transfer', methods=['GET'])
def transfer() -> str:
    return render_template('transfer.html')

@app.route('/users', methods=['GET'])
def users() -> str:
    users = Users.get_user(0)
    return render_template('users.html', users = users)

@app.route('/transactionHistory', methods=['GET'])
def transaction_history() -> str:
    transactions = Transactions.get_transactions(session["id"])
    return render_template('transactionHistory.html', transactions = transactions)

@app.route('/addUser', methods=['POST'])
def add_user() -> str:
    user = Users(
        name= request.form['name'],
        password= request.form['password'],
        account_type = "Savings Account",
        balance= 0,
        street= request.form['street'],
        city= request.form['city'],
        state= request.form['state'],
        zip= request.form['zip'],
        ph_no= request.form['ph_no'],
        dob=request.form['dob'],
        is_account_active = True
    )
    db.session.add(user)
    db.session.commit()
    flash('User Added successfully')
    return redirect("login")

@app.route('/depositMoney', methods=['POST'])
def deposit_money() -> str:
    transaction = Transactions(
        user_id = session["id"],
        trans_type = "Credit",
        trans_amount = request.form['depositAmount'],
        beneficiary= 0
    )
    db.session.add(transaction)
    user = Users.get_user(int(session['id']))
    updatedBalance = user.balance + int(request.form['depositAmount'])
    user.balance = updatedBalance
    db.session.commit()
    flash('Your amount has been deposited')
    return redirect("home")

@app.route('/withdrawMoney', methods=['POST'])
def withdraw_money() -> str:
    user = Users.get_user(int(session['id']))
    withdrawAmount = int(request.form['withdrawAmount'])
    if(user.balance >= withdrawAmount):
        transaction = Transactions(
            user_id = session["id"],
            trans_type = "Debit",
            trans_amount = withdrawAmount,
            beneficiary= 0
        )
        db.session.add(transaction) 
        updatedBalance = user.balance - withdrawAmount
        user.balance = updatedBalance
        db.session.commit()
        flash('Your amount has been Withdrawn')
        return redirect("home")
    else:
        flash('low balance')
        return redirect('withdraw')

@app.route('/transferMoney', methods=['POST'])
def transfer_money() -> str:
    beneficiaryId = request.form['transferId']
    if(session["id"] == int(beneficiaryId)):
        flash("You can't transfer to same account")
        return redirect("transfer")
    transferUser = Users.get_user(session["id"])
    beneficiaryUser = Users.get_user(beneficiaryId)
    amountTransfered = int(request.form['transferAmount'])
    if (beneficiaryUser == None or beneficiaryUser == "1"):
        flash('Beneficiary Does not exist')
        return redirect('transfer')
    if(transferUser.balance >= amountTransfered):
        transaction = Transactions(
            user_id = session["id"],
            trans_type = "Debit",
            trans_amount = amountTransfered,
            beneficiary= beneficiaryId
        )
        db.session.add(transaction) 
        beneficiaryUser.balance = beneficiaryUser.balance + amountTransfered
        transferUser.balance =  transferUser.balance - amountTransfered
        db.session.commit()
        flash('Your amount has been transferred')
        return redirect("home")
    else:
        flash('low balance')
        return redirect("transfer")

@app.route('/loginUser', methods=['POST'])
def login_user() -> str:
    user = Users.get_user(int(request.form['id']))
    target = "login"
    if( user == None ):
        flash("User does not exist")
    elif(user.password != request.form['password']):
        flash("Incorrect password")
    elif(user.is_account_active == False):
        flash("your account has been suspended,Kindly Reachout to the admin to activate your account")
    else:
        session["id"] = user.id
        session["name"] = user.name
        target="home"
    return redirect(target)

@app.route('/logoutUser', methods=['GET'])
def logout_user() -> str:
    session.pop("id",None)
    session.pop("name",None)
    flash("Logged Out")
    return redirect("login")