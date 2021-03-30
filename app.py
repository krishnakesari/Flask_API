## Import statement
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float
import os
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from flask_mail import Mail, Message

## variable set to the flask instructor
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'planets.db')
### Creating an access token
app.config['JWT_SECRET_KEY'] = 'super-secret' # change secret later
### Creating an email server
app.config['MAIL_SERVER'] = 'smtp.mailtrap.io'
#### Creating a log in configuration
app.config['MAIL_USERNAME'] = os.environ['MAIL_USERNAME']
app.config['MAIL_PASSWORD'] = os.environ['MAIL_PASSWORD']

### Initialize database before using
db = SQLAlchemy(app)
### Adding Marshmallow
ma = Marshmallow(app)
### Adding JWT manager
jwt = JWTManager(app)
### Adding Mail configuration
mail = Mail(app)

#### Initializing CLI commands
##### 1. Create command to create database
@app.cli.command('db_create') # decorator line
def db_create():   # Creating function definition
    db.create_all()
    print('Database created!')

##### 2. Create command to drop database
@app.cli.command('db_drop')
def db_drop():
    db.drop_all()
    print('Database dropped!')

#### 3. Create command to seed database
@app.cli.command('db_seed')
def db_seed():
    mercury = Planet(planet_name='Mercury',
                     planet_type='Class D',
                     home_star='Sol',
                     mass=3.258e23,
                     radius=1516,
                     distance=35.98e6)

    venus = Planet(planet_name='venus',
                         planet_type='Class K',
                         home_star='Sol',
                         mass=4.867e24,
                         radius=3760,
                         distance=67.24e6)

    earth = Planet(planet_name='Earth',
                         planet_type='Class M',
                         home_star='Sol',
                         mass=5.972e24,
                         radius=3959,
                         distance=92.96e6)

    db.session.add(mercury)
    db.session.add(venus)
    db.session.add(earth)

    test_user = User(first_name='William',
                     last_name='Herschel',
                     email='test@test.com',
                     password='pass')

    db.session.add(test_user)
    db.session.commit()
    print('Database seeded!')

## Decorator (gives special capabilities to functions) in python
## Defining route for our endpoint (URL)
@app.route('/')
def hello_world():
    return 'Hello World!'


## Create an endpoint link
@app.route('/super_simple')
def super_simple():
    return jsonify(message='Hello from the planetary API. boo ya!!')


## Create another endpoint link
@app.route('/not_found')
def not_found():
    return jsonify(message='That resources was not found'), 404


## Add parameters
@app.route('/parameters')
def parameters():
    name = request.args.get('name')
    age = int(request.args.get('age'))
    if age < 18:
        return jsonify(messsage='sorry '+name+' , not authorized'), 401
    else:
        return jsonify(message='welcome ' + name)


## Add URL variables
@app.route('/url_variables/<string:name>/<int:age>')
def url_variables(name: str, age: int):
    if age < 18:
        return jsonify(messsage='sorry '+name+' , not authorized'), 401
    else:
        return jsonify(message='welcome ' + name)

## Add URL for 'GET' Requests
@app.route('/planets', methods=['GET'])
def planets():
    planets_list = Planet.query.all()
    result = planets_schema.dump(planets_list)
    return jsonify(result)

## Creating JWT for registering new users
@app.route('/register',methods=['POST'])
def register():
    email = request.form['email']
    test = User.query.filter_by(email=email).first()
    if test:
        return jsonify(message='email already exists'),409
    else:
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        password = request.form['password']
        user = User(first_name=first_name, last_name=last_name, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return jsonify(message="User Created Successfully"), 201

# Creating route definition for access token
@app.route('/login', methods=['POST'])
def login():
    if request.is_json:
        email = request.json['email']
        password = request.json['password']
    else:
        email = request.form['email']
        password = request.form['password']

    test = User.query.filter_by(email=email, password=password).first()
    if test:
        access_token = create_access_token(identity=email)
        return jsonify(message="Login succeeded!", access_token=access_token)
    else:
        return jsonify(message="Not correct email or password"), 401

#  Creating route for email reset password
@app.route('/retrieve_password/<string:email>', methods=['GET'])
def retrieve_password(email: str):
    user = User.query.filter_by(email=email).first()
    if user:
        msg = Message("your Planetary API password is" + user.password,
                      sender="admin@planetary-api.com",
                      recipients=[email])
        mail.send(msg)
        return jsonify(message="Password sent to " + email)
    else:
        return jsonify(message="That email doesn't exist")

# Creating route for retrieving details

# database models
class User(db.Model):
    __table_name__ = 'users'
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)

class Planet(db.Model):
    __tablename__ = 'planets'
    planet_id = Column(Integer, primary_key=True)
    planet_name = Column(String)
    planet_type = Column(String)
    home_star = Column(String)
    mass = Column(Float)
    radius = Column(Float)
    distance = Column(Float)

class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'first_name', 'last_name', 'email', 'password')

class PlanetSchema(ma.Schema):
    class Meta:
        fields = ('planet_id', 'planet_name', 'planet_type', 'home_star', 'mass', 'radius', 'distance')


#### Instantiating above schema
user_schema = UserSchema()
users_schema = UserSchema(many=True)

planet_schema = PlanetSchema()
planets_schema = PlanetSchema(many=True)

## Name test
if __name__ == '__main__':
    app.run()
