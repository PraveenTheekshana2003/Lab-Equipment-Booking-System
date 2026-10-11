from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lab.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# User Model
class User(db.Model):
  __tablename__ = 'users'

  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(80), unique=True, nullable=False)
  email = db.Column(db.String(120), unique=True, nullable=False)
  password_hash = db.Column(db.String(256), nullable=False)
  role = db.Column(db.String(20), nullable=False, default='student')

  def set_password(self, password):
    self.password_hash = generate_password_hash(password)

  def check_password(self, password):
    return check_password_hash(self.password_hash, password)


# Routes
@app.route('/')
def index():
  return jsonify({'message': 'Lab Equipment Booking System API is running'})


@app.route('/api/register', methods=['POST'])
def register():
  data = request.get_json()
  if not data or not data.get('username') or not data.get('password'):
    return jsonify({'error': 'Missing username or password'}), 400

  if User.query.filter_by(username=data['username']).first():
    return jsonify({'error': 'Username already exists'}), 400

  user = User(
      username=data['username'],
      email=data.get('email', ''),
      role=data.get('role', 'student'),
  )
  user.set_password(data['password'])
  db.session.add(user)
  db.session.commit()
  return jsonify({'message': 'User registered successfully'}), 201


@app.route('/api/login', methods=['POST'])
def login():
  data = request.get_json()
  if not data or not data.get('username') or not data.get('password'):
    return jsonify({'error': 'Missing username or password'}), 400

  user = User.query.filter_by(username=data['username']).first()
  if user and user.check_password(data['password']):
    return (
        jsonify({
            'message': 'Login successful',
            'username': user.username,
            'role': user.role,
        }),
        200,
    )

  return jsonify({'error': 'Invalid username or password'}), 401


if __name__ == '__main__':
  with app.app_context():
    db.create_all()
  app.run(debug=True)