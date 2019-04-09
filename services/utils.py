import os

upload_folder = os.path.join(os.getcwd(), 'cache', 'upload')
wav_folder = os.path.join(os.getcwd(), 'cache', 'wav')
name_size = 4

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