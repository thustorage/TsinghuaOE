import redis
import json
import os
import random
import unicodedata
import argparse
import hashlib
from PIL import Image, ImageFont, ImageDraw 

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--dist", type=str, help="Dir to dump the problems for every students.")
parser.add_argument("-f", "--file", type=str, help="Student meta data file.")
parser.add_argument("-p", "--problem", type=str, help="Problem meta data file.")
parser.add_argument("-e", "--exam", type=str, help="Exam meta data file.")
args = parser.parse_args()

pool = redis.ConnectionPool(host='127.0.0.1', port=6379)
r = redis.Redis(connection_pool=pool)

def chr_width(c):
    if (unicodedata.east_asian_width(c) in ('F','W','A')):
        return 2
    else:
        return 1

def token_gen(stu_id, exam_name):
    m = hashlib.md5()
    seed = random.randint(0, 2^24)
    m.update(str(seed).encode('utf-8'))
    m.update(stu_id.encode('utf-8'))
    m.update(exam_name.encode('utf-8'))
    return m.hexdigest()

def read_json(path):
    f = open(path, "r")
    info = json.load(f)
    f.close()
    return info

def problem_gen(id, dist, problem):
    flag = 63
    added = 0
    acc = 0
    if 'text' not in problem:
         return '' 
    text = list(problem['text'])
    for i, t in enumerate(text):
        acc += chr_width(t)
        if t == '\n':
            acc = 0
        if (acc) % flag <= 1 and i > 1 and acc > 1:
            text.insert((i+added), '\n')
            added += 1
            acc = 0
    text = ''.join(text)
    fontSize = 20
    lines = text.split('\n')
    im = Image.new("RGB", (650, len(lines)*(fontSize+5)), (255, 255, 255))
    dr = ImageDraw.Draw(im)
    font = ImageFont.truetype('wqy-zenhei.ttc', fontSize)
    dr.text((0, 0), text, font=font, fill="#000000")
    im = im.convert('RGBA')

    wm_front = ImageFont.truetype('wqy-zenhei.ttc', int(fontSize/3))
    wm_layer = Image.new("RGBA", im.size, (255, 255, 255, 0))
    wm_dr = ImageDraw.Draw(wm_layer)
    wm_dr.text((int(im.size[0]/2), int(fontSize/2)), str(id), font=font, fill=(0,0,0,80))

    im = Image.alpha_composite(im, wm_layer)
    im.save(dist)
    return dist

def exam_gen(r, stu_id, token, dist, items, problems):
    os.makedirs(dist)
    dist_list = []
    id = 1
    for index, item in enumerate(items):
        length = item['num']
        s_problems = [{} for x in range(length)]
        if 'problem_type' in item:
            s_problems = random.sample(problems[item['problem_type']], length)
        for i, s_problem in enumerate(s_problems):
            s_problem_options = []
            if 'options' in s_problem:
                print(s_problem)
                s_problem_options = s_problem['options']
            if 'rand_options' in item and item['rand_options']:
                s_problem_options = random.sample(s_problem_options, len(s_problem_options))
            dist_list += [
                {
                    'id': id,
                    'type': item['type'],
                    'label':  item['label'] if 'label' in item else '',
                    'path': problem_gen(stu_id, os.path.join(dist, f"str{id}.png"), s_problem),
                    'options': s_problem_options if 'options' in s_problem else [],
                    'multiple': item['multiple'] if 'multiple' in item else '',
                    'title': item['title'] if 'title' in item else '',
                    'body': item['body'] if 'body' in item else ''
                }
            ]

            id += 1
    print(dist_list)
    assert r.set(token, json.dumps({'items': dist_list}))

def md5(text):
    m = hashlib.md5()
    m.update(text.encode('utf-8'))
    return m.hexdigest()

stu_info = read_json(args.file)
problem_info = read_json(args.problem)
exam_info = read_json(args.exam)

problem_set = {}
for index in problem_info:
    problem_set_path = problem_info[index]
    problem_list = []
    for path in problem_set_path:
        problem_list += [read_json(path)]
    problem_set[index] = problem_list

for stu_id in stu_info:
    stu_token = token_gen(stu_id, exam_info['name'])
    stu_dist = os.path.join(args.dist, stu_token)
    exam_gen(r, stu_id, stu_token, stu_dist, exam_info['items'], problem_set)
    ori_dit = json.loads(r.get(md5(stu_id)))
    ori_dit['token'] = stu_token
    r.set(md5(stu_id), json.dumps(ori_dit))
    print(r.get(md5(stu_id)))


# template = {
#     'id': 'bc75782a480fd7edcfe3ea7f65fb9a19',
#     'password': '61e32b0f0aebe08825b25346dc5ae962',
#     'token': '61e32b0f0aebe08825b25346dc5ae962'}
# r.set('bc75782a480fd7edcfe3ea7f65fb9a19', json.dumps(template))
# 
# exam_for_id = {
#     'items': [
#         {'id':1,
#          'label': "多项选择答案",
#          'type': "select",
#          'path': '',
#          'options': ["Option A","Option B","Option C","Option D"],
#          'multiple': True,
#         },
#         {'id':2,
#          'type': "select",
#          'label': "单项选择答案",
#          'path': '',
#          'options': ["Option A","Option B","Option C","Option D"],
#          'multiple': False
#         },
#         {'id':3,
#          'type': "text",
#          'body': "test2",
#          'path': ''
#         },
#         {'id':4,
#          'type': "submit",
#          'title': "提交",
#          'body':"请确认所有题目已经完成作答。"
#         }
#       ]
# }
# r.set('61e32b0f0aebe08825b25346dc5ae962', json.dumps(exam_for_id))
# print(json.dumps(exam_for_id))
# print(json.loads(r.get('61e32b0f0aebe08825b25346dc5ae962')))

