from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import UserMixin, LoginManager, login_required
from flask_cors import CORS, cross_origin
from datetime import timedelta
from datetime import datetime
import requests
import uuid
import os
import json
from openpyxl import load_workbook
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

#import psycopg2
print('starting...')
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SECRET_KEY'] = 'hattrick'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=365)
app.config['SESSION_PERMANENT'] = True
app.permanent_session_lifetime = timedelta(days=365)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Suppress a warning

#client = MongoClient("mongodb://mongo:CE5Bf1AcB5c12HgBFB3Ff-aFAdEd-bgf@roundhouse.proxy.rlwy.net:44834")
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
CORS(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
scheduler = BackgroundScheduler()
with app.app_context():
    db.create_all()
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
    opt1 = db.Column(db.String(10000000), nullable=True)
    opt2 = db.Column(db.String(10000000), nullable=True)
    opt3 = db.Column(db.String(10000000), nullable=True)
    question = db.Column(db.String(10000000), nullable=True)
    uploaded = db.Column(db.String(10000000), nullable=True)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'correct_answer': self.correct_answer,
            'opt1': self.opt1,
            'opt2': self.opt2,
            'opt3': self.opt3,
            'question': self.question
        }

class HardQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    correct_answer = db.Column(db.String(10000000), nullable=True)
    opt1 = db.Column(db.String(10000000), nullable=True)
    opt2 = db.Column(db.String(10000000), nullable=True)
    opt3 = db.Column(db.String(10000000), nullable=True)
    question = db.Column(db.String(10000000), nullable=True)
    uploaded = db.Column(db.String(10000000), nullable=True)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'correct_answer': self.correct_answer,
            'opt1': self.opt1,
            'opt2': self.opt2,
            'opt3': self.opt3,
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
    new = EasyQuestion(correct_answer=data['correctAnswer'], opt1=data['opt1'], opt2=data['opt2'], opt3=data['opt3'], question=data['question'], uploaded=str(datetime.now().strftime('%d-%m-%Y')))

    db.session.add(new)
    db.session.commit()
    return 'Success', 200

@app.route('/upload-hard', methods=["POST"])
def uploadHard():
    data = request.get_json()
    new = HardQuestion(correct_answer=data['correctAnswer'], opt1=data['opt1'], opt2=data['opt2'], opt3=data['opt3'], question=data['question'], uploaded=str(datetime.now().strftime('%d-%m-%Y')))
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



@app.route('/upload')
def Upload():
    return render_template('quiz_upload.html')


@app.route("/clear-quiz")
def DeleteQuiz():
    db.session.query(EasyQuestion).delete()
    db.session.query(HardQuestion).delete()

    # Commit the changes to the database
    db.session.commit()
    return "Cleared", 200


@app.route('/upload-questions', methods=['POST'])
def upload_questions():
    try:
        file = request.files['file']
        data = json.loads(request.form['data'])

        # Process the uploaded Excel file
        excel_data = data['excelData']
        for table in excel_data.keys():
            rows = excel_data[table]['rows']

            for i in range(1, len(rows)):
                row = rows[i]

                question = row[0]
                correct_answer = row[1]
                options = row[2:5]
                difficulty = row[5]
                duration = 12
                points = 4

                # Check the difficulty level and upload to the appropriate collection
                collection_name = 'easy_questions' if difficulty == 'easy' else 'hard_questions'

                # Make a request to the server
                response = make_request(question, correct_answer, options, duration, points, difficulty, collection_name)
                print(response.json())

        return jsonify({'message': 'Questions uploaded successfully'}), 200

    except Exception as e:
        response = {'error': str(e)}
        return jsonify(response), 500

def make_request(question, correct_answer, options, duration, points, difficulty, collection_name):
    url = f"https://hattrick-server-production.up.railway.app/upload-{difficulty}"
    data = {
        'question': question,
        'correctAnswer': correct_answer,
        'opt1': options[0],
        'opt2': options[1],
        'opt3': options[2],
        'duration': str(duration),
        'points': str(points)
    }
    headers = {'Content-Type': 'application/json; charset=UTF-8'}
    response = requests.post(url, data=json.dumps(data), headers=headers)
    return response



@scheduler.scheduled_job('interval', days=7)  # Adjust the interval as needed
def delete_old_questions():
    one_week_ago = datetime.now() - timedelta(days=7)
    
    # Delete questions uploaded exactly one week ago
    EasyQuestion.query.filter(EasyQuestion.uploaded <= one_week_ago).delete()
    HardQuestion.query.filter(HardQuestion.uploaded <= one_week_ago).delete()

    # Commit the changes to the database
    db.session.commit()


trigger = CronTrigger(day='1')  # This will run the job on the 1st day of every month

# Schedule the job with the cron trigger
@scheduler.scheduled_job(trigger)
def credit_top_users():
    # Your existing code for crediting top users
    one_week_ago = datetime.now() - timedelta(days=7)

    # Retrieve the top 5 users with the highest super points
    top_users = User.query.order_by(User.super_points.desc()).limit(5).all()

    # Credit the top user with 1 million
    if top_users:
        top_users[0].earning_balance += 1000000

        # Credit the other 4 users with 50000 each
        for user in top_users[1:]:
            user.earning_balance += 50000

        # Commit the changes to the database
        db.session.commit()

# Start the scheduler when the Flask app starts
scheduler.start()








if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.getenv("PORT", default=5000))