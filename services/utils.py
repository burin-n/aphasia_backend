def secure_filename(filename):
    return filename

def allowed_file(file):
    return True

def get_oracle(file='text'):
    oracle = dict()
    with open(file) as f:
        for line in f:
            name = line.strip().split(' ')[0]
            word = line.strip().split(' ')[1:]
            oracle[name] = word
    return oracle