from flask import Flask
from flask_cors import *
from controller.test_controller import testModule
from controller.webKG_controller import webKGModule
from controller.bookKG_controller import bookKGModule

app = Flask(__name__)
CORS(app, supports_credentials=True)

app.register_blueprint(testModule, url_prefix='/testModule')
app.register_blueprint(webKGModule, url_prefix='/webKG')
app.register_blueprint(bookKGModule, url_prefix='/bookKG')

@app.route('/')
def hello_world():
    return 'flask_test is running!!!'

if __name__ == '__main__':
    app.run(port=2525)