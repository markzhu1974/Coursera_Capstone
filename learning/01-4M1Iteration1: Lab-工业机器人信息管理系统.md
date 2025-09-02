# 工业机器人信息管理系统教程

本教程的学习分成3个里程碑：

* 里程碑 1： 工业机器人信息的管理
* 里程碑 2： 工业机器人的维修维护记录管理
* 里程碑 3： DeepSeek工业机器人智能维修助手


# 工业机器人信息管理系统 - Milestone 1 教学教程

在第一个里程碑的教学，将通过4个迭代步骤，从零开始完成机器人基础信息的增删改查功能。

* 迭代1：完成数据库的准备和机器人数据显示
* 迭代2：完成机器人信息创建功能
* 迭代3：完成机器人信息修改功能
* 迭代4：完成机器人信息查询和删除功能

# 迭代1：完成数据库的准备和机器人数据显示

### 第一步：创建项目结构
```
robot_management/
├── server.py          # Python后端服务器
├── database.py        # 数据库操作模块
├── static/
│   ├── index.html    # 主页面
│   ├── style.css     # 样式文件
│   └── script.js     # JavaScript功能
└── robots.db          # SQLite数据库(自动生成)
```

### 第二步：创建数据库和表结构

**database.py**
```python
import sqlite3
import os

# 初始化数据库函数
def init_database():
    # 连接SQLite数据库（如果不存在会自动创建）
    conn = sqlite3.connect('robots.db')
    # 创建游标对象用于执行SQL语句
    cursor = conn.cursor()
    
    # 创建机器人信息表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS robots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_id TEXT NOT NULL UNIQUE,
        model TEXT NOT NULL,
        manufacturer TEXT NOT NULL,
        location TEXT NOT NULL
    )
    ''')
    
    # 提交事务
    conn.commit()
    # 关闭数据库连接
    conn.close()

# 插入一些示例数据
def insert_sample_data():
    conn = sqlite3.connect('robots.db')
    cursor = conn.cursor()
    
    # 示例数据
    sample_robots = [
        ('WRB-001', 'FANUC ARCMate 120iC', 'FANUC', '装配线A'),
        ('WRB-002', 'ABB IRB 2600', 'ABB', '焊接站B'),
        ('WRB-003', 'KUKA KR 10 R1420', 'KUKA', '焊接站B'),
        ('WRB-004', 'Yaskawa MA1440', 'Yaskawa', '装配线A'),
        ('WRB-005', 'FANUC ARCMate 120iC', 'FANUC', '焊接站B'),
        ('WRB-006', 'OTC FD-B4', 'OTC', '包装区C'),
        ('WRB-007', 'Panasonic TA-1400', 'Panasonic', '焊接站B'),
        ('WRB-008', 'FANUC M-10iD/12', 'FANUC', '装配线A'),
        ('WRB-009', 'KUKA KR 6 R700', 'KUKA', '焊接站B'),
        ('WRB-010', 'ABB IRB 1600', 'ABB', '包装区C')
    ]
    
    
    # 插入示例数据
    cursor.executemany(
        'INSERT OR IGNORE INTO robots (device_id, model, manufacturer, location) VALUES (?, ?, ?, ?)',
        sample_robots
    )
    
    conn.commit()
    conn.close()

# 获取所有机器人信息
def get_all_robots():
    conn = sqlite3.connect('robots.db')
    cursor = conn.cursor()
    
    # 查询所有机器人数据
    cursor.execute('SELECT id, device_id, model, manufacturer, location FROM robots')
    robots = cursor.fetchall()
    
    conn.close()
    return robots

# 程序入口点
if __name__ == '__main__':
    # 初始化数据库
    init_database()
    # 插入示例数据
    insert_sample_data()
    print("数据库初始化完成并已添加示例数据")
```
#### 在VS Code中打开database.py 并且点击右上角的Run三角按钮，或者在终端当前项目的目录下执行：python database.py，即可运行创建数据库的程序。执行完成后，可以看到生成了robots.db文件

