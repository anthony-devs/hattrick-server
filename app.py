from flask import Flask, render_template, url_for, redirect, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from flask_cors import CORS, cross_origin
from datetime import timedelta
import datetime
import requests
import uuid

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # Set the database URI
app.config['SECRET_KEY'] = 'hattrick'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=365)  # Set session duration to 1 year
app.config['SESSION_PERMANENT'] = True  # Make sessions permanent
app.permanent_session_lifetime = timedelta(days=365)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
CORS(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(db.Model, UserMixin):
    id = db.Column(db.String(36), primary_key=True, unique=True)
    city = db.Column(db.String(2000), nullable=False)
    password = db.Column(db.String(80), nullable=False)
    full_name = db.Column(db.String(5000), nullable=False)
    username = db.Column(db.String(600), nullable=False, unique=True)
    email = db.Column(db.String(8000), nullable=False, unique=True)
    earning_balance = db.Column(db.Integer, nullable=True)
    coins = db.Column(db.Integer, nullable=True)
    practice_points = db.Column(db.Integer, nullable=True)
    is_subscribed = db.Column(db.Boolean, nullable=True)
    super_points = db.Column(db.Integer, nullable=True)
    day = db.Column(db.String(150), nullable=False)
    month = db.Column(db.String(150), nullable=False)
    year = db.Column(db.String(150), nullable=False)
    games_played = db.Column(db.Integer, nullable=True)

class EasyQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    correct_answer = db.Column(db.String(10000000), nullable=True)
    Opt1 = db.Column(db.String(10000000), nullable=True)
    Opt2 = db.Column(db.String(10000000), nullable=True)
    Opt3 = db.Column(db.String(10000000), nullable=True)
    question = db.Column(db.String(10000000), nullable=True)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'correct_answer': self.correct_answer,
            'Opt1': self.Opt1,
            'Opt2': self.Opt2,
            'Opt3': self.Opt3,
            'question': self.question
        }

class HardQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    correct_answer = db.Column(db.String(10000000), nullable=True)
    Opt1 = db.Column(db.String(10000000), nullable=True)
    Opt2 = db.Column(db.String(10000000), nullable=True)
    Opt3 = db.Column(db.String(10000000), nullable=True)
    question = db.Column(db.String(10000000), nullable=True)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'correct_answer': self.correct_answer,
            'Opt1': self.Opt1,
            'Opt2': self.Opt2,
            'Opt3': self.Opt3,
            'question': self.question
        }

@app.route('/register', methods=['POST'])
@cross_origin()
def Register():
    data = request.get_json()
    
    # Check if the username and email already exist
    existing_username = User.query.filter_by(username=data['username']).first()
    existing_email = User.query.filter_by(email=data['email']).first()

    if existing_username:
        return jsonify({'error': 'Username already exists'}), 92

    if existing_email:
        return jsonify({'error': 'Email already exists'}), 92
    else:
        # Generate a UUID for the new user's ID
        new_user_id = str(uuid.uuid4())

        # Hash the password
        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')

        # Create a new user with the generated ID
        new_user = User(
            id=new_user_id,
            city=data['city'],
            password=hashed_password,
            full_name=data['FullName'],
            email=data['email'],
            username=data['username'],
            earning_balance=0,
            coins=15,
            practice_points=0,
            is_subscribed=False,
            super_points=0,
            games_played = 0,
            day=str(datetime.datetime.now().day),
            month=str(datetime.datetime.now().month),
            year=str(datetime.datetime.now().year)
        )

        if data['ref_id']:
            referer = User.query.filter_by(username=data['ref_id']).first()
            referer.earning_balance += 800
            db.session.commit()

        db.session.add(new_user)
        db.session.commit()
        return {'username': new_user.username}, 200


@app.route('/delete', methods=['POST'])
@cross_origin()
def DeleteUser():
    data = request.get_json()
    user_to_delete = User.query.filter_by(id=data['uid']).first()
    
    if user_to_delete:
        db.session.delete(user_to_delete)
        db.session.commit()
        return 'User deleted successfully', 200
    else:
        return 'User not found', 404

@app.route('/login', methods=['POST'])
@cross_origin()
def Login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if user:
        try:
            if user and bcrypt.check_password_hash(user.password, data['password']):
                print(data)
                print(user.id)
                print(user.username)
                print(user.full_name)
                print(user.email)
                return jsonify({
                    'uid':user.id,
                    'username': user.username,
                    'FullName': user.full_name,
                    'city': user.city,
                    'coins': user.coins,
                    'earning_balance': user.earning_balance,
                    'email':user.email,
                    'is_subscribed':user.is_subscribed,
                    'practice_points':user.practice_points,
                    'super_points':user.super_points,
                    'played' : user.games_played,
                }), 200
                
            else:
                return jsonify({
                    "msg" : "Invalid Password"
                }), 508
        except:
            return jsonify({
                    "msg" : "Production Server Down!!!"
                }), 500
    else:
        return 'User Not Found', 404

@app.route('/auth_user', methods=['POST'])
@cross_origin()
def AuthUser():
    data = request.get_json()
    username = data['username']
    print(username)
    user = User.query.filter_by(id=username).first()
    if user:
        return jsonify({
            'uid':user.id,
            'username': user.username,
            'FullName': user.full_name,
            'city': user.city,
            'coins': user.coins,
            'earning_balance': user.earning_balance,
            'email':user.email,
            'is_subscribed':user.is_subscribed,
            'practice_points':user.practice_points,
            'super_points':user.super_points,
            'played' : user.games_played,
        }), 200
    else:
        return 'Invalid User', 404

@app.route('/')
@cross_origin()
def index():
    return 'Unauthorized User', 403

@app.route('/upload-easy', methods=["POST"])
def uploadEasy():
    data = request.get_json()
    new = EasyQuestion(correct_answer=data['correctAnswer'], Opt1=data['opt1'], Opt2=data['opt2'], Opt3=data['opt3'], question=data['question'])

    db.session.add(new)
    db.session.commit()
    return 'Success', 200

@app.route('/upload-hard', methods=["POST"])
def uploadHard():
    data = request.get_json()
    new = HardQuestion(correct_answer=data['correctAnswer'], Opt1=data['opt1'], Opt2=data['opt2'], Opt3=data['opt3'], question=data['question'])
    db.session.add(new)
    db.session.commit()
    return 'Success', 200

@app.route('/easy_questions', methods=["GET"])
def getEasyQuestions():
    questions = EasyQuestion.query.all()
    return jsonify([question.serialize for question in questions]), 200

@app.route('/hard_questions', methods=["GET"])
def getHardQuestions():
    questions = HardQuestion.query.all()
    return jsonify([question.serialize for question in questions]), 200

@app.route("/playable", methods=["POST"])
def Playable():
    data = request.get_json()
    user = User.query.filter_by(id=data['uid']).first()
    return jsonify(
        {
            "coins" : user.coins
        }
    )
@app.route('/post-game', methods=["POST"])
def PostPracticeGame():
    data = request.get_json()
    user = User.query.filter_by(id=data['uid']).first() # Get the current authenticated user
    print(data["type"])
    if user:
        if int(data['score']) > 9 and bool(user.is_subscribed):
        # Update the user's profile information based on the data sent in the request
            if data['type'] == "QuizType.Super_League":
                user.super_points += int(data["score"])
                user.coins -= 1
            else:
                user.practice_points += int(data['score'])
                user.coins -= 1
                user.earning_balance += 10
            
            
            # You can update other fields as needed

            db.session.commit()  # Commit the changes to the database
            return jsonify({
            'uid':user.id,
            'username': user.username,
            'FullName': user.full_name,
            'city': user.city,
            'coins': user.coins,
            'earning_balance': user.earning_balance,
            'email':user.email,
            'is_subscribed':user.is_subscribed,
            'practice_points':user.practice_points,
            'super_points':user.super_points,
            'msg': 'You are A Winner'
        }), 200
        else:
            if bool(user.is_subscribed):
                if data['type'] == "QuizType.Super_League":
                    user.super_points += int(data["score"])
                    user.coins -= 1
                    user.games_played += 1
                else:
                    user.practice_points += int(data['score'])
                    user.coins -= 1
                    user.games_played += 1
            else:
                user.practice_points += int(data['score'])
                user.games_played += 1
                user.coins -= 1
            db.session.commit()
            if int(data['score']) < 9 :
                return jsonify({
                'uid':user.id,
                'username': user.username,
                'FullName': user.full_name,
                'city': user.city,
                'coins': user.coins,
                'earning_balance': user.earning_balance,
                'email':user.email,
                'is_subscribed':user.is_subscribed,
                'practice_points':user.practice_points,
                'super_points':user.super_points,
                'msg': 'You Are getting a hang of it'
            }), 200
            else:
                return jsonify({
                'uid':user.id,
                'username': user.username,
                'FullName': user.full_name,
                'city': user.city,
                'coins': user.coins,
                'earning_balance': user.earning_balance,
                'email':user.email,
                'is_subscribed':user.is_subscribed,
                'practice_points':user.practice_points,
                'super_points':user.super_points,
                'msg': 'You Are Good at This!'
            }), 200
    else:
        return 'User not found', 404

def get_country_flag(country_name):
    response = requests.get(f'https://restcountries.com/v2/name/{country_name}')
    data = response.json()
    if response.status_code == 200:
        return data[0]['flags']['png']
    else:
        return "Country not found"


@app.route("/get-board", methods=['GET'])
def getBoard():
    # Retrieve the top 30 users with the highest super points
    top_users = User.query.order_by(User.super_points.desc()).limit(100).all()

    # Create a list of user information to return
    
    leaderboard = [
        {
            'username': user.username,
            'super_points': user.super_points,
            'city': get_country_flag(user.city)
        }
        for user in top_users
    ]

    return jsonify(leaderboard), 200

@app.route("/get-three", methods=['GET'])
def getThree():
    # Retrieve the top 30 users with the highest super points
    top_users = User.query.order_by(User.super_points.desc()).limit(3).all()

    # Create a list of user information to return
    
    leaderboard = [
        {
            'username': user.username,
            'super_points': user.super_points,
            'city': get_country_flag(user.city)
        }
        for user in top_users
    ]

    return jsonify(leaderboard), 200


def calculate_percentage(part, whole):
    if whole == 0:
        return 0  # Avoid division by zero
    return (part / whole) * 100
@app.route("/userlytics",methods=['POST'])
def GetUserAnalytics():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    all_points = user.practice_points + user.super_points
    return jsonify({
        'username': user.username,
        'FullName': user.full_name,
        'city': user.city,
        'practice_points':user.practice_points,
        'super_points':user.super_points,
        'percentage' : calculate_percentage(all_points, user.games_played * 10),
        'played' : user.games_played,
        'flag': get_country_flag(user.city)
    })

@app.route('/edit-user', methods=['POST'])
@cross_origin()
@login_required  # Use the login_required decorator to ensure the user is authenticated
def EditUser():
    data = request.get_json()
    user = User.query.filter_by(id=data['uid']).first()  # Get the current authenticated user

    if user:
        # Update the user's profile information based on the data sent in the request
        user.city = data['city']
        user.full_name = data['FullName']
        user.email = data['email']
        user.username = data['username']
        # You can update other fields as needed

        db.session.commit()  # Commit the changes to the database

        return jsonify({
            'uid': user.id,
            'username': user.username,
            'FullName': user.full_name,
            'city': user.city,
            'coins': user.coins,
            'earning_balance': user.earning_balance,
            'email': user.email,
            'is_subscribed': user.is_subscribed,
            'practice_points': user.practice_points,
            'super_points': user.super_points,
            'msg': 'Profile updated successfully'
        }), 200
    else:
        return 'User not found', 404
    
previous_month = 0

@app.route("/buy-coins", methods=['POST'])
def initCoins():
    data = request.get_json()
    user = User.query.filter_by(id=data['uid']).first()
    if user: 
        user.coins += int(data['amt'])
        db.session.commit()
        return "Coins Purchased", 200
    else:
        return "User Not Found", 404


def check_new_month():
    global previous_month

    # Get the current month
    current_month = datetime.datetime.now().month

    if datetime.datetime.now().day == 1:
        previous_month = current_month
        return True
    else:
        return False
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    if check_new_month:
        top_user = User.query.order_by(User.super_points.desc()).limit(5).all()
        # Create a list of user information to return
        top_user.earning_balance += 50
        