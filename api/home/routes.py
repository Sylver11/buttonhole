from api.home import bp as home
from flask import render_template

@home.route('/', methods=['GET'])
def index():
    #raise Exception('Hello, World!'):
    return render_template('home_bp/index.html')


@home.route('/time')
def get_current_time():
    import time
    return {'time': time.time()}
