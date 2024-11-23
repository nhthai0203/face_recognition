from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from resources.FaceRecognize import FaceRecognize

# Initialize flask app
app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///face_encodings.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize api and database
api = Api(app)
db = SQLAlchemy(app)

# Add resources to api
api.add_resource(FaceRecognize, '/face-recognize')

# Create database tables
@app.before_first_request
def create_tables():
    db.create_all()

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