#### 在VS Code的扩展插件中搜索“SQLite3 Editor”并且安装。安装完成后，在VS Code中点击robots.db文件，就可以打开数据库图形界面，看到插入的数据

### 第三步：创建Python HTTP服务器

**server.py**
```python
import http.server
import socketserver
import json
import database
import os  # 导入os模块用于路径操作

# 定义服务器端口
PORT = 8000

# 自定义请求处理类，继承自SimpleHTTPRequestHandler
class RobotHandler(http.server.SimpleHTTPRequestHandler):
    # 设置CORS头，允许跨域请求
    def set_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
    
    # 处理OPTIONS预检请求
    def do_OPTIONS(self):
        self.send_response(200)
        self.set_cors_headers()
        self.end_headers()
    
    # 重写do_GET方法以处理默认页面重定向
    def do_GET(self):
        # 如果请求根路径"/"，重定向到static/index.html
        if self.path == '/':
            self.send_response(302)  # 302重定向状态码
            self.send_header('Location', '/static/index.html')
            self.end_headers()
            return
        
        # 如果请求路径是/api/robots，返回机器人列表
        if self.path == '/api/robots':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.set_cors_headers()
            self.end_headers()
            
            # 从数据库获取所有机器人
            robots = database.get_all_robots()
            # 将数据转换为字典列表
            robots_list = []
            for robot in robots:
                robots_list.append({
                    'id': robot[0],
                    'device_id': robot[1],
                    'model': robot[2],
                    'manufacturer': robot[3],
                    'location': robot[4]
                })
            
            # 返回JSON格式的响应
            self.wfile.write(json.dumps(robots_list).encode())
        else:
            # 对于其他请求，使用默认的静态文件服务
            # 设置静态文件目录为当前目录
            self.directory = os.getcwd()
            super().do_GET()

# 程序入口点
if __name__ == '__main__':
    # 初始化数据库
    database.init_database()
    database.insert_sample_data()
    
    # 创建 HTTPServer
    server = http.server.HTTPServer(('', PORT), RobotHandler)
    print(f"服务器运行在端口 {PORT}")
    print("打开浏览器访问: http://localhost:8000/")
    # 启动服务器，持续处理请求
    server.serve_forever()
```

### 第四步：创建前端页面

**static/index.html**
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>工业机器人信息管理系统</title>
    <!-- 引入样式文件 -->
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>工业机器人信息管理系统</h1>
        </header>
        
        <main>
            <!-- 查询区域 -->
            <section class="search-section">
                <h2>查询条件</h2>
                <div class="search-form">
                    <input type="text" id="searchInput" placeholder="输入设备编号或型号搜索">
                    <button onclick="searchRobots()">查询</button>
                </div>
            </section>
            
            <!-- 机器人列表 -->
            <section class="robot-list">
                <h2>机器人列表</h2>
                <table id="robotTable">
                    <thead>
                        <tr>
                            <th>选择</th>
                            <th>设备编号</th>
                            <th>型号</th>
                            <th>生产厂家</th>
                            <th>位置</th>
                        </tr>
                    </thead>
                    <tbody>
                        <!-- 机器人数据将通过JavaScript动态填充 -->
                    </tbody>
                </table>
            </section>
            
            <!-- 操作按钮 -->
            <section class="action-buttons">
                <button onclick="addRobot()">新增</button>
                <button onclick="editRobot()">修改</button>
                <button onclick="deleteRobot()">删除</button>
            </section>
        </main>
    </div>
    
    <!-- 引入JavaScript文件 -->
    <script src="script.js"></script>
</body>
</html>
```

**static/style.css**
```css
/* 基础样式重置 */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Arial', sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #f4f4f4;
}

.container {
    width: 90%;
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

/* 头部样式 */
header {
    background-color: #2c3e50;
    color: white;
    padding: 20px 0;
    text-align: center;
    margin-bottom: 20px;
    border-radius: 5px;
}

/* 主内容区域样式 */
main {
    background-color: white;
    padding: 20px;
    border-radius: 5px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

/* 查询区域样式 */
.search-section {
    margin-bottom: 20px;
    padding-bottom: 20px;
    border-bottom: 1px solid #eee;
}

.search-form {
    display: flex;
    gap: 10px;
}

.search-form input {
    flex-grow: 1;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
}

.search-form button {
    padding: 10px 15px;
    background-color: #3498db;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

.search-form button:hover {
    background-color: #2980b9;
}

/* 表格样式 */
.robot-list {
    margin-bottom: 20px;
}

table {
    width: 100%;
    border-collapse: collapse;
}

th, td {
    padding: 12px 15px;
    text-align: left;
    border-bottom: 1px solid #ddd;
}

th {
    background-color: #f8f9fa;
    font-weight: bold;
}

tr:hover {
    background-color: #f5f5f5;
}

/* 操作按钮样式 */
.action-buttons {
    display: flex;
    gap: 10px;
}

.action-buttons button {
    padding: 10px 15px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-weight: bold;
}

.action-buttons button:nth-child(1) {
    background-color: #27ae60;
    color: white;
}

.action-buttons button:nth-child(2) {
    background-color: #f39c12;
    color: white;
}

.action-buttons button:nth-child(3) {
    background-color: #e74c3c;
    color: white;
}

.action-buttons button:hover {
    opacity: 0.9;
}
```

**static/script.js**
```javascript
// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 加载机器人数据
    loadRobots();
});

// 加载机器人数据函数
function loadRobots() {
    // 发送GET请求到服务器API
    fetch('/api/robots')
        .then(response => response.json())  // 解析响应为JSON
        .then(data => {
            // 调用函数填充表格数据
            populateTable(data);
        })
        .catch(error => {
            // 错误处理
            console.error('获取数据失败:', error);
        });
}

// 填充表格数据函数（HTML字符串拼接版）
function populateTable(robots) {
    // 获取表格tbody元素
    const tbody = document.querySelector('#robotTable tbody');
    // 清空现有内容
    tbody.innerHTML = '';
    
    // 用 map 拼接每一行
    let rows = robots.map(robot => {
        return `
            <tr>
                <td><input type="checkbox" data-id="${robot.id}"></td>
                <td>${robot.device_id}</td>
                <td>${robot.model}</td>
                <td>${robot.manufacturer}</td>
                <td>${robot.location}</td>
            </tr>
        `;
    }).join('');

    // 一次性写入表格
    tbody.innerHTML = rows;
}

// 查询机器人函数
function searchRobots() {
    // 获取搜索输入值
    const searchValue = document.getElementById('searchInput').value.toLowerCase();
    
    // 发送GET请求到服务器API
    fetch('/api/robots')
        .then(response => response.json())
        .then(data => {
            // 过滤数据
            const filteredData = data.filter(robot => 
                robot.device_id.toLowerCase().includes(searchValue) || 
                robot.model.toLowerCase().includes(searchValue)
            );
            // 填充过滤后的数据
            populateTable(filteredData);
        })
        .catch(error => {
            console.error('搜索失败:', error);
        });
}

// 新增机器人函数（待实现）
function addRobot() {
    alert('新增功能将在迭代2实现');
}

// 修改机器人函数（待实现）
function editRobot() {
    alert('修改功能将在迭代3实现');
}

// 删除机器人函数（待实现）
function deleteRobot() {
    alert('删除功能将在迭代4实现');
}
```

### 第五步：运行系统

1. 在终端中运行Python服务器：
```
python server.py
```

2. 打开浏览器访问：http://localhost:8000/static/index.html

现在你已经完成了迭代1，可以显示机器人列表数据。接下来我会在下一个迭代中指导你实现新增功能。

请运行当前代码确保一切正常，然后输入"继续"我将提供迭代2的内容。
