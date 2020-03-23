# Naive Exam System

## 前端配置
前端基于Vue开发，采用常规的web-package安装即可。
```
npm install
```

### 开发环境
```
npm run serve
```

### 部署
```
npm run build
```
本命令将在本目录下生成`./dist`，请将`80`端口解析至`./dist`。

## 后端配置
安装依赖包。
```
apt install ttf-wqy-zenhei
apt install redis
pip install pillow
pip install flask
pip install flask-redis
```
运行redis。
```
redis
```
### 添加学生
请参考`./backend/stu.json`描述文件。在将学生添加至数据库前，需要按照格式编写学生的学号，密码（`password`）为可选项，如无则将自动生成。
```
python createStudent.py -f stu.json
```


如需更多帮助。
```
python createStudent.py -h
```

### 添加题目
请参考`./backend/problems.json`以及`./backend/problems`文件夹下的题目描述文件。
### 添加考试
请参考`./backend/exam.json`描述文件。
```
python createExam.py -d midterm -f s.json -p problems.json -e exam.json
```
本命令将在`./backend/`目录下生成`./midterm`（由`-d`配置），请将`80`端口解析至`.midterm`。

如需更多帮助。
```
python createExam.py -h
```

### 部署后端服务器
```
gunicorn -w4 -b0.0.0.0:5000 index:app
```

##　可供参考的Nginx配置文件
```
....
        location / {
                # First attempt to serve request as file, then
                # as directory, then fall back to displaying a 404.
                try_files $uri $uri/ =404;
                root /home/ubuntu/develop/exam/dist;
        }

        location /app {
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Real-Port $remote_port;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

                proxy_pass http://127.0.0.1:5000;
        }
        location /midterm {
                alias /home/ubuntu/develop/exam/backend/midterm;
        }
......
```