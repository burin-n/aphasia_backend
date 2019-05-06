import os

partition = '6'
upload_folder = os.path.join(os.getcwd(), 'cache', 'upload' + partition)
wav_folder = os.path.join(os.getcwd(), 'cache', 'wav' + partition)
log_file = os.path.join(os.getcwd(), 'decode{}.log'.format(partition))
result_file = os.path.join(os.getcwd(), 'result{}.log'.format(partition))

def create_cache_folder():
    if(not os.path.isdir(upload_folder)):
        os.makedirs(upload_folder)
    if(not os.path.isdir(wav_folder)):
        os.makedirs(wav_folder)
    

name_size = 4
empty_char = 'empty'

def secure_filename(filename):
    ext = filename.split('.')[-1]
    name = len(os.listdir(upload_folder))
    prefix = "0"*(name_size - len(str(name)))
    return prefix+ str(name) + '.' + ext

def allowed_file(file):
    if(file.split('.')[-1] in ['m4a', 'wav', 'caf']):
        return True
    else:
        return False

def get_oracle(file='text'):
    oracle = dict()
    with open(file) as f:
        for line in f:
            name = line.strip().split(' ')[0]
            word = line.strip().split(' ')[1:]
            oracle[name] = word
    return oracle


def isVow(x):
    return x in ['a','aa', 'i', 'ii', 'v', 'vv', 'u', 'uu', 'e', 'ee',
                'x', 'xx', 'o', 'oo', '@', '@@', 'q', 'qq', 
                'ia', 'iia', 'va', 'vva', 'ua', 'uua']


def isFinal(x):
    return x[-1] == '^'


def isInit(x):
    return not isVow(x) and not isFinal(x)