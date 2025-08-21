# 🧑‍💻 Step by Step 教程：Python + SQLite + HTTP Server 学生信息管理系统

---

## 第 1 步：了解数据库和SQL的基本概念

1. **数据库（Database）**

   * 就像一个电子版的 Excel 表格，用来存储和管理数据。
   * 我们要存的是 **学生信息**。

2. **表（Table）**

   * 就像 Excel 的一张表。
   * 每一行是一条记录（学生）。
   * 每一列是一个字段（姓名、性别、年龄、专业）。

3. **SQL（结构化查询语言）**

   * 用来操作数据库的语言。
   * 常见语句：

     * `CREATE TABLE` 创建表
     * `INSERT INTO` 插入数据
     * `SELECT` 查询数据

---

## 第 2 步：用 SQLite 创建数据库和表

SQLite 是一个轻量级数据库，不需要安装服务器，直接用文件存储。

👉 新建一个文件 `init_db.py`：

```python
import sqlite3  # 导入sqlite模块

# 1. 连接数据库（如果没有会自动创建 student.db）
conn = sqlite3.connect('student.db')

# 2. 创建一个游标（相当于指针，用来执行SQL语句）
cursor = conn.cursor()

# 3. 创建表 student（如果不存在就创建）
cursor.execute('''
CREATE TABLE IF NOT EXISTS student (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- 自动生成的ID
    name TEXT NOT NULL,                     -- 姓名
    gender TEXT NOT NULL,                   -- 性别
    age INTEGER NOT NULL,                   -- 年龄
    major TEXT NOT NULL                     -- 专业
)
''')

print("数据库和表已创建！")

# 4. 提交事务并关闭连接
conn.commit()
conn.close()
```

运行一次：

```bash
python init_db.py
```

你会看到提示“数据库和表已创建！”，并且目录下多了一个 `student.db` 文件。

---

## 第 3 步：准备前端页面

新建一个目录 `static`，在里面放一个 `index.html`：

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>学生信息管理</title>
</head>
<body>
    <h2>添加学生信息</h2>
    <form method="POST" action="/add">
        姓名: <input type="text" name="name"><br>
        性别: <input type="text" name="gender"><br>
        年龄: <input type="number" name="age"><br>
        专业: <input type="text" name="major"><br>
        <input type="submit" value="提交">
    </form>

    <h2>学生列表</h2>
    <div id="student-list">
        <!-- 学生表格会在这里显示 -->
    </div>
</body>
</html>
```

---

## 第 4 步：用 Python HTTP Server 搭建后端

新建 `server.py`：

```python
from http.server import SimpleHTTPRequestHandler, HTTPServer
import urllib.parse
import sqlite3
import os

class StudentHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            # 返回首页
            with open('static/index.html', 'r', encoding='utf-8') as f:
                content = f.read()
            # 在页面插入学生表格
            table_html = self.get_students_table()
            content = content.replace('<div id="student-list">', '<div id="student-list">' + table_html)
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == '/add':
            # 获取表单数据
            length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(length).decode('utf-8')
            params = urllib.parse.parse_qs(post_data)

            name = params.get('name', [''])[0]
            gender = params.get('gender', [''])[0]
            age = params.get('age', [''])[0]
            major = params.get('major', [''])[0]

            # 插入到数据库
            conn = sqlite3.connect('student.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO student (name, gender, age, major) VALUES (?, ?, ?, ?)",
                           (name, gender, age, major))
            conn.commit()
            conn.close()

            # 插入完成后，重定向到首页
            self.send_response(303)
            self.send_header('Location', '/')
            self.end_headers()

    def get_students_table(self):
        # 从数据库获取所有学生信息
        conn = sqlite3.connect('student.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, gender, age, major FROM student")
        rows = cursor.fetchall()
        conn.close()

        # 拼接成HTML表格
        table = "<table border='1'><tr><th>ID</th><th>姓名</th><th>性别</th><th>年龄</th><th>专业</th></tr>"
        for row in rows:
            table += f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td></tr>"
        table += "</table>"
        return table

if __name__ == '__main__':
    server = HTTPServer(('localhost', 8000), StudentHandler)
    print("服务器启动，打开 http://localhost:8000")
    server.serve_forever()
```

运行：

```bash
python server.py
```

浏览器打开：
👉 [http://localhost:8000](http://localhost:8000)

你可以 **添加学生信息**，然后会看到下面的 **表格显示所有学生**。

---

## 第 5 步：学员练习

1. 添加几个学生，验证是否能显示。
2. 修改 `index.html`，把表单里的性别换成 `<select>` 下拉框（"男" / "女"）。
3. 修改 `get_students_table`，在表格里增加一个“序号”列，从 1 开始编号。

---

✅ 到这里，我们就完成了一个最小可运行的 **学生信息管理系统**：

* 学会了 **数据库/表/SQL** 的基本概念。
* 用 Python + SQLite 建表、插入、查询。
* 用 HTTP Server 处理表单请求。
* 在网页上添加和显示学生信息。

---

要不要我帮你把这个教程再整理成 **分阶段的教学手册**（比如“第1天：数据库基础”，“第2天：HTTP Server”，“第3天：整合”）方便学员分天练习？
