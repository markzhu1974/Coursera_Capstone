
### 里程碑二：完成机器人维修维护信息的录入、浏览、查询

在这个里程碑中，我们将在已有的系统基础上，扩展功能，增加一个专门的界面来管理特定机器人的维修记录。

#### 步骤 1: 更新数据库 (`database.py`)

首先，我们需要在数据库中添加一张新表来存储维修记录。

**修改 `database.py`:**

打开 `database.py` 文件，在 `init_db` 函数中添加创建 `maintenance_records` 表的SQL语句。

```python
# 导入sqlite3模块，它是Python中用于操作SQLite数据库的标准库
import sqlite3

# 定义一个函数来初始化数据库和数据表
def init_db():
    # 使用'with'语句连接到数据库（如果不存在，则会创建一个名为'robots.db'的文件）
    # 'with'语句可以确保数据库连接在使用后自动关闭
    with sqlite3.connect('robots.db') as conn:
        # 创建一个'cursor'对象，用于执行SQL语句
        cursor = conn.cursor()
        
        # 执行SQL语句来创建一个名为'robots'的数据表，如果它还不存在的话
        # 'CREATE TABLE IF NOT EXISTS'是一个安全的建表方式，不会在表已存在时报错
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS robots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,  -- 主键，整数类型，自动增长
                device_id TEXT NOT NULL UNIQUE,      -- 设备编号，文本类型，不能为空，且必须唯一
                model TEXT NOT NULL,                 -- 型号，文本类型，不能为空
                manufacturer TEXT NOT NULL,          -- 生产厂家，文本类型，不能为空
                location TEXT                        -- 位置，文本类型
            )
        ''')
        
        # --- 新增代码开始 ---
        # 执行SQL语句来创建一个名为'maintenance_records'的维修记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS maintenance_records (
                record_id INTEGER PRIMARY KEY AUTOINCREMENT, -- 维修记录的主键，自动增长
                robot_device_id TEXT NOT NULL,               -- 关联的机器人设备编号，文本类型，不能为空
                maintenance_date TEXT NOT NULL,              -- 维护日期，文本类型
                fault_code TEXT,                             -- 故障代码，文本类型
                phenomenon TEXT,                             -- 故障现象
                analysis TEXT,                               -- 原因分析
                measures TEXT,                               -- 采取措施
                parts_replaced TEXT,                         -- 更换部件
                duration REAL,                               -- 耗时（小时），浮点数类型
                technician TEXT,                             -- 维修人员
                FOREIGN KEY (robot_device_id) REFERENCES robots (device_id) -- 设置外键，关联到robots表的device_id
            )
        ''')
        # --- 新增代码结束 ---
        
        # 提交事务，将上述的建表操作保存到数据库文件中
        conn.commit()

# 这是一个常见的Python脚本写法，确保只有在直接运行此文件时，下面的代码才会被执行
if __name__ == '__main__':
    # 调用初始化函数
    init_db()
    # 在控制台打印一条消息，告知用户数据库已成功初始化
    print("数据库和数据表初始化/更新成功。")

```

**如何运行:**

再次在终端中运行 `database.py` 脚本来创建新表。这个操作是安全的，不会影响已有的 `robots` 表和数据。

```bash
python database.py
```

#### 步骤 2: 更新后端 (`server.py`)

现在我们需要为维修记录添加新的API接口。

1.  **获取** 某个特定机器人的所有维修记录。
2.  **添加** 一条新的维修记录。

**修改 `server.py`:**

```python
# 导入所需模块 (保持不变)
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import sqlite3
import os
from urllib.parse import urlparse, parse_qs # 导入urllib.parse用于解析URL参数

# --- 数据库操作函数 (robots部分保持不变) ---
def get_all_robots():
    # ... (此函数代码不变) ...
    with sqlite3.connect('robots.db') as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM robots")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def add_robot(robot_data):
    # ... (此函数代码不变) ...
    try:
        with sqlite3.connect('robots.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO robots (device_id, model, manufacturer, location) VALUES (?, ?, ?, ?)",
                           (robot_data['device_id'], robot_data['model'], robot_data['manufacturer'], robot_data['location']))
            conn.commit()
        return True, None
    except sqlite3.IntegrityError:
        return False, "设备编号已存在"

def update_robot(robot_id, robot_data):
    # ... (此函数代码不变) ...
    with sqlite3.connect('robots.db') as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE robots SET device_id=?, model=?, manufacturer=?, location=? WHERE id=?",
                       (robot_data['device_id'], robot_data['model'], robot_data['manufacturer'], robot_data['location'], robot_id))
        conn.commit()

def delete_robot(robot_id):
    # ... (此函数代码不变) ...
    with sqlite3.connect('robots.db') as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM robots WHERE id=?", (robot_id,))
        conn.commit()

# --- 新增的维修记录数据库操作函数 ---

# 根据设备编号获取维修记录
def get_maintenance_records(device_id):
    with sqlite3.connect('robots.db') as conn: # 连接数据库
        conn.row_factory = sqlite3.Row # 设置row_factory
        cursor = conn.cursor() # 创建游标
        # 查询指定device_id的所有维修记录，并按日期降序排列
        cursor.execute("SELECT * FROM maintenance_records WHERE robot_device_id = ? ORDER BY maintenance_date DESC", (device_id,))
        rows = cursor.fetchall() # 获取所有结果
        return [dict(row) for row in rows] # 转换为字典列表并返回

# 添加一条新的维修记录
def add_maintenance_record(record_data):
    with sqlite3.connect('robots.db') as conn: # 连接数据库
        cursor = conn.cursor() # 创建游标
        # 执行插入语句
        cursor.execute('''
            INSERT INTO maintenance_records 
            (robot_device_id, maintenance_date, fault_code, phenomenon, analysis, measures, parts_replaced, duration, technician)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            record_data['robot_device_id'],
            record_data['maintenance_date'],
            record_data['fault_code'],
            record_data['phenomenon'],
            record_data['analysis'],
            record_data['measures'],
            record_data['parts_replaced'],
            record_data['duration'],
            record_data['technician']
        ))
        conn.commit() # 提交事务


# --- HTTP请求处理类 (RequestHandler) ---

class RequestHandler(BaseHTTPRequestHandler):
    
    # 修改 do_GET 方法以处理新的API请求
    def do_GET(self):
        # 解析URL
        parsed_path = urlparse(self.path)
        path = parsed_path.path # 获取路径部分，如 /api/maintenance
        query = parse_qs(parsed_path.query) # 获取查询参数，如 {'deviceId': ['RB001']}

        # API请求：获取机器人列表
        if path == '/api/robots':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            robots = get_all_robots()
            self.wfile.write(json.dumps(robots).encode('utf-8'))
        
        # --- 新增代码开始 ---
        # API请求：获取特定机器人的维修记录
        elif path == '/api/maintenance':
            # 从查询参数中获取设备ID
            device_id = query.get('deviceId', [None])[0]
            if device_id:
                records = get_maintenance_records(device_id) # 调用函数获取数据
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(records).encode('utf-8')) # 返回JSON数据
            else:
                # 如果没有提供deviceId，则返回错误
                self.send_error(400, 'Missing deviceId query parameter')
        # --- 新增代码结束 ---

        # 文件请求：处理前端静态文件 (这部分逻辑不变)
        else:
            try:
                filepath = 'web' + ('/index.html' if self.path == '/' else self.path)
                if not os.path.abspath(filepath).startswith(os.path.abspath('web')):
                    raise FileNotFoundError
                with open(filepath, 'rb') as f:
                    self.send_response(200)
                    if filepath.endswith(".html"):
                        self.send_header('Content-type', 'text/html')
                    elif filepath.endswith(".css"):
                        self.send_header('Content-type', 'text/css')
                    self.end_headers()
                    self.wfile.write(f.read())
            except FileNotFoundError:
                self.send_error(404, 'File Not Found: %s' % self.path)

    # 修改 do_POST 方法以处理新的API请求
    def do_POST(self):
        # API请求：添加新机器人
        if self.path == '/api/robots':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            robot_data = json.loads(post_data)
            success, message = add_robot(robot_data)
            if success:
                self.send_response(201)
                self.end_headers()
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(message.encode('utf-8'))
        
        # --- 新增代码开始 ---
        # API请求：添加新维修记录
        elif self.path == '/api/maintenance':
            content_length = int(self.headers['Content-Length']) # 获取请求体长度
            post_data = self.rfile.read(content_length) # 读取数据
            record_data = json.loads(post_data) # 解析JSON
            
            add_maintenance_record(record_data) # 调用函数添加记录
            
            self.send_response(201) # 返回201 Created
            self.end_headers()
        # --- 新增代码结束 ---
        
    # do_PUT 和 do_DELETE 方法保持不变
    def do_PUT(self):
        # ... (此方法代码不变) ...
        if self.path.startswith('/api/robots/'):
            robot_id = int(self.path.split('/')[-1])
            content_length = int(self.headers['Content-Length'])
            put_data = self.rfile.read(content_length)
            robot_data = json.loads(put_data)
            update_robot(robot_id, robot_data)
            self.send_response(200)
            self.end_headers()

    def do_DELETE(self):
        # ... (此方法代码不变) ...
        if self.path.startswith('/api/robots/'):
            robot_id = int(self.path.split('/')[-1])
            delete_robot(robot_id)
            self.send_response(200)
            self.end_headers()

# --- 启动服务器 (保持不变) ---
def run(server_class=HTTPServer, handler_class=RequestHandler, port=8000):
    # ... (此函数代码不变) ...
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"服务器已在 http://localhost:{port} 上启动...")
    httpd.serve_forever()

if __name__ == '__main__':
    run()

```

#### 步骤 3: 更新前端 (`web/index.html` 和 `web/style.css`)

我们将对前端进行较大改动：

1.  将机器人列表和维修记录分为两个不同的“视图”或“页面”。
2.  在机器人列表的操作列增加一个“查看维修记录”的按钮。
3.  创建一个新的维修记录视图，包含一个表单用于添加新记录，一个表格用于显示历史记录。

**修改 `web/index.html`:**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>工业机器人信息管理系统</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>

    <div class="container">
        
        <div id="robot-view">
            <h1>工业机器人信息管理系统</h1>

            <div class.form-container">
                <form id="robot-form">
                    <input type="hidden" id="robot-id" name="id">
                    <input type="text" id="device_id" name="device_id" placeholder="设备编号" required>
                    <input type="text" id="model" name="model" placeholder="型号" required>
                    <input type="text" id="manufacturer" name="manufacturer" placeholder="生产厂家" required>
                    <input type="text" id="location" name="location" placeholder="位置">
                    <button type="submit">保存机器人</button>
                    <button type="button" onclick="clearForm()">取消</button>
                </form>
            </div>

            <h2>机器人列表</h2>
            <table id="robot-list">
                <thead>
                    <tr>
                        <th>设备编号</th>
                        <th>型号</th>
                        <th>生产厂家</th>
                        <th>位置</th>
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody id="robot-list-body"></tbody>
            </table>
        </div>

        <div id="maintenance-view" style="display: none;">
            <h1 id="maintenance-title">维修记录</h1>
            
            <button onclick="showRobotView()">返回机器人列表</button>

            <h2>添加新维修记录</h2>
            <div class.form-container">
                <form id="maintenance-form">
                    <input type="hidden" id="maint-robot-device-id">
                    <input type="date" id="maintenance_date" required>
                    <input type="text" id="fault_code" placeholder="故障代码">
                    <input type="text" id="technician" placeholder="维修人员" required>
                    <input type="number" id="duration" placeholder="耗时(小时)" step="0.1">
                    <textarea id="phenomenon" placeholder="故障现象"></textarea>
                    <textarea id="analysis" placeholder="原因分析"></textarea>
                    <textarea id="measures" placeholder="采取措施"></textarea>
                    <textarea id="parts_replaced" placeholder="更换部件"></textarea>
                    <button type="submit">保存记录</button>
                </form>
            </div>

            <h2>历史维修记录</h2>
            <table id="maintenance-list">
                <thead>
                    <tr>
                        <th>维修日期</th>
                        <th>故障代码</th>
                        <th>故障现象</th>
                        <th>维修人员</th>
                        <th>耗时</th>
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody id="maintenance-list-body"></tbody>
            </table>
        </div>

    </div>

    <script>
        // 当文档加载完成后执行
        document.addEventListener('DOMContentLoaded', function() {
            // 加载机器人列表
            loadRobots();

            // 监听机器人表单提交事件
            document.getElementById('robot-form').addEventListener('submit', function(event) {
                event.preventDefault();
                saveRobot();
            });
            
            // --- 新增代码开始 ---
            // 监听维修记录表单提交事件
            document.getElementById('maintenance-form').addEventListener('submit', function(event) {
                event.preventDefault();
                saveMaintenanceRecord();
            });
            // --- 新增代码结束 ---
        });

        // --- 视图切换函数 ---
        // 显示机器人列表视图
        function showRobotView() {
            document.getElementById('robot-view').style.display = 'block';
            document.getElementById('maintenance-view').style.display = 'none';
        }
        
        // 显示维修记录视图
        function showMaintenanceView(deviceId) {
            document.getElementById('robot-view').style.display = 'none';
            document.getElementById('maintenance-view').style.display = 'block';
            // 设置标题和隐藏字段的值
            document.getElementById('maintenance-title').innerText = `机器人 [${deviceId}] 的维修记录`;
            document.getElementById('maint-robot-device-id').value = deviceId;
            // 加载该机器人的维修记录
            loadMaintenanceRecords(deviceId);
        }

        // --- 机器人相关函数 (大部分不变, loadRobots有小修改) ---
        function clearForm() { /* ... (代码不变) ... */ 
            document.getElementById('robot-form').reset();
            document.getElementById('robot-id').value = '';
        }

        async function loadRobots() {
            try {
                const response = await fetch('/api/robots');
                const robots = await response.json();
                const tbody = document.getElementById('robot-list-body');
                tbody.innerHTML = '';
                
                robots.forEach(robot => {
                    const tr = document.createElement('tr');
                    tr.dataset.id = robot.id;
                    // --- 修改：在操作列增加 "查看维修记录" 按钮 ---
                    tr.innerHTML = `
                        <td>${robot.device_id}</td>
                        <td>${robot.model}</td>
                        <td>${robot.manufacturer}</td>
                        <td>${robot.location}</td>
                        <td>
                            <button onclick="editRobot(${robot.id}, '${robot.device_id}', '${robot.model}', '${robot.manufacturer}', '${robot.location}')">编辑</button>
                            <button onclick="deleteRobot(${robot.id})">删除</button>
                            <button class="view-maint" onclick="showMaintenanceView('${robot.device_id}')">查看维修记录</button>
                        </td>
                    `;
                    tbody.appendChild(tr);
                });
            } catch (error) {
                console.error('加载机器人列表失败:', error);
            }
        }
        
        async function saveRobot() { /* ... (代码不变) ... */ 
            const id = document.getElementById('robot-id').value;
            const device_id = document.getElementById('device_id').value;
            const model = document.getElementById('model').value;
            const manufacturer = document.getElementById('manufacturer').value;
            const location = document.getElementById('location').value;
            const robotData = { device_id, model, manufacturer, location };
            const isUpdating = id !== '';
            const url = isUpdating ? `/api/robots/${id}` : '/api/robots';
            const method = isUpdating ? 'PUT' : 'POST';
            try {
                const response = await fetch(url, {
                    method: method,
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(robotData),
                });
                if (response.ok) {
                    clearForm();
                    loadRobots();
                } else {
                    const errorText = await response.text();
                    alert('保存失败: ' + errorText);
                }
            } catch (error) {
                console.error('保存机器人失败:', error);
            }
        }

        function editRobot(id, device_id, model, manufacturer, location) { /* ... (代码不变) ... */ 
            document.getElementById('robot-id').value = id;
            document.getElementById('device_id').value = device_id;
            document.getElementById('model').value = model;
            document.getElementById('manufacturer').value = manufacturer;
            document.getElementById('location').value = location;
            window.scrollTo(0, 0); // 滚动到页面顶部方便编辑
        }
        
        async function deleteRobot(id) { /* ... (代码不变) ... */ 
            if (confirm('确定要删除这个机器人吗？')) {
                try {
                    const response = await fetch(`/api/robots/${id}`, { method: 'DELETE' });
                    if (response.ok) {
                        loadRobots();
                    } else {
                        const errorText = await response.text();
                        alert('删除失败: ' + errorText);
                    }
                } catch (error) {
                    console.error('删除机器人失败:', error);
                }
            }
        }

        // --- 新增的维修记录相关函数 ---

        // 加载特定机器人的维修记录
        async function loadMaintenanceRecords(deviceId) {
            try {
                // 发送GET请求，注意URL中包含了查询参数
                const response = await fetch(`/api/maintenance?deviceId=${deviceId}`);
                const records = await response.json();
                const tbody = document.getElementById('maintenance-list-body');
                tbody.innerHTML = ''; // 清空列表

                // 遍历记录并添加到表格
                records.forEach(record => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td>${record.maintenance_date}</td>
                        <td>${record.fault_code}</td>
                        <td>${record.phenomenon}</td>
                        <td>${record.technician}</td>
                        <td>${record.duration || ''}</td>
                        <td>
                            <button>详情</button>
                        </td>
                    `;
                    tbody.appendChild(tr);
                });
            } catch (error) {
                console.error('加载维修记录失败:', error);
            }
        }
        
        // 保存一条新的维修记录
        async function saveMaintenanceRecord() {
            // 从表单获取数据
            const deviceId = document.getElementById('maint-robot-device-id').value;
            const recordData = {
                robot_device_id: deviceId,
                maintenance_date: document.getElementById('maintenance_date').value,
                fault_code: document.getElementById('fault_code').value,
                phenomenon: document.getElementById('phenomenon').value,
                analysis: document.getElementById('analysis').value,
                measures: document.getElementById('measures').value,
                parts_replaced: document.getElementById('parts_replaced').value,
                duration: parseFloat(document.getElementById('duration').value) || null, // 转换为浮点数，如果为空则为null
                technician: document.getElementById('technician').value,
            };

            // 简单的输入验证
            if (!recordData.maintenance_date || !recordData.technician) {
                alert('维修日期和维修人员不能为空！');
                return;
            }
            
            try {
                // 发送POST请求到后端
                const response = await fetch('/api/maintenance', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(recordData),
                });
                
                if (response.ok) {
                    // 如果成功，重置表单并重新加载列表
                    document.getElementById('maintenance-form').reset();
                    loadMaintenanceRecords(deviceId);
                } else {
                    alert('保存维修记录失败！');
                }
            } catch (error) {
                console.error('保存维修记录失败:', error);
            }
        }
    </script>
</body>
</html>
```

**修改 `web/style.css`:**

在 `style.css` 文件末尾添加一些新的样式来美化维修记录的表单和按钮。

```css
/* ... (之前的CSS代码保持不变) ... */

/* 查看维修记录按钮的样式 */
.view-maint {
    background-color: #17a2b8 !important; /* 使用!important覆盖通用按钮样式 */
}

.view-maint:hover {
    background-color: #138496 !important;
}

/* 维修记录表单中的textarea样式 */
#maintenance-form textarea {
    width: 100%; /* 宽度占满 */
    padding: 10px; /* 内边距 */
    margin-bottom: 10px; /* 下外边距 */
    border-radius: 4px; /* 圆角 */
    border: 1px solid #ccc; /* 边框 */
    box-sizing: border-box; /* 让padding和border包含在width内 */
    min-height: 80px; /* 最小高度 */
    font-family: inherit; /* 继承字体 */
}

/* 维修记录表单中特定输入框的样式，让它们并排显示 */
#maintenance-form input[type="date"],
#maintenance-form input[type="text"],
#maintenance-form input[type="number"] {
    display: inline-block; /* 设置为行内块元素 */
    width: 49%; /* 宽度约为一半，留出间隙 */
}

/* 返回按钮的样式 */
#maintenance-view > button {
    background-color: #6c757d;
    color: white;
    padding: 10px 15px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    margin-bottom: 20px;
}

#maintenance-view > button:hover {
    background-color: #5a6268;
}
```

#### 步骤 4: 运行和测试

1.  **停止旧的服务器**：如果你之前的 `server.py` 还在运行，按 `Ctrl + C` 停止它。
2.  **更新数据库**：确保你已经重新运行了 `python database.py` 来添加新表。
3.  **启动新服务器**：在终端中，再次运行 `server.py`：
    ```bash
    python server.py
    ```
4.  **访问和测试**：
      * 在浏览器中刷新 `http://localhost:8000`。
      * 机器人列表的每一行后面应该多了一个蓝色的“查看维修记录”按钮。
      * 点击任意一个机器人的“查看维修记录”按钮。页面应该会切换到维修记录视图，并显示该机器人的设备编号。
      * 在“添加新维修记录”表单中填写信息，然后点击“保存记录”。
      * 新保存的记录应该会立即出现在下方的“历史维修记录”表格中。
      * 点击“返回机器人列表”按钮，页面应该会切换回机器人列表视图。

**恭喜！你已经完成了第二个里程碑！** 你的系统现在不仅能管理机器人基本信息，还能管理每个机器人的详细维修历史了。
