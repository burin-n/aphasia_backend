import os
from flask import Flask, request, jsonify
import sys
import urllib
from services.client import MyClient
from services.post_processing import post_processing
from services.distance_scoring import distance_scoring
from collections import Counter
import time
import datetime
import services.utils as utils
from pydub import AudioSegment


scoring = distance_scoring()
post_processing = post_processing()
oracle_text = utils.get_oracle()

upload_folder = os.path.join(os.getcwd(), 'cache', 'upload')
wav_folder = os.path.join(os.getcwd(), 'cache', 'wav')



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
    def query(audiofile, oracle):
        # gstreamer_url = 'ws://161.200.194.159:10000/client/ws/speech'
        gstreamer_url = 'ws://localhost:10000/client/ws/speech'
        # audiofile = '/home/burin/kaldi/egs/aphasia/s5/audios/disability/D00_004.wav'
        # oracle = oracle.split(' ')
        
        content_type = ''
        byterate = 32000
        ws = MyClient(audiofile, gstreamer_url + '?%s' % (urllib.parse.urlencode([("content-type", content_type)])), byterate=byterate)
        ws.connect()
        while(not ws.terminated):
            time.sleep(0.5)
        print('done connect')


        results = ws.get_full_hyp()
        print('starting postprocessing...')
        # print(results)
        post_results = []

        f = open('decode.log', 'a')
        fr = open('result.log', 'a')

        datenow = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        f.write('### ' + datenow + '\n')
        f.write('* incoming ip address: ' + request.remote_addr + '\n')
        f.write('* orable: ' + ' '.join(oracle) + '\n')

        fr.write('### ' + datenow + '\n')
        fr.write('* incoming ip address: ' + request.remote_addr + '\n')
        fr.write('* orable: ' + ' '.join(oracle) + '\n')            

        # post-process each nbest
        for res in results:
            print(res)
            try:
                processed_transcript = post_processing(res['transcript'].split(' '))
                print(processed_transcript)
            except Exception as e:
                processed_transcript= ''
                print(e)

            f.write('predict: {}\n'.format(res))
            f.write('post process: {}\n'.format(processed_transcript))

            res['processed_transcript'] = processed_transcript
            post_results.append(res)
        
        # merge nbest into usable format
        initc, vow, finalc = Counter(), Counter(), Counter()
        for e in post_results:
            t_init, t_vow, t_final = e['processed_transcript']
            for x in t_init:
                initc[x] += 1
            for x in t_vow:
                vow[x] += 1
            for x in t_final:
                finalc[x] += 1

        # scoring
        init_cost, vow_cost, final_cost = scoring( (initc, vow, finalc), oracle )
        ret = {
                "_init" : round(1-init_cost,2),
                "_vow" : round(1-vow_cost, 2),
                "_final" : round(1-final_cost, 2),  
            }        

        ret_json = jsonify(
            score = ret,
            counter = {
                    "initc" : initc,
                    "vow" : vow,
                    "finalc" : finalc
                }
        )

        f.write("== Counter \n\tinitc: {}\n\tvow: {}\n\tfinalc: {}\n".format(initc, vow, finalc))
        f.write("-> initc: {} vow: {} finalc: {}\n".format(round(1-init_cost,2), round(1-vow_cost,2), round(1-final_cost,2) ))
        f.write('\n\n')
        f.close()
        fr.write("== Counter \n\tinitc: {}\n\tvow: {}\n\tfinalc: {}\n".format(initc, vow, finalc))
        fr.write("-> initc: {} vow: {} finalc: {}\n".format(round(1-init_cost,2), round(1-vow_cost,2), round(1-final_cost,2) ))
        fr.write('\n\n')
        fr.close()

        return ret_json


        # return "score: {} {} {}".format(1-init_cost, 1-vow_cost, 1-final_cost)


    @app.route('/upload', methods=['POST'])
    def upload_file():
        try:
            target = request.args.get('target')
            print(target)
            print(oracle_text[target])
        except:
            return 'error'

        if request.method == 'POST':
            # check if the post request has the file part
            # print(request.files)
            if 'file' not in request.files:
                print('###########')
                print(request.data)
                print('###########')
                return 'No file part'

            file = request.files['file']
            # if user does not select file, browser also
            # submit a empty part without filename
            if file.filename == '':
                return 'No selected file'
            if file and utils.allowed_file(file.filename):
                filename = utils.secure_filename(file.filename)
                path = os.path.join(upload_folder, filename)
                file.save(path)
                print(filename + ' is uploaded at ' + path)
                # return filename + ' is uploaded'
                converted_path = convert(path)
                
                # return converted_path
                return query(converted_path, oracle_text[target])
            
            return "nothing"

    
    def convert(filepath):
        (path, file_extension) = os.path.splitext(filepath)
        filename = path.split('/')[-1]
        file_extension_final = file_extension.replace('.', '')
        wav_path = ''
        try:
            track = AudioSegment.from_file(filepath,file_extension_final)
            
            wav_filename = filename+'.wav'
            wav_path = wav_folder + '/' + wav_filename
            
            print('CONVERTING: ' + str(filepath))
            file_handle = track.export(wav_path, format='wav')
            # os.remove(filepath)
        except Exception as error:
            print(str(error))
            print("ERROR CONVERTING " + str(filepath))
        
        return wav_path

    return app