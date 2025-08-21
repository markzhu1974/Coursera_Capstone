# 🧑‍💻 Step by Step 教程：Python + SQLite + HTTP Server 学生信息管理系统

---

# 第 1 步：了解数据库和 SQL 的基本概念

---

## 什么是数据库（Database）？

* **数据库** 是用来可靠存储、管理和检索数据的软件系统或文件集合。
* 类比：把数据库想成“电子档案柜”或“更强大的 Excel”。
* 我们用 **SQLite**：它把数据库存为单个文件（例如 `student.db`），不需要单独安装数据库服务器，适合学习与小型应用。

---

## 表（Table）、行（Row）、列（Column）

* **表**：数据库中存放某类实体数据的结构（像 Excel 的一张表）。
* **列（字段）**：定义记录的属性，比如 `name`、`age`、`major`。每列有名字和数据类型/约束。
* **行（记录）**：表里的一个实体，一条学生信息就是一行。

示意 — `student` 表的结构（也就是表的每一列的含义）：

| 字段名    | 数据类型    | 说明    |
| ------ | ------- | ----- |
| id     | INTEGER | 主键，自增 |
| name   | TEXT    | 学生姓名  |
| gender | TEXT    | 性别    |
| age    | INTEGER | 年龄    |
| major  | TEXT    | 专业    |

---
## 表的数据的示例

| id | name | gender | age | major |
| -- | ---- | ------ | --- | ----- |
| 1  | 张三   | 男      | 20  | 计算机科学 |
| 2  | 李四   | 女      | 21  | 电气工程  |
| 3  | 王五   | 男      | 19  | 机械工程  |
| 4  | 赵六   | 女      | 22  | 信息管理  |
| 5  | 陈七   | 男      | 23  | 软件工程  |

---

## 主键（Primary Key）与唯一性

* **主键** 用来唯一标识每条记录（例如 `id`）。
* 好处：保证记录可被准确定位（更新、删除、引用）。
* 在 SQLite 中常用 `INTEGER PRIMARY KEY AUTOINCREMENT` 来自动生成 `id`。

---

## 数据类型（以 SQLite 为例）

SQLite 对类型的处理比较宽松（类型亲和性），但常见约定如下：

* `INTEGER`：整数（年龄、ID）
* `TEXT`：文本（姓名、专业）
* `REAL`：浮点数（若有金额、分数）
* `BLOB`：二进制数据（文件、图片）
* SQLite 的特点：即使声明了类型，也可能在同一列存入不同类型的数据（要养成规范写法）。

---

## 常用约束（Constraints）

就是对表的某一个列的要求，在创建表的时候使用

* `NOT NULL`：该列不能为空。
* `UNIQUE`：值不能重复。
* `DEFAULT`：缺省值。
* `CHECK(...)`：自定义校验条件（例如 `CHECK(age > 0)`）。
* `FOREIGN KEY`：外键（用于跨表关联）。
  在我们的简单学生表中常见：`id` 主键、`name NOT NULL` 等。

---

## CRUD：四类基本操作

* **Create（创建）**：`INSERT INTO` —— 插入新记录。
* **Read（读取）**：`SELECT` —— 查询数据。
* **Update（更新）**：`UPDATE` —— 修改记录。
* **Delete（删除）**：`DELETE` —— 删除记录。

---

## 常见 SQL 语句示例（针对 student 表）

1. **创建表**

```sql
CREATE TABLE IF NOT EXISTS student (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    gender TEXT NOT NULL,
    age INTEGER NOT NULL,
    major TEXT NOT NULL
);
```

说明：`IF NOT EXISTS` 避免重复创建；`AUTOINCREMENT` 自动递增 id。

2. **插入数据**

```sql
INSERT INTO student (name, gender, age, major)
VALUES ('张三', '男', 20, '机械工程');
```

3. **查询所有**

```sql
SELECT * FROM student;
```

4. **带条件查询**

```sql
SELECT id, name, age FROM student WHERE age > 21 ORDER BY age DESC LIMIT 10;
```

解释：查出年龄 >21 的前 10 条，按年龄降序排列。

5. **更新记录**

```sql
UPDATE student SET major = '计算机科学' WHERE id = 1;
```

6. **删除记录**

```sql
DELETE FROM student WHERE id = 3;
```

---

## SQL 的筛选、排序与分页（常用子句）

* `WHERE`：添加筛选条件（支持比较、逻辑运算符）。
* `ORDER BY`：排序（`ASC` / `DESC`）。
* `LIMIT`（SQLite 支持）+ `OFFSET`：分页。
* `GROUP BY` / `HAVING`：分组统计（本练习暂不深入）。

---

## 事务（Transaction）

* 事务是一组要么全部成功要么全部失败的操作单位。
* 在 Python + sqlite3 中，`conn.commit()` 提交事务，`conn.rollback()` 回滚。
* 例如插入多条关键数据时，发生异常应回滚以保持数据一致性。

Python 示例：

```python
import sqlite3

conn = sqlite3.connect('student.db')
try:
    cursor = conn.cursor()
    # 插入三条学生信息
    cursor.execute("INSERT INTO student (name, gender, age, major) VALUES (?, ?, ?, ?)",
                   ('李四', '女', 22, '电子工程'))
    cursor.execute("INSERT INTO student (name, gender, age, major) VALUES (?, ?, ?, ?)",
                   ('王五', '男', 21, '计算机科学'))
    cursor.execute("INSERT INTO student (name, gender, age, major) VALUES (?, ?, ?, ?)",
                   ('赵六', '女', 23, '机械工程'))

    # 如果三条都成功，提交事务
    conn.commit()
    print("三条记录插入成功！")

except Exception as e:
    # 如果有任何一条失败，回滚事务
    conn.rollback()
    print("插入失败，事务已回滚：", e)

finally:
    conn.close()
```

注意：使用参数化查询（上例中的 `?` 占位符）可以 **防止 SQL 注入**，并正确处理字符串转义。

---

## 索引（Index）

* 索引提高查询速度（类似书的目录），但会占用空间并稍慢写入。
* 示例：如果常按 `age` 或 `name` 查询，可以建索引：

```sql
CREATE INDEX IF NOT EXISTS idx_student_age ON student(age);
```

* 对于小型练习项目，索引不是必要的；了解即可。

---

## 关系型数据库基础与规范化（简单说明）

* 关系型数据库以表相互关联来建模复杂数据（本项目是单表，关系较少）。
* **范式（Normalization）**：用来减少冗余与更新异常。

  * 1NF：每个字段原子化（不要把多个值塞在同一列）。
  * 2NF/3NF：消除部分依赖、传递依赖（更适合多表设计）。
* 练习项目中只用一张 `student` 表，后续若需记录课程、成绩，可把课程抽成另一张表并用外键关联。

---

## SQLite 的一些特性提醒

* SQLite 文件就是数据库（备份就是复制 `.db` 文件）。
* SQLite 没有严格的数据类型限制（类型亲和性），但仍建议按常规声明类型。
* `AUTOINCREMENT` 在 SQLite 下不是总必要（`INTEGER PRIMARY KEY` 本身会自动分配 rowid），但保留能保证 id 不重用（在某些极端场景）。

---

## 在命令行查看数据库（sqlite3 CLI）

如果你安装了 sqlite3 命令行工具，可以这样做：

```bash
sqlite3 student.db
-- 进到 sqlite 命令行后：
.tables          -- 显示表
.schema student  -- 显示表结构
SELECT * FROM student;  -- 查询
.exit
```

---

## 常见错误与最佳实践

* **忘记 `conn.commit()`**：插入或更新后看不到变化 → 一定要提交或使用 `with` 语句管理连接。
* **不关闭连接**：资源泄露，最好在 `finally` 中 `conn.close()` 或使用 `with sqlite3.connect(...) as conn:`。
* **字符串拼接拼 SQL（危险！）**：容易遭受 SQL 注入，务必用参数化查询（`?` 占位符或命名占位符）。
* **输入校验**：不要完全信任前端输入（类型、长度、合法性都应在后端校验）。
* **备份数据库**：定期复制 `.db` 文件作为备份。

---

## 与本项目相关的 Python 操作示例（参数化查询 + 查询展示）

插入（参数化）：

```python
def add_student(name, gender, age, major):
    conn = sqlite3.connect('student.db')
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO student (name, gender, age, major) VALUES (?, ?, ?, ?)",
            (name, gender, age, major)
        )
        conn.commit()
    finally:
        conn.close()
```

读取并打印（简单示例）：

```python
def list_students():
    conn = sqlite3.connect('student.db')
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, gender, age, major FROM student")
        rows = cursor.fetchall()
        for r in rows:
            print(r)  # (id, name, gender, age, major)
    finally:
        conn.close()
```

---

## 小练习（Practice）

1. 写一条 SQL，查出 **专业为“计算机科学”且年龄 ≤ 22** 的学生。
   答案示例：

   ```sql
   SELECT * FROM student WHERE major = '计算机科学' AND age <= 22;
   ```

2. 写一条 SQL，把 id=2 的学生专业改为“自动化”。
   答案示例：

   ```sql
   UPDATE student SET major = '自动化' WHERE id = 2;
   ```

3. 在 Python 中如何避免 SQL 注入？写出插入语句的正确写法（参数化）。
   答案示例见上面的 `add_student` 函数（使用 `?` 占位符）。

---

## 小结

* 熟悉**表/行/列/主键/数据类型/约束**是数据库入门关键。
* 多练习 `CREATE`、`INSERT`、`SELECT`、`UPDATE`、`DELETE` 与 `WHERE/ORDER BY/LIMIT`。
* 在 Python 中**始终使用参数化查询**并管理好连接与事务。
* SQLite 简单易用、适合本练习场景；但在大型生产环境中，可能会用到 MySQL、Postgres 或其他 DBMS，概念是共通的。

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
