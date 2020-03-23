from flask import Flask, request
import json
from flask_redis import FlaskRedis

app = Flask(__name__)

app.config['REDIS_URL']='redis://:@localhost:6379/'
app.debug = True

redis_store = FlaskRedis(app)

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
        return {'code': 1, "message": "Wrong id."}
    dic = json.loads(res)
    if dic['password'] != data['password']:
        return {'code': 2, "message": "Wrong password."}
    if 'token' in dic:
        return {'code':0, 'path':dic['token']}
    else:
        return {'code': 3, "message": "Wrong password."}

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
    res = redis_store.get(data['token'])
    if res is None:
        return {'code': 1, "message": "用户未被授权访问"}
    dic = json.loads(res)
    if 'items' not in dic:
        return {'code':2, 'message': "用户未被授权当前考试"}
    return {'code':0, 'items':dic['items']}

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
    res = redis_store.get(data['token'])
    if res is None:
        return {'code': 3, "message": "用户未被授权访问"}
    dic = json.loads(res)
    dic['answers'] = data['answers']
    ret = redis_store.set(data['token'], json.dumps(dic) )
    if (ret):
        return {'code':0, 'ret': ret}
    else :
        return {'code':5, 'ret': "写入数据库失败，请联系助教。"}

if __name__=="__main__":
    app.run()