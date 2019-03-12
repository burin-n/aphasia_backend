import os
from flask import Flask
import sys
import urllib
from services.client import MyClient

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/')
    def hello():
        return 'Hello, World!'


    @app.route('/query')
    def query():
        gstreamer_url = 'ws://161.200.194.155:8080/client/ws/speech'
        audiofile = '/Users/burin/Desktop/D00_004.wav'
        content_type = ''
        byterate = 32000
        ws = MyClient(audiofile, gstreamer_url + '?%s' % (urllib.parse.urlencode([("content-type", content_type)])), byterate=byterate)
        ws.connect()
        result = ws.get_full_hyp()
        return result


    return app