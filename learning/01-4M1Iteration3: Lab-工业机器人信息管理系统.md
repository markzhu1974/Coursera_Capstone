# 迭代3：完成机器人修改功能

现在我们将实现修改机器人信息的功能，包括前端编辑界面和后端API。

## 第一步：扩展数据库功能

**database.py**（新增函数）
```python
# 添加根据ID获取机器人信息的函数
def get_robot_by_id(robot_id):
    conn = sqlite3.connect('robots.db')
    cursor = conn.cursor()
    
    # 根据ID查询机器人信息
    cursor.execute(
        'SELECT id, device_id, model, manufacturer, location FROM robots WHERE id = ?',
        (robot_id,)
    )
    robot = cursor.fetchone()
    conn.close()
    
    if robot:
        # 返回机器人信息的字典形式
        return {
            'id': robot[0],
            'device_id': robot[1],
            'model': robot[2],
            'manufacturer': robot[3],
            'location': robot[4]
        }
    return None

# 添加更新机器人信息的函数
def update_robot(robot_id, device_id, model, manufacturer, location):
    conn = sqlite3.connect('robots.db')
    cursor = conn.cursor()
    
    try:
        # 更新机器人信息，确保设备编号不重复（排除当前记录）
        cursor.execute(
            '''UPDATE robots 
               SET device_id = ?, model = ?, manufacturer = ?, location = ?
               WHERE id = ? AND device_id NOT IN (
                   SELECT device_id FROM robots WHERE device_id = ? AND id != ?
               )''',
            (device_id, model, manufacturer, location, robot_id, device_id, robot_id)
        )
        
        # 检查是否成功更新
        if cursor.rowcount > 0:
            conn.commit()
            return True
        else:
            # 可能是设备编号重复或记录不存在
            return False
    except Exception as e:
        # 处理其他异常
        print(f"更新数据时发生错误: {e}")
        return False
    finally:
        conn.close()
```

## 第二步：扩展服务器API

**server.py**（按下面的说明修改代码，以满足新增机器人信息都需要）
```python

#import库进行url路径的解析
import urllib.parse

...

# 在do_GET方法下加上路径解析，并且加上请求单条信息的代码。
# 用下面的do_GET方法的代码替换原先的do_GET方法的代码

def do_GET(self):
    # 解析请求路径
    parsed_path = urllib.parse.urlparse(self.path)
    path = parsed_path.path
    
    # 如果请求根路径"/"，重定向到static/index.html
    if path == '/':
        self.send_response(302)
        self.send_header('Location', '/static/index.html')
        self.end_headers()
        return
    
    # 如果请求路径是/api/robots，返回所有机器人列表
    if path == '/api/robots':
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.set_cors_headers()
        self.end_headers()
        
        robots = database.get_all_robots()
        robots_list = []
        for robot in robots:
            robots_list.append({
                'id': robot[0],
                'device_id': robot[1],
                'model': robot[2],
                'manufacturer': robot[3],
                'location': robot[4]
            })
        
        self.wfile.write(json.dumps(robots_list).encode())
        return
    
    # 如果请求路径是/api/robots/{id}，返回单个机器人信息
    if path.startswith('/api/robots/'):
        robot_id = path.split('/')[-1]
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.set_cors_headers()
        self.end_headers()
        
        robot = database.get_robot_by_id(robot_id)
        if robot:
            self.wfile.write(json.dumps(robot).encode())
        else:
            response = {'error': '机器人不存在'}
            self.wfile.write(json.dumps(response).encode())
        return
    
    # 对于静态文件请求，设置正确的目录路径
    if path.startswith('/static/'):
        # 设置静态文件目录为当前目录
        self.directory = os.getcwd()
        # 调用父类方法处理静态文件
        super().do_GET()
        return
    
    # 对于其他请求返回404
    self.send_response(404)
    self.end_headers()
    self.wfile.write(b'File not found')

...

# 增加do_PUT方法，以处理对机器人信息的修改

# 处理PUT请求（修改机器人）
def do_PUT(self):
    # 只处理/api/robots/的PUT请求
    if self.path.startswith('/api/robots/'):
        # 从URL路径中提取机器人ID
        robot_id = self.path.split('/')[-1]
        
        # 获取请求内容长度
        content_length = int(self.headers['Content-Length'])
        # 读取请求体数据
        put_data = self.rfile.read(content_length)
        
        try:
            # 解析JSON数据
            data = json.loads(put_data.decode('utf-8'))
            
            # 调用数据库函数更新机器人信息
            success = database.update_robot(
                robot_id,
                data['device_id'],
                data['model'],
                data['manufacturer'],
                data['location']
            )
            
            if success:
                # 更新成功，返回200状态码
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.set_cors_headers()
                self.end_headers()
                response = {'message': '机器人信息更新成功'}
                self.wfile.write(json.dumps(response).encode())
            else:
                # 更新失败，返回400状态码
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.set_cors_headers()
                self.end_headers()
                response = {'error': '更新失败，设备编号可能已存在或记录不存在'}
                self.wfile.write(json.dumps(response).encode())
                
        except json.JSONDecodeError:
            # JSON解析错误
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.set_cors_headers()
            self.end_headers()
            response = {'error': '无效的JSON数据'}
            self.wfile.write(json.dumps(response).encode())
        except KeyError as e:
            # 缺少必要字段
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.set_cors_headers()
            self.end_headers()
            response = {'error': f'缺少必要字段: {e}'}
            self.wfile.write(json.dumps(response).encode())
    else:
        # 对于其他PUT请求返回404
        self.send_response(404)
        self.end_headers()

```

以下是更新好之后完整的代码

**server.py**（新增do_PUT方法后完整的server.py代码）
```python
import http.server
import socketserver
import json
import database
import os
import urllib.parse

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
    
    # 重写do_GET方法以处理默认页面重定向和API请求
    def do_GET(self):
        # 解析请求路径
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        # 如果请求根路径"/"，重定向到static/index.html
        if path == '/':
            self.send_response(302)
            self.send_header('Location', '/static/index.html')
            self.end_headers()
            return
        
        # 如果请求路径是/api/robots，返回所有机器人列表
        if path == '/api/robots':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.set_cors_headers()
            self.end_headers()
            
            robots = database.get_all_robots()
            robots_list = []
            for robot in robots:
                robots_list.append({
                    'id': robot[0],
                    'device_id': robot[1],
                    'model': robot[2],
                    'manufacturer': robot[3],
                    'location': robot[4]
                })
            
            self.wfile.write(json.dumps(robots_list).encode())
            return
        
        # 如果请求路径是/api/robots/{id}，返回单个机器人信息
        if path.startswith('/api/robots/'):
            robot_id = path.split('/')[-1]
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.set_cors_headers()
            self.end_headers()
            
            robot = database.get_robot_by_id(robot_id)
            if robot:
                self.wfile.write(json.dumps(robot).encode())
            else:
                response = {'error': '机器人不存在'}
                self.wfile.write(json.dumps(response).encode())
            return
        
        # 对于静态文件请求，设置正确的目录路径
        if path.startswith('/static/'):
            # 设置静态文件目录为当前目录
            self.directory = os.getcwd()
            # 调用父类方法处理静态文件
            super().do_GET()
            return
        
        # 对于其他请求返回404
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b'File not found')
    
    # 处理POST请求（新增机器人）
    def do_POST(self):
        # 只处理/api/robots的POST请求
        if self.path == '/api/robots':
            # 获取请求内容长度
            content_length = int(self.headers['Content-Length'])
            # 读取请求体数据
            post_data = self.rfile.read(content_length)
            
            try:
                # 解析JSON数据
                data = json.loads(post_data.decode('utf-8'))
                
                # 调用数据库函数添加机器人
                success = database.add_robot(
                    data['device_id'],
                    data['model'],
                    data['manufacturer'],
                    data['location']
                )
                
                if success:
                    # 添加成功，返回201状态码
                    self.send_response(201)
                    self.send_header('Content-type', 'application/json')
                    self.set_cors_headers()
                    self.end_headers()
                    response = {'message': '机器人添加成功'}
                    self.wfile.write(json.dumps(response).encode())
                else:
                    # 添加失败，返回400状态码
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.set_cors_headers()
                    self.end_headers()
                    response = {'error': '添加失败，设备编号可能已存在'}
                    self.wfile.write(json.dumps(response).encode())
                    
            except json.JSONDecodeError:
                # JSON解析错误
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.set_cors_headers()
                self.end_headers()
                response = {'error': '无效的JSON数据'}
                self.wfile.write(json.dumps(response).encode())
            except KeyError as e:
                # 缺少必要字段
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.set_cors_headers()
                self.end_headers()
                response = {'error': f'缺少必要字段: {e}'}
                self.wfile.write(json.dumps(response).encode())
        else:
            # 对于其他POST请求返回404
            self.send_response(404)
            self.end_headers()
    
    # 处理PUT请求（修改机器人）
    def do_PUT(self):
        # 只处理/api/robots/的PUT请求
        if self.path.startswith('/api/robots/'):
            # 从URL路径中提取机器人ID
            robot_id = self.path.split('/')[-1]
            
            # 获取请求内容长度
            content_length = int(self.headers['Content-Length'])
            # 读取请求体数据
            put_data = self.rfile.read(content_length)
            
            try:
                # 解析JSON数据
                data = json.loads(put_data.decode('utf-8'))
                
                # 调用数据库函数更新机器人信息
                success = database.update_robot(
                    robot_id,
                    data['device_id'],
                    data['model'],
                    data['manufacturer'],
                    data['location']
                )
                
                if success:
                    # 更新成功，返回200状态码
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.set_cors_headers()
                    self.end_headers()
                    response = {'message': '机器人信息更新成功'}
                    self.wfile.write(json.dumps(response).encode())
                else:
                    # 更新失败，返回400状态码
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.set_cors_headers()
                    self.end_headers()
                    response = {'error': '更新失败，设备编号可能已存在或记录不存在'}
                    self.wfile.write(json.dumps(response).encode())
                    
            except json.JSONDecodeError:
                # JSON解析错误
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.set_cors_headers()
                self.end_headers()
                response = {'error': '无效的JSON数据'}
                self.wfile.write(json.dumps(response).encode())
            except KeyError as e:
                # 缺少必要字段
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.set_cors_headers()
                self.end_headers()
                response = {'error': f'缺少必要字段: {e}'}
                self.wfile.write(json.dumps(response).encode())
        else:
            # 对于其他PUT请求返回404
            self.send_response(404)
            self.end_headers()

# 程序入口点
if __name__ == '__main__':
    # 初始化数据库
    database.init_database()
    database.insert_sample_data()
    
    # 创建TCP服务器实例
    with socketserver.TCPServer(("", PORT), RobotHandler) as httpd:
        print(f"服务器运行在端口 {PORT}")
        print("打开浏览器访问: http://localhost:8000/")
        print("静态文件目录: ", os.getcwd())
        # 启动服务器，持续处理请求
        httpd.serve_forever()
```

## 第三步：创建编辑机器人模态窗口

**static/index.html**（在body末尾添加，放在新增模态窗口之后）
```html
<!-- 编辑机器人模态窗口 -->
<div id="editModal" class="modal">
    <div class="modal-content">
        <span class="close" onclick="closeEditModal()">&times;</span>
        <h2>编辑机器人信息</h2>
        <form id="editForm" onsubmit="submitEditForm(event)">
            <input type="hidden" id="edit_id" name="id">
            <div class="form-group">
                <label for="edit_device_id">设备编号:</label>
                <input type="text" id="edit_device_id" name="device_id" required>
            </div>
            <div class="form-group">
                <label for="edit_model">型号:</label>
                <input type="text" id="edit_model" name="model" required>
            </div>
            <div class="form-group">
                <label for="edit_manufacturer">生产厂家:</label>
                <input type="text" id="edit_manufacturer" name="manufacturer" required>
            </div>
            <div class="form-group">
                <label for="edit_location">位置:</label>
                <input type="text" id="edit_location" name="location" required>
            </div>
            <div class="form-buttons">
                <button type="submit">保存</button>
                <button type="button" onclick="closeEditModal()">取消</button>
            </div>
        </form>
    </div>
</div>
```

## 第四步：更新前端JavaScript功能

**static/script.js**（更新和新增函数）
```javascript
// 更新editRobot函数，打开编辑模态窗口
function editRobot() {
    // 获取选中的机器人
    const selectedRobot = getSelectedRobot();
    if (!selectedRobot) {
        alert('请先选择一个机器人');
        return;
    }
    
    // 获取机器人详细信息
    fetch(`/api/robots/${selectedRobot}`)
        .then(response => response.json())
        .then(robot => {
            if (robot.error) {
                alert(robot.error);
                return;
            }
            
            // 填充表单数据
            document.getElementById('edit_id').value = robot.id;
            document.getElementById('edit_device_id').value = robot.device_id;
            document.getElementById('edit_model').value = robot.model;
            document.getElementById('edit_manufacturer').value = robot.manufacturer;
            document.getElementById('edit_location').value = robot.location;
            
            // 显示编辑模态窗口
            const modal = document.getElementById('editModal');
            modal.style.display = 'block';
        })
        .catch(error => {
            console.error('获取机器人信息失败:', error);
            alert('获取机器人信息失败');
        });
}

// 关闭编辑模态窗口
function closeEditModal() {
    const modal = document.getElementById('editModal');
    modal.style.display = 'none';
}

// 提交编辑表单
function submitEditForm(event) {
    event.preventDefault(); // 阻止表单默认提交行为
    
    // 获取表单数据
    const formData = {
        device_id: document.getElementById('edit_device_id').value,
        model: document.getElementById('edit_model').value,
        manufacturer: document.getElementById('edit_manufacturer').value,
        location: document.getElementById('edit_location').value
    };
    
    const robotId = document.getElementById('edit_id').value;
    
    // 发送PUT请求到服务器
    fetch(`/api/robots/${robotId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response => {
        if (response.status === 200) {
            // 更新成功
            alert('机器人信息更新成功！');
            closeEditModal();
            loadRobots(); // 重新加载数据
        } else if (response.status === 400) {
            // 更新失败，显示错误信息
            return response.json().then(data => {
                alert('更新失败: ' + data.error);
            });
        }
    })
    .catch(error => {
        console.error('更新机器人信息时发生错误:', error);
        alert('更新失败，请检查网络连接');
    });
}

// 获取选中的机器人ID
function getSelectedRobot() {
    const checkboxes = document.querySelectorAll('#robotTable tbody input[type="checkbox"]:checked');
    if (checkboxes.length === 0) {
        return null;
    }
    if (checkboxes.length > 1) {
        alert('请只选择一个机器人');
        return null;
    }
    return checkboxes[0].dataset.id;
}

// 更新window.onclick函数，支持关闭编辑模态窗口
window.onclick = function(event) {
    const addModal = document.getElementById('addModal');
    const editModal = document.getElementById('editModal');
    
    if (event.target === addModal) {
        closeAddModal();
    }
    if (event.target === editModal) {
        closeEditModal();
    }
};
```

这里，同样，要注意把之前定义的待实现的editRobot() 方法删去

```javascript
// 修改机器人函数（待实现）
function editRobot() {
    alert('修改功能将在迭代3实现');
}
```


## 第五步：测试修改功能

1. 重启服务器：`python server.py`
2. 访问：`http://localhost:8000/`
3. 选择一个机器人，点击"修改"按钮
4. 修改表单数据并提交
5. 检查数据是否成功更新

## 功能说明

现在你已完成迭代3，实现了以下功能：

1. **数据库层**：
   - 添加了`get_robot_by_id`函数获取单个机器人信息
   - 添加了`update_robot`函数更新机器人信息

2. **服务器层**：
   - 添加了`do_PUT`方法处理HTTP PUT请求
   - 扩展了`do_GET`方法支持获取单个机器人信息

3. **前端层**：
   - 创建了编辑模态窗口
   - 实现了获取选中机器人功能
   - 添加了表单预填充和数据提交逻辑
   - 增强了错误处理和用户反馈

**关键特性：**
- 支持选择单个机器人进行编辑
- 表单自动填充现有数据
- 设备编号唯一性验证（排除当前记录）
- 友好的用户反馈
- 自动刷新数据列表

现在用户可以选择一个机器人，点击"修改"按钮，编辑信息并保存更新。

请测试这个功能，确保一切正常工作，然后输入"继续"我将提供迭代4的内容。