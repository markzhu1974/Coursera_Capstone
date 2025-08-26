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