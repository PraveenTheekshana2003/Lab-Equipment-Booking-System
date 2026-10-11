from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lab.db'


@app.route('/')
def index():
    return 'Lab Equipment Booking System API'


if __name__ == '__main__':
    app.run(debug=True)