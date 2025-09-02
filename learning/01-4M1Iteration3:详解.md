# 工业机器人信息管理系统 - 迭代3：修改功能详解

## ✅ 整体架构说明

本系统采用 **前后端分离架构**，修改功能涉及以下组件：

```
┌────────────────────┐    ┌──────────────────┐    ┌──────────────────┐    ┌─────────────┐
│  前端 (HTML/JS)    │───▶│  server.py       │───▶│  database.py     │───▶│  SQLite     │
│  选择 + 编辑表单    │    │  GET/PUT请求处理  │    │  数据读取/更新   │    │  robots.db  │
└────────────────────┘    └──────────────────┘    └──────────────────┘    └─────────────┘
```

---

## 第一步：扩展数据库功能（`database.py`）

### 1. 获取单个机器人信息

```python
# 添加根据ID获取机器人信息的函数
def get_robot_by_id(robot_id):
    """
    根据机器人ID从数据库中查询单个机器人信息
    参数：
        robot_id: 机器人的唯一标识ID
    返回值：
        如果找到，返回包含机器人信息的字典
        如果未找到，返回None
    """
    
    # 连接SQLite数据库
    # 如果robots.db不存在，会自动创建
    conn = sqlite3.connect('robots.db')
    
    # 创建游标对象，用于执行SQL命令
    cursor = conn.cursor()
    
    # 执行SQL查询，根据ID获取机器人信息
    # 使用?占位符防止SQL注入攻击
    # (robot_id,) 是一个元组，即使只有一个参数也要加逗号
    cursor.execute(
        'SELECT id, device_id, model, manufacturer, location FROM robots WHERE id = ?',
        (robot_id,)
    )
    
    # fetchone() 获取一条记录
    # 如果没找到，返回None
    robot = cursor.fetchone()
    
    # 关闭数据库连接，释放资源
    conn.close()
    
    # 如果查询到了机器人数据
    if robot:
        # 将元组数据转换为字典格式，便于JSON序列化
        return {
            'id': robot[0],           # 第1列：ID
            'device_id': robot[1],    # 第2列：设备编号
            'model': robot[2],        # 第3列：型号
            'manufacturer': robot[3], # 第4列：生产厂家
            'location': robot[4]      # 第5列：位置
        }
    # 如果没有找到，返回None
    return None
```

### 2. 更新机器人信息

```python
# 添加更新机器人信息的函数
def update_robot(robot_id, device_id, model, manufacturer, location):
    """
    更新数据库中指定ID的机器人信息
    参数：
        robot_id: 要更新的机器人ID
        device_id: 新的设备编号
        model: 新的型号
        manufacturer: 新的生产厂家
        location: 新的位置
    返回值：
        True: 更新成功
        False: 更新失败（如设备编号重复）
    """
    
    # 连接数据库
    conn = sqlite3.connect('robots.db')
    
    # 创建游标
    cursor = conn.cursor()
    
    # 使用try-except-finally确保资源正确释放
    try:
        # 执行UPDATE语句更新机器人信息
        # 复杂的WHERE条件确保：
        # 1. 更新指定ID的记录
        # 2. 新的设备编号不能与其他机器人的设备编号冲突（排除自己）
        cursor.execute(
            '''UPDATE robots 
               SET device_id = ?, model = ?, manufacturer = ?, location = ?
               WHERE id = ? AND device_id NOT IN (
                   SELECT device_id FROM robots WHERE device_id = ? AND id != ?
               )''',
            # 参数按顺序填入?占位符
            (device_id, model, manufacturer, location, robot_id, device_id, robot_id)
        )
        
        # 检查是否成功更新了记录
        # rowcount表示受影响的行数
        if cursor.rowcount > 0:
            # 有记录被更新，提交事务
            conn.commit()
            return True
        else:
            # 没有记录被更新
            # 可能原因：记录不存在 或 设备编号重复
            return False
            
    except Exception as e:
        # 捕获其他异常（如数据库连接问题）
        print(f"更新数据时发生错误: {e}")
        return False
        
    finally:
        # 无论成功或失败，都关闭数据库连接
        conn.close()
```

> 💡 **安全提示**：`UPDATE`语句中的子查询确保了设备编号的唯一性验证，防止更新时出现重复。

---

## 第二步：扩展服务器API（`server.py`）

### 1. 导入URL解析库

```python
# 导入urllib.parse库，用于解析URL路径
# 这样可以轻松提取路径中的参数
import urllib.parse
```

### 2. 更新`do_GET`方法（支持获取单个机器人）

```python
# 重写do_GET方法以处理多种请求
def do_GET(self):
    """
    处理HTTP GET请求
    支持：
    - / → 重定向到首页
    - /api/robots → 获取所有机器人
    - /api/robots/{id} → 获取单个机器人
    - /static/... → 静态文件服务
    """
    
    # 解析完整的URL，分离出路径、查询参数等
    parsed_path = urllib.parse.urlparse(self.path)
    path = parsed_path.path  # 只取路径部分
    
    # 如果请求根路径"/"，重定向到静态首页
    if path == '/':
        self.send_response(302)  # 302临时重定向
        self.send_header('Location', '/static/index.html')  # 重定向目标
        self.end_headers()
        return
    
    # 如果请求所有机器人列表
    if path == '/api/robots':
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.set_cors_headers()
        self.end_headers()
        
        # 从数据库获取所有机器人
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
        
        # 发送JSON响应
        self.wfile.write(json.dumps(robots_list).encode())
        return
    
    # 如果请求单个机器人信息 /api/robots/{id}
    if path.startswith('/api/robots/'):
        # 从路径中提取ID：/api/robots/5 → 5
        robot_id = path.split('/')[-1]
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.set_cors_headers()
        self.end_headers()
        
        # 从数据库获取指定ID的机器人
        robot = database.get_robot_by_id(robot_id)
        
        if robot:
            # 找到机器人，返回其信息
            self.wfile.write(json.dumps(robot).encode())
        else:
            # 没找到，返回错误信息
            response = {'error': '机器人不存在'}
            self.wfile.write(json.dumps(response).encode())
        return
    
    # 如果请求静态文件（CSS、JS、图片等）
    if path.startswith('/static/'):
        # 设置静态文件目录为当前工作目录
        self.directory = os.getcwd()
        # 调用父类方法处理文件读取
        super().do_GET()
        return
    
    # 其他路径返回404
    self.send_response(404)
    self.end_headers()
    self.wfile.write(b'File not found')
```

### 3. 新增`do_PUT`方法（处理修改请求）

```python
# 处理PUT请求（修改机器人）
def do_PUT(self):
    """
    处理HTTP PUT请求，用于更新机器人信息
    请求路径：/api/robots/{id}
    请求体：JSON格式的机器人信息
    """
    
    # 只处理/api/robots/{id}格式的PUT请求
    if self.path.startswith('/api/robots/'):
        # 从URL中提取机器人ID
        # 例如：/api/robots/3 → robot_id = "3"
        robot_id = self.path.split('/')[-1]
        
        # 获取请求体的长度（字节数）
        content_length = int(self.headers['Content-Length'])
        
        # 读取请求体中的原始数据
        put_data = self.rfile.read(content_length)
        
        # 使用try-except结构处理可能的异常
        try:
            # 将字节数据解码为UTF-8字符串，然后解析为JSON对象
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
                # 更新成功，返回HTTP 200 OK
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.set_cors_headers()
                self.end_headers()
                response = {'message': '机器人信息更新成功'}
                self.wfile.write(json.dumps(response).encode())
            else:
                # 更新失败，可能是设备编号重复或记录不存在
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.set_cors_headers()
                self.end_headers()
                response = {'error': '更新失败，设备编号可能已存在或记录不存在'}
                self.wfile.write(json.dumps(response).encode())
                
        except json.JSONDecodeError:
            # JSON格式错误
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.set_cors_headers()
            self.end_headers()
            response = {'error': '无效的JSON数据'}
            self.wfile.write(json.dumps(response).encode())
            
        except KeyError as e:
            # 缺少必要的JSON字段
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.set_cors_headers()
            self.end_headers()
            response = {'error': f'缺少必要字段: {e}'}
            self.wfile.write(json.dumps(response).encode())
    else:
        # 不支持的PUT路径，返回404
        self.send_response(404)
        self.end_headers()
```

---

## 第三步：创建编辑机器人模态窗口（`static/index.html`）

```html
<!-- 编辑机器人模态窗口 -->
<!-- 这是一个浮动的对话框，用于编辑现有机器人信息 -->
<div id="editModal" class="modal">
    <!-- 模态窗口的内容区域 -->
    <div class="modal-content">
        <!-- 关闭按钮，点击时调用closeEditModal()函数 -->
        <span class="close" onclick="closeEditModal()">&times;</span>
        <h2>编辑机器人信息</h2>
        
        <!-- 编辑表单，onsubmit事件阻止默认提交行为 -->
        <form id="editForm" onsubmit="submitEditForm(event)">
            <!-- 隐藏字段：存储机器人ID，不显示给用户 -->
            <input type="hidden" id="edit_id" name="id">
            
            <!-- 设备编号输入组 -->
            <div class="form-group">
                <label for="edit_device_id">设备编号:</label>
                <!-- required属性表示必填字段 -->
                <input type="text" id="edit_device_id" name="device_id" required>
            </div>
            
            <!-- 型号输入组 -->
            <div class="form-group">
                <label for="edit_model">型号:</label>
                <input type="text" id="edit_model" name="model" required>
            </div>
            
            <!-- 生产厂家输入组 -->
            <div class="form-group">
                <label for="edit_manufacturer">生产厂家:</label>
                <input type="text" id="edit_manufacturer" name="manufacturer" required>
            </div>
            
            <!-- 位置输入组 -->
            <div class="form-group">
                <label for="edit_location">位置:</label>
                <input type="text" id="edit_location" name="location" required>
            </div>
            
            <!-- 表单操作按钮 -->
            <div class="form-buttons">
                <!-- 提交按钮，type="submit"触发表单提交 -->
                <button type="submit">保存</button>
                <!-- 取消按钮，点击关闭模态窗口 -->
                <button type="button" onclick="closeEditModal()">取消</button>
            </div>
        </form>
    </div>
</div>
```

> 💡 **关键设计**：
> - 使用 `edit_` 前缀区分新增和编辑表单
> - 隐藏的 `edit_id` 字段存储机器人ID
> - 与新增模态窗口共享CSS样式

---

## 第四步：更新前端JavaScript功能（`static/script.js`）

### 1. 修改机器人主函数

```javascript
// 更新editRobot函数，打开编辑模态窗口
function editRobot() {
    // 获取用户选中的机器人ID
    const selectedRobot = getSelectedRobot();
    
    // 如果没有选择机器人，提示用户
    if (!selectedRobot) {
        alert('请先选择一个机器人');
        return;
    }
    
    // 发送GET请求获取机器人详细信息
    // URL: /api/robots/5
    fetch(`/api/robots/${selectedRobot}`)
        .then(response => response.json())  // 解析JSON响应
        .then(robot => {
            // 如果服务器返回错误
            if (robot.error) {
                alert(robot.error);
                return;
            }
            
            // 将机器人信息填充到编辑表单中
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
            // 网络错误或服务器问题
            console.error('获取机器人信息失败:', error);
            alert('获取机器人信息失败');
        });
}
```

### 2. 获取选中机器人

```javascript
// 获取选中的机器人ID
function getSelectedRobot() {
    // 查找所有被选中的复选框
    const checkboxes = document.querySelectorAll('#robotTable tbody input[type="checkbox"]:checked');
    
    // 如果没有选中任何机器人
    if (checkboxes.length === 0) {
        return null;
    }
    
    // 如果选中了多个机器人
    if (checkboxes.length > 1) {
        alert('请只选择一个机器人');
        return null;
    }
    
    // 返回选中机器人的ID（存储在data-id属性中）
    return checkboxes[0].dataset.id;
}
```

### 3. 提交编辑表单

```javascript
// 提交编辑表单
function submitEditForm(event) {
    // 阻止表单的默认提交行为（会刷新页面）
    event.preventDefault();
    
    // 获取表单中的数据
    const formData = {
        device_id: document.getElementById('edit_device_id').value,
        model: document.getElementById('edit_model').value,
        manufacturer: document.getElementById('edit_manufacturer').value,
        location: document.getElementById('edit_location').value
    };
    
    // 获取要修改的机器人ID
    const robotId = document.getElementById('edit_id').value;
    
    // 发送PUT请求到服务器
    // URL: /api/robots/5
    fetch(`/api/robots/${robotId}`, {
        method: 'PUT',  // HTTP方法：PUT表示更新
        headers: {
            'Content-Type': 'application/json'  // 告诉服务器发送的是JSON数据
        },
        body: JSON.stringify(formData)  // 将JavaScript对象转换为JSON字符串
    })
    .then(response => {
        if (response.status === 200) {
            // HTTP状态码200：更新成功
            alert('机器人信息更新成功！');
            closeEditModal();  // 关闭模态窗口
            loadRobots();      // 重新加载机器人列表
        } else if (response.status === 400) {
            // HTTP状态码400：请求错误
            return response.json().then(data => {
                alert('更新失败: ' + data.error);
            });
        }
    })
    .catch(error => {
        // 网络错误
        console.error('更新机器人信息时发生错误:', error);
        alert('更新失败，请检查网络连接');
    });
}
```

### 4. 关闭编辑模态窗口

```javascript
// 关闭编辑模态窗口
function closeEditModal() {
    // 获取模态窗口元素
    const modal = document.getElementById('editModal');
    // 隐藏模态窗口
    modal.style.display = 'none';
}
```

### 5. 更新窗口点击事件

```javascript
// 更新window.onclick函数，支持关闭两个模态窗口
window.onclick = function(event) {
    // 获取两个模态窗口元素
    const addModal = document.getElementById('addModal');
    const editModal = document.getElementById('editModal');
    
    // 如果点击了新增模态窗口的遮罩层
    if (event.target === addModal) {
        closeAddModal();
    }
    
    // 如果点击了编辑模态窗口的遮罩层
    if (event.target === editModal) {
        closeEditModal();
    }
};
```

---

## 第五步：测试修改功能

### 测试步骤：
1. **启动服务器**：`python server.py`
2. **访问系统**：`http://localhost:8000/`
3. **执行修改**：
   - 勾选一个机器人
   - 点击"修改"按钮
   - 修改部分字段（如位置）
   - 点击"保存"
4. **验证结果**：
   - 检查是否出现"更新成功"提示
   - 查看表格是否刷新并显示新数据
   - 检查数据库确认数据已更新

### 预期结果：
- 成功修改：数据正确更新
- 失败情况：
  - 未选择机器人 → 提示"请先选择"
  - 选择多个机器人 → 提示"请只选择一个"
  - 设备编号重复 → 提示"设备编号可能已存在"

---

## 数据流图（修改机器人）

```text
前端 (HTML/JavaScript)                      后端 (server.py)                           后端 (database.py)                        数据库 (SQLite)
           │                                      │                                          │                                          │
           │ 勾选机器人并点击【修改】               │                                          │                                          │
           │  getSelectedRobot()                  │                                          │                                          │
           │ ────fetch(`/api/robots/5`) ─────────>│   do_GET:            get_robot_by_id(5)  │                                          │
           │                                      │─────────────────────────────────────────>│    SELECT * FROM robots WHERE id = 5     │
           │                                      │                                          │─────────────────────────────────────────>│
           │                                      │                                          │    返回结果                               │
           │                                      │                                          │<─────────────────────────────────────────│
           │                                      │<─────────────────────────────────────────│                                          │
           │<───── 返回机器人数据 ─────────────────│                                          │                                          │
           │    填充编辑表单                       │                                          │                                          │
           │    显示编辑模态窗口                   │                                          │                                          │
           │    修改数据并点击【保存】              │                                          │                                          │
           │    submitEditForm()                  │                                          │                                          │
           │────fetch(`/api/robots/5`, PUT) ─────>│     do_PUT         update_robot(5, ...)  │                                          │
           │                                      │─────────────────────────────────────────>│                                          │
           │                                      │                                          │    UPDATE robots SET ... WHERE id = 5    │
           │                                      │                                          │─────────────────────────────────────────>│
           │                                      │                                          │    返回UPDATE 结果                        │
           │                                      │                                          │<─────────────────────────────────────────│
           │                                      │<─────────────────────────────────────────│                                          │
           │<───── 200 OK ────────────────────────│                                          │                                          │
           │    alert("更新成功")                  │                                          │                                          │
           │    closeEditModal()                  │                                          │                                          │
           │    loadRobots()                      │                                          │                                          │
```

现在您已完成迭代3，实现了机器人修改功能。请测试这个功能，确保一切正常工作，然后输入"继续"我将提供迭代4的内容。
------

代码参考 [code/01-4_Lab/M1Iteration3](code/01-4_Lab/M1Iteration3)