# Online Exam @TsinghuaStorage


## 快速开始
### 前端配置
前端基于Vue开发，采用常规的web-package安装即可。
#### 安装依赖
```
npm install
```
#### 部署
```
npm run build
```
本命令将在本目录下生成`./dist`，请将`80`端口解析至`./dist`。

### 后端配置

#### 依赖
以Ubuntu18.04为例。

| type | name |
| --- | --- |
| bin | redis, pandoc, firefox |
| python pkg | pillow, flask, flask-redis, pypandoc, gunicorn |

#### 运行环境
- redis在运行状态。
- `./backend/driver`（建议为绝对路径）在PATH中。

#### 添加学生
请参考`./backend/stu.json`描述文件。在将学生添加至数据库前，需要按照格式编写学生的学号，密码（`password`）为可选项，如无预设密码则将自动生成密码并保存至原文件中。

将学生添加至redis数据库中：
```
cd ./backend
python createStudent.py -f stu.json
```

如需更多帮助：
```
cd ./backend
python createStudent.py -h
```

#### 添加题目
请参考`./backend/problems.json`以及`./backend/problems`文件夹下的题目描述文件。

#### 添加考试
请参考`./backend/exam.json`描述文件。
```
cd ./backend
python createExam.py -d midterm -f s.json -p problems.json -e exam.json
```
本命令将在`./backend/`目录下生成`./midterm`（由`-d`配置），请将`80`端口的`{url}/midterm`的网络访问解析至`.midterm`。

如需更多帮助。
```
cd ./backend
python createExam.py -h
```

#### 部署后端服务器
```
cd ./backend
gunicorn --access-logfile acc.log --error-logfile err.log --log-level info -w4 -b0.0.0.0:5000 index:app
```
`acc.log`中包含IP地址变化检测记录（标记为`[IP Switch]`）。

*注意：*
`./backend/index.py`中的`REDIS_URL`需要视情况修改。

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