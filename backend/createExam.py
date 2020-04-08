import redis
import json
import os
import re
import random
import unicodedata
import argparse
import hashlib
import logging
import warnings
warnings.filterwarnings('ignore')
from PIL import Image, ImageFont, ImageDraw 

from selenium import webdriver

### re
blank_re = re.compile(r'%{.+?}%')
option_re = re.compile(r"^- (.*)")

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

def problem_gen_markdown(id, dist, problem, p_type):
    from tempfile import NamedTemporaryFile
    import pypandoc
    name_options = []
    name_blanks = []
    standard = {}
    with open(problem) as pf:
        with NamedTemporaryFile("w") as tf:
            options = []
            option_index = 0
            blanks = []
            blank_index = 0
            value_dict = {}
            for line in pf:
                if (p_type == 'judge' or p_type == 'select'):
                    value_list = re.findall(r"%{(.+?)}%", line)
                    if len(value_list) > 0:
                        for value in value_list:
                            for key in value_dict:
                                if type(value_dict[key]) is str:
                                    value = re.sub(f"{key}", f"'{value_dict[key]}'", value)
                                else:
                                    value = re.sub(f"{key}", f"{value_dict[key]}", value)
                            value = str(eval(value))
                            line = re.sub(r"%{(.+?)}%", value, line, 1)
                if (p_type == 'judge' or p_type == 'select') and re.match(r"^- (.*)", line) is not None:
                    options.append((option_index,line))
                    option_index += 1
                elif p_type == 'text' and blank_re.search(line) is not None:
                    for item in blank_re.findall(line):
                        blanks.append(item)
                        name_blanks.append(f"<{blank_index}>")
                        line = blank_re.sub(f"[<  {blank_index}  >](0.0.0.0)", line, 1)
                        blank_index += 1
                    tf.write(line)
                elif re.match(r"^\$ (.*)", line) is not None:
                    var = re.search(r"^\$ (\S+?)(\s*?)=", line).group(1)
                    value = re.search(r"^\$(.*?)=(.*)$", line).group(2)
                    value_dict[str(var)] = random.sample(eval(value), 1)[0]
                else:
                    tf.write(line)
            s_options = random.sample(options, len(options))
            for index, (op_id, option) in enumerate(s_options):
                if op_id == 0:
                    standard['op'] = index
            standard['blank'] = blanks
            if p_type == 'select':
                insert_list = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']
                for index, (op_id, option) in enumerate(s_options):
                    option = list(option)
                    option.insert(2, chr(index+65) + ': ')
                    option_t = ''.join(option) + '\n'
                    tf.write(option_t)
                    name_options.append(insert_list[index])
            elif p_type == 'judge':
                standard['op'] = options[0]
                name_options = ['T', 'F']
            else:
                pass
            tf.flush()
            with NamedTemporaryFile("w") as html_tf:
                ori_path = os.path.dirname(os.path.realpath(__file__))
                tmp_dist = os.path.realpath(dist)
                html_path = os.path.realpath(problem) + '.html'
                css_path = os.path.realpath('temp.css')
                os.chdir(os.path.dirname(os.path.realpath(problem)))
                pypandoc.convert(tf.name, 'html5', extra_args=[f'-c {css_path}', '-s'], format='markdown', outputfile=html_path)
                # driver.delete_all_cookies()
                driver.set_window_size(600, 300)
                driver.get(f"file:{html_path}")
                scroll_height = driver.execute_script('return document.body.scrollHeight')
                scroll_width = driver.execute_script('return document.body.scrollWidth')
                driver.set_window_size(scroll_width, scroll_height+200)
                with NamedTemporaryFile() as image_tf:
                    driver.save_screenshot(image_tf.name)
                    os.chdir(ori_path)
                    im = Image.open(image_tf.name)
                    im = im.convert('RGBA')
                    wm_front = ImageFont.truetype('DejaVuSans.ttf', 15)
                    wm_layer = Image.new("RGBA", im.size, (255, 255, 255, 0))
                    wm_dr = ImageDraw.Draw(wm_layer)
                    for i in range (10):
                        wm_dr.text((int(im.size[0]/10 * i), int(im.size[1]/10 * i)), str(id), font=wm_front, fill=(0,0,0,80))
                    im = Image.alpha_composite(im, wm_layer)
                    im.save(dist)

    return problem, name_options, dist, name_blanks, standard

def problem_gen(id, dist, problem, p_type):
    return problem_gen_markdown(id, dist, problem, p_type)

def exam_gen(r, stu_id, token, dist, items, problems, p_type):
    os.makedirs(dist)
    dist_list = []
    standards_list = []
    id = 1
    for index, item in enumerate(items):
        length = item['num']
        s_problems = [{} for x in range(length)]
        if 'problem_type' in item:
            s_problems = random.sample(problems[item['problem_type']], length)
        for i, s_problem in enumerate(s_problems):
            s_problem_options = []
            blanks = []
            if item['type'] != 'submit':
                p_id, s_problem_options, path, blanks, standard = problem_gen(stu_id, os.path.join(dist, f"str{id}.png"), s_problem, item['type'])
                standards_list.append(standard)
            if 'rand_options' in item and item['rand_options']:
                s_problem_options = random.sample(s_problem_options, len(s_problem_options))
            dist_list += [
                {
                    'id': id,
                    'type': item['type'],
                    'label':  item['label'] if 'label' in item else '',
                    'path': path if item['type'] != 'submit' else '',
                    'options': s_problem_options,
                    'blanks': blanks,
                    'multiple': item['multiple'] if 'multiple' in item else '',
                    'title': item['title'] if 'title' in item else '',
                    'body': item['body'] if 'body' in item else '',
                    'p_id': p_id # won't send to student.
                }
            ]
            id += 1
    assert r.set(token, json.dumps({'items': dist_list, 'standards': standards_list}))


def md5(text):
    m = hashlib.md5()
    m.update(text.encode('utf-8'))
    return m.hexdigest()

def walk_dir(dir):
    from collections import defaultdict
    dic = defaultdict(list)
    for root, dirs, files in os.walk(dir):
        for f in files:
            if re.match(r"^(.*)\.md$", f) is not None:
                dic[root].append(os.path.join(root, f))
    return dic

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

    for index, stu_id in enumerate(stu_info):
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
        print(f"\r{index}/{len(stu_info)}")
        
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dist", type=str, help="Dir to dump the problems for every students.")
    parser.add_argument("-f", "--file", type=str, help="Student meta data file.")
    parser.add_argument("-p", "--problem", type=str, help="Problem meta data file.")
    parser.add_argument("-e", "--exam", type=str, help="Exam meta data file.")
    parser.add_argument("-A", "--redis-address", type=str, default='127.0.0.1', help='Address for redis connection.')
    parser.add_argument("-P", "--redis-port", type=int, default=6379, help='Port for redis connection.')
    parser.add_argument("-RP", "--redis-password", type=str, default=None, help='Passsword for redis connection.')
    args = parser.parse_args()

    ## Connect to Redis
    # TODO: Make redis connection configurable.
    pool = redis.ConnectionPool(
        host=args.redis_address,
        port=args.redis_port,
        password=args.redis_password
    )
    r = redis.Redis(connection_pool=pool)

    
    main_markdown(args)

