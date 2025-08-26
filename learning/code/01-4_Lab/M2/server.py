import http.server
import socketserver
import json
import database
import os
import urllib.parse
import sqlite3

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
        

        # 如果请求路径是/api/robotsearch，处理搜索请求
        if path.startswith('/api/robotsearch'):
            # 解析查询参数
            parsed_path = urllib.parse.urlparse(self.path)
            query_params = urllib.parse.parse_qs(parsed_path.query)
            
            # 获取查询参数
            device_id = query_params.get('device_id', [None])[0]
            model = query_params.get('model', [None])[0]
            manufacturer = query_params.get('manufacturer', [None])[0]
            location = query_params.get('location', [None])[0]
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.set_cors_headers()
            self.end_headers()
            
            # 调用搜索函数
            robots = database.search_robots(device_id, model, manufacturer, location)
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
        
        # 维修记录分页查询
        if path.startswith('/api/maintenance') and not path.startswith('/api/maintenance/search'):
            parsed_path = urllib.parse.urlparse(self.path)
            query_params = urllib.parse.parse_qs(parsed_path.query)
            
            # 处理分页参数
            page = int(query_params.get('page', [1])[0])
            per_page = int(query_params.get('per_page', [10])[0])
            
            # 计算偏移量
            offset = (page - 1) * per_page
            
            conn = sqlite3.connect('robots.db')
            cursor = conn.cursor()
            
            # 获取总记录数
            cursor.execute('SELECT COUNT(*) FROM maintenance')
            total_records = cursor.fetchone()[0]
            
            # 获取当前页记录
            cursor.execute('''
            SELECT id, device_id, maintenance_date, fault_code, 
                fault_phenomenon, maintenance_personnel
            FROM maintenance
            ORDER BY maintenance_date DESC
            LIMIT ? OFFSET ?
            ''', (per_page, offset))
            
            records = []
            for row in cursor.fetchall():
                records.append({
                    'id': row[0],
                    'device_id': row[1],
                    'maintenance_date': row[2],
                    'fault_code': row[3],
                    'fault_phenomenon': row[4],
                    'maintenance_personnel': row[5]
                })
            
            conn.close()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                'records': records,
                'total_records': total_records,
                'current_page': page,
                'per_page': per_page
            }
            self.wfile.write(json.dumps(response).encode())
            return
        
        # 维修记录搜索
        if path.startswith('/api/maintenance/search'):
            print('进入维修记录搜索/api/maintenance/search')

            parsed_path = urllib.parse.urlparse(self.path)
            query_params = urllib.parse.parse_qs(parsed_path.query)
            device_id = query_params.get('device_id', [None])[0] 
            
            print(f'parsed_path: [{parsed_path}]')
            print(f'query_params: [{query_params}]')
            print(f'device_id: [{device_id}]')
            
            conn = sqlite3.connect('robots.db')
            cursor = conn.cursor()

            cursor.execute('''
            SELECT id, device_id, maintenance_date, fault_code, 
                fault_phenomenon, maintenance_personnel
            FROM maintenance
            WHERE device_id = ?
            ORDER BY maintenance_date DESC
            ''', (device_id,))

            print('执行完查找维修记录的SQL语句')

            rows = cursor.fetchall()
            print(rows)

            records = []
            for row in rows:
                records.append({
                    'id': row[0],
                    'device_id': row[1],
                    'maintenance_date': row[2],
                    'fault_code': row[3],
                    'fault_phenomenon': row[4],
                    'maintenance_personnel': row[5]
                })
            
            conn.close()

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                'records': records,
                'total_records': len(records)
            }

            self.wfile.write(json.dumps(response).encode())
            return

        
        # 单个维修记录详情
        if path.startswith('/api/mrdetail/'):
            record_id = self.path.split('/')[-1]
            print('record_id:', record_id) 

            conn = sqlite3.connect('robots.db')
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT * FROM maintenance WHERE id = ?
            ''', (record_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                record = {
                    'id': row[0],
                    'device_id': row[1],
                    'maintenance_date': row[2],
                    'fault_code': row[3],
                    'fault_phenomenon': row[4],
                    'cause_analysis': row[5],
                    'measures_taken': row[6],
                    'replaced_parts': row[7],
                    'time_consumed': row[8],
                    'maintenance_personnel': row[9]
                }
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(record).encode())
            else:
                self.send_response(404)
                self.end_headers()
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

        # 处理维修记录添加请求
        elif self.path == '/api/mradd':
            print('进入维修记录添加/api/mradd')
            
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                print('解析后的数据:', data)

                # 调用数据库函数添加维修记录
                success = database.add_maintenance_record(
                    data.get('device_id', ''),           # 如果不存在则赋空字符串
                    data.get('maintenance_date', ''),
                    data.get('fault_code', ''),
                    data.get('fault_phenomenon', ''),
                    data.get('cause_analysis', ''),
                    data.get('measures_taken', ''),
                    data.get('replaced_parts', ''),
                    data.get('time_consumed', ''),
                    data.get('maintenance_personnel', '')
                )
                
                if success:
                    self.send_response(201)
                    self.send_header('Content-type', 'application/json')
                    self.set_cors_headers()
                    self.end_headers()
                    response = {'message': '维修记录添加成功'}
                    self.wfile.write(json.dumps(response).encode())
                else:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.set_cors_headers()
                    self.end_headers()
                    response = {'error': '添加失败，设备编号可能不存在'}
                    self.wfile.write(json.dumps(response).encode())
                    
            except json.JSONDecodeError:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.set_cors_headers()
                self.end_headers()
                response = {'error': '无效的JSON数据'}
                self.wfile.write(json.dumps(response).encode())
            except KeyError as e:
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

    # 在RobotHandler类中添加do_DELETE方法
    def do_DELETE(self):
        # 处理/api/robots/的DELETE请求
        if self.path.startswith('/api/robots/'):
            # 从URL路径中提取机器人ID
            robot_id = self.path.split('/')[-1]
            
            # 调用数据库函数删除机器人
            success = database.delete_robot(robot_id)
            
            if success:
                # 删除成功，返回200状态码
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.set_cors_headers()
                self.end_headers()
                response = {'message': '机器人删除成功'}
                self.wfile.write(json.dumps(response).encode())
            else:
                # 删除失败，返回404状态码
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.set_cors_headers()
                self.end_headers()
                response = {'error': '删除失败，记录不存在'}
                self.wfile.write(json.dumps(response).encode())
        else:
            # 对于其他DELETE请求返回404
            self.send_response(404)
            self.end_headers()


# 程序入口点
if __name__ == '__main__':
    # 初始化数据库
    database.init_database()
    database.insert_sample_data()
    database.insert_maintenance_data()
    
    # 创建TCP服务器实例
    with socketserver.TCPServer(("", PORT), RobotHandler) as httpd:
        print(f"服务器运行在端口 {PORT}")
        print("打开浏览器访问: http://localhost:8000/")
        print("静态文件目录: ", os.getcwd())
        # 启动服务器，持续处理请求
        httpd.serve_forever()