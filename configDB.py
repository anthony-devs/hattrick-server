from app import app, db  # Import your Flask app and db instance
#import datetime
# Create an application context
with app.app_context():
    #db.session.flush()
    #db.drop_all()
    db.create_all()

#print(datetime.datetime.now().day)