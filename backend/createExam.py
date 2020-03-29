import redis
import json
import os
import random
import unicodedata
import argparse
import hashlib
import logging
import warnings
warnings.filterwarnings('ignore')
from PIL import Image, ImageFont, ImageDraw 

from selenium import webdriver

def chr_width(c):
    if (unicodedata.east_asian_width(c) in ('F','W','A')):
        return 2
    else:
        return 1

def token_gen(stu_id, exam_name):
    m = hashlib.md5()
    seed = random.randint(0, 2**24)
    m.update(str(seed).encode('utf-8'))
    m.update(stu_id.encode('utf-8'))
    m.update(exam_name.encode('utf-8'))
    return m.hexdigest()

def read_json(path):
    f = open(path, "r")
    info = json.load(f)
    f.close()
    return info

def problem_gen_rawtext(id, dist, problem):
    flag = 63
    added = 0
    acc = 0
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
    options = problem['options']
    return problem['text'], options, dist

def problem_gen_markdown(id, dist, problem):
    from tempfile import NamedTemporaryFile
    import pypandoc
    import re
    name_options = []
    with open(problem) as pf:
        with NamedTemporaryFile("w") as tf:
            options = []
            for line in pf:
                if re.match(r"^- (.*)", line) is not None:
                    options.append(line)
                elif re.match(r"^# (.*)", line) is not None:
                    continue
                else:
                    tf.write(line)
            s_options = random.sample(options, len(options))
            if len(s_options) == 4:
                insert_list = ['A: ', 'B: ', 'C: ', 'D: ']
                for index, option in enumerate(s_options):
                    option = list(option)
                    option.insert(2, insert_list[index])
                    option_t = ''.join(option) + '\n'
                    tf.write(option_t)
                name_options = ['A', 'B', 'C', 'D']
            elif len(s_options) == 2:
                name_options = ['T', 'F']
            else:
                pass
            tf.flush()
            pypandoc.convert(tf.name, 'html', format='md', outputfile=dist)
            with NamedTemporaryFile("w") as html_tf:
                pypandoc.convert(tf.name, 'html', format='markdown+footnotes+pipe_tables',outputfile=html_tf.name)
                # driver.delete_all_cookies()
                driver.set_window_size(500, 300)
                driver.get(f"file:{html_tf.name}")
                scroll_height = driver.execute_script('return document.body.scrollHeight')
                scroll_width = driver.execute_script('return document.body.scrollWidth')
                driver.set_window_size(scroll_width, scroll_height+80)
                with NamedTemporaryFile() as image_tf:
                    driver.save_screenshot(image_tf.name)
                    im = Image.open(image_tf.name)
                    im = im.convert('RGBA')
                    wm_front = ImageFont.truetype('wqy-zenhei.ttc', 10)
                    wm_layer = Image.new("RGBA", im.size, (255, 255, 255, 0))
                    wm_dr = ImageDraw.Draw(wm_layer)
                    for i in range (10):
                        wm_dr.text((int(im.size[0]/10 * i), int(im.size[1]/10 * i)), str(id), font=wm_front, fill=(0,0,0,80))
                    im = Image.alpha_composite(im, wm_layer)
                    im.save(dist)
                
    return problem, name_options, dist

def problem_gen(id, dist, problem, p_type):
    if p_type == 'rawtext':
        return problem_gen_rawtext(id, dist, problem)
    else:
        return problem_gen_markdown(id, dist, problem)

def exam_gen(r, stu_id, token, dist, items, problems, p_type):
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
            if item['type'] != 'submit':
                p_id, s_problem_options, path = problem_gen(stu_id, os.path.join(dist, f"str{id}.png"), s_problem, p_type)
            if 'rand_options' in item and item['rand_options']:
                s_problem_options = random.sample(s_problem_options, len(s_problem_options))
            dist_list += [
                {
                    'id': id,
                    'type': item['type'],
                    'label':  item['label'] if 'label' in item else '',
                    'path': path if item['type'] != 'submit' else '',
                    'options': s_problem_options,
                    'multiple': item['multiple'] if 'multiple' in item else '',
                    'title': item['title'] if 'title' in item else '',
                    'body': item['body'] if 'body' in item else '',
                    'p_id': p_id
                }
            ]
            id += 1
    assert r.set(token, json.dumps({'items': dist_list}))

def md5(text):
    m = hashlib.md5()
    m.update(text.encode('utf-8'))
    return m.hexdigest()

def walk_dir(dir):
    from collections import defaultdict
    dic = defaultdict(list)
    for root, dirs, files in os.walk(dir):
        for f in files:
            dic[root].append(os.path.join(root, f))
    return dic

def main_rawtext(args):
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
        exam_gen(r, stu_id, stu_token, stu_dist, exam_info['items'], problem_set, 'rawtext')
        ori_dit = json.loads(r.get(md5(stu_id)))
        ori_dit['token'] = stu_token
        r.set(md5(stu_id), json.dumps(ori_dit))

def get_webd_option():
    option = webdriver.FirefoxOptions()
    option.add_argument('--headless')
    option.add_argument("-height=300")
    option.add_argument("-width=300")
    option.add_argument("--hide-scrollbars")
    return option

def main_markdown(args):
    stu_info = read_json(args.file)
    problem_info = read_json(args.problem)
    exam_info = read_json(args.exam)
    
    if 'problem_dir' not in problem_info:
        logging.error(f"No 'problem_dir' in {args.problem}.")
        return
    problems = walk_dir(problem_info['problem_dir'])

    for stu_id in stu_info:
        global driver
        option = get_webd_option()
        driver = webdriver.Firefox('./driver', firefox_options=option)
        stu_token = token_gen(stu_id, exam_info['name'])
        stu_dist = os.path.join(args.dist, stu_token)
        exam_gen(r, stu_id, stu_token, stu_dist, exam_info['items'], problems, 'markdown')
        driver.quit()
        ori_dit = json.loads(r.get(md5(stu_id)))
        ori_dit['token'] = stu_token
        r.set(md5(stu_id), json.dumps(ori_dit))
        
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dist", type=str, help="Dir to dump the problems for every students.")
    parser.add_argument("-f", "--file", type=str, help="Student meta data file.")
    parser.add_argument("-p", "--problem", type=str, help="Problem meta data file.")
    parser.add_argument("-e", "--exam", type=str, help="Exam meta data file.")
    parser.add_argument("-t", "--type", choices=['markdown', 'rawtext'], default='markdown', help="Problem generating backend.")
    args = parser.parse_args()

    ## Connect to Redis
    # TODO: Make redis connection configurable.
    pool = redis.ConnectionPool(host='127.0.0.1', port=6379)
    r = redis.Redis(connection_pool=pool)

    if (args.type=='rawtext'):
        main_rawtext(args)
    else:
        main_markdown(args)
    driver.quit()
