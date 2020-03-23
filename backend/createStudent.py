import redis
import json
import random
import argparse
import hashlib

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--file", type=str)
parser.add_argument("-s", "--save", action='store_true', default=True)
parser.add_argument("-c", "--clean", action='store_true', default=False)
args = parser.parse_args()

def password_gen(stu_id):
    m = hashlib.md5()
    seed = random.randint(0, 2^24)
    m.update(str(seed).encode('utf-8'))
    m.update(stu_id.encode('utf-8'))
    return m.hexdigest()

def md5(text):
    m = hashlib.md5()
    m.update(text.encode('utf-8'))
    return m.hexdigest()

## Open file
f = open(args.file, "r")
stu_info = json.load(f)
f.close()

## Connect to Redis
pool = redis.ConnectionPool(host='127.0.0.1', port=6379)
r = redis.Redis(connection_pool=pool)

## IF clean
if args.clean:
    for item in stu_info:
        r.delete(item)
## add Student Info
else:
    for item in stu_info:
        if 'password' not in stu_info[item] or stu_info[item]['password'] == "":
            stu_info[item]['password'] = password_gen(item)
        print(json.dumps({'stu_id': item, 'password': md5(stu_info[item]['password'])}))
        r.set(md5(item), json.dumps({'stu_id': item, 'password': md5(stu_info[item]['password'])}))
        print(r.get(md5(item)))
    if args.save:
        json.dump(stu_info, open(args.file, "w"))
