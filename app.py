import os
from flask import Flask
import sys
import urllib
from services.client import MyClient
from services.post_processing import post_processing
from services.distance_scoring import distance_scoring
from collections import Counter

scoring = distance_scoring()
post_processing = post_processing()


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
        # gstreamer_url = 'ws://161.200.194.159:10000/client/ws/speech'
        gstreamer_url = 'ws://localhost:10000/client/ws/speech'
        audiofile = '/home/burin/kaldi/egs/aphasia/s5/audios/disability/D00_004.wav'
        content_type = ''
        oracle = 'k @@ j^'.split(' ')
        byterate = 32000
        ws = MyClient(audiofile, gstreamer_url + '?%s' % (urllib.parse.urlencode([("content-type", content_type)])), byterate=byterate)
        ws.connect()
        results = ws.get_full_hyp()
        post_results = []
        
        for res in results:
            print(type(res), res)
            try:
                processed_transcript = post_processing(res['transcript'].split(' '))
            except Exception as e:
                processed_transcript= ''
                print(e)

            res['processed_transcript'] = processed_transcript
            post_results.append(res)

        initc, vow, finalc = Counter(), Counter(), Counter()
        for e in post_results:
            t_init, t_vow, t_final = e['processed_transcript']
            for x in t_init:
                initc[x] += 1
            for x in t_vow:
                vow[x] += 1
            for x in t_final:
                finalc[x] += 1

        init_cost, vow_cost, final_cost = scoring( (initc, vow, finalc), oracle )
        return "score: {} {} {}".format(1-init_cost, 1-vow_cost, 1-final_cost)

    return app