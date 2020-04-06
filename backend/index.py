from flask import Flask, request
import json
from flask_redis import FlaskRedis
import logging

app = Flask(__name__)

app.config['REDIS_URL']='redis://:@localhost:6379/'
app.debug = True

redis_store = FlaskRedis(app)

def ip_check(request, dic):
    """
    Args:
        request: The request from flask api.
        dic: The state dict from redis.
    Return:
        True: the ip address is the same as the orginal one. 
        False: the ip address is changed.
    """
    if 'ip' not in dic:
        return False
    elif dic['ip'][-1] == request.headers['X-Real-Ip']:
        return True
    else:
        return False

def keywords_check(keys, data):
    for key in keys:
        if key not in data:
            return False
    return True


@app.route('/app/login',methods = ['POST'])
def login():
    data = {}
    if request.content_type.startswith('application/json'):
        data = request.get_data()
        data = json.loads(data)
    else:
        for key, value in request.form.items():
            if key.endswith('[]'):
                data[key[:-2]] = request.form.getlist(key)
            else:
                data[key] = value
    res = redis_store.get(data['id'])
    if res is None:
        return {'code': 1, "message": "用户名错误"}
    dic = json.loads(res)
    if dic['password'] != data['password']:
        return {'code': 2, "message": "密码错误"}
    if 'token' in dic:
        return {'code':0, 'path':dic['token']}
    else:
        return {'code': 3, "message": "密码错误"}

@app.route('/app/exam',methods = ['POST'])
def exam():
    data = {}
    if request.content_type.startswith('application/json'):
        data = request.get_data()
        data = json.loads(data)
    else:
        for key, value in request.form.items():
            if key.endswith('[]'):
                data[key[:-2]] = request.form.getlist(key)
            else:
                data[key] = value
    if not keywords_check(['token', 'id'], data):
        app.logger.warning(f"Error Access from {request.headers['X-Real-Ip']}: {data}")
        return {'code':4, 'message': "提交的信息不全。"}
    res = redis_store.get(data['token'])
    stu_id_md5 = data['id']
    if res is None:
        return {'code': 5, "message": "用户未被授权访问"}
    token_res = json.loads(redis_store.get(stu_id_md5))
    if token_res is None or 'token' not in token_res or data['token'] != token_res['token']:
        return {'code': 6, "message": "用户无法参加当前考试"}
    dic = json.loads(res)
    print(dic['standards'])
    if 'items' not in dic:
        return {'code':7, 'message': "用户未被授权当前考试"}
    for item in dic['items']:
        if 'p_id' in item:
            item['p_id'] = '*'
    if 'answers' in dic:
        answers = dic['answers']
    else:
        answers = {}
    return {'code':0, 'items':dic['items'], 'answers': answers}

@app.route('/app/submit',methods = ['POST'])
def submit():
    data = {}
    if request.content_type.startswith('application/json'):
        data = request.get_data()
        data = json.loads(data)
    else:
        for key, value in request.form.items():
            if key.endswith('[]'):
                data[key[:-2]] = request.form.getlist(key)
            else:
                data[key] = value
    if not keywords_check(['token', 'id', 'answers'], data):
        app.logger.warning(f"[Error Access] {request.headers['X-Real-Ip']}: {data}")
        return {'code':8, 'message': "提交的信息不全。"}
    res = redis_store.get(data['token'])
    stu_id_md5 = data['id']
    if res is None:
        app.logger.warning(f"[Error Access] {request.headers['X-Real-Ip']}: {data}")
        return {'code': 9, "message": "用户未被授权访问"}
    token_res = json.loads(redis_store.get(stu_id_md5))
    if token_res is None or 'token' not in token_res or data['token'] != token_res['token']:
        return {'code': 10, "message": "用户无法参加当前考试"}
    stu_id = token_res['stu_id']
    dic = json.loads(res)
    if not ip_check(request, dic):
        if 'ip' not in dic:
            dic['ip'] = []
        else:
            warning_info = f"[IP Switch] {stu_id} from {dic['ip'][-1]} to {request.headers['X-Real-Ip']}"      
            app.logger.warning(warning_info)
        dic['ip'].append(request.headers['X-Real-Ip'])

    dic['answers'] = data['answers']
    ret = redis_store.set(data['token'], json.dumps(dic) )
    if (ret):
        return {'code':0, 'message': ret}
    else:
        app.logger.error(f"Student: {stu_id}; Data: {data}")
        return {'code':11, 'message': "写入数据库失败，请联系助教。"}

if __name__=="__main__":
    app.run()

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.access')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)