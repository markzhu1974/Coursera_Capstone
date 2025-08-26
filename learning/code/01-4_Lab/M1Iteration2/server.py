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

    # 在RobotHandler类中添加do_POST方法
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

# 程序入口点
if __name__ == '__main__':
    # 初始化数据库
    database.init_database()
    database.insert_sample_data()
    
    # 创建TCP服务器实例
    with socketserver.TCPServer(("", PORT), RobotHandler) as httpd:
        print(f"服务器运行在端口 {PORT}")
        print("打开浏览器访问: http://localhost:8000/")
        # 启动服务器，持续处理请求
        httpd.serve_forever()