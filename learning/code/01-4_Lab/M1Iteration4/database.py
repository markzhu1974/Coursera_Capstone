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


# 添加新增机器人函数
def add_robot(device_id, model, manufacturer, location):
    conn = sqlite3.connect('robots.db')
    cursor = conn.cursor()
    
    try:
        # 插入新的机器人记录
        cursor.execute(
            'INSERT INTO robots (device_id, model, manufacturer, location) VALUES (?, ?, ?, ?)',
            (device_id, model, manufacturer, location)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # 处理唯一性约束错误（设备编号重复）
        print(f"错误：设备编号 {device_id} 已存在")
        return False
    except Exception as e:
        # 处理其他异常
        print(f"插入数据时发生错误: {e}")
        return False
    finally:
        conn.close()

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

# 添加查询机器人函数（支持多条件查询）
def search_robots(device_id=None, model=None, manufacturer=None, location=None):
    conn = sqlite3.connect('robots.db')
    cursor = conn.cursor()
    
    # 构建基础查询语句
    query = 'SELECT id, device_id, model, manufacturer, location FROM robots WHERE 1=1'
    params = []
    
    # 根据提供的参数添加查询条件
    if device_id:
        query += ' AND device_id LIKE ?'
        params.append(f'%{device_id}%')
    if model:
        query += ' AND model LIKE ?'
        params.append(f'%{model}%')
    if manufacturer:
        query += ' AND manufacturer LIKE ?'
        params.append(f'%{manufacturer}%')
    if location:
        query += ' AND location LIKE ?'
        params.append(f'%{location}%')
    
    # 执行查询
    cursor.execute(query, params)
    robots = cursor.fetchall()
    
    conn.close()
    return robots

# 添加删除机器人函数
def delete_robot(robot_id):
    conn = sqlite3.connect('robots.db')
    cursor = conn.cursor()
    
    try:
        # 删除指定ID的机器人
        cursor.execute('DELETE FROM robots WHERE id = ?', (robot_id,))
        conn.commit()
        
        # 返回是否成功删除了记录
        return cursor.rowcount > 0
    except Exception as e:
        # 处理异常
        print(f"删除数据时发生错误: {e}")
        return False
    finally:
        conn.close()

# 添加批量删除机器人函数
def delete_robots(robot_ids):
    conn = sqlite3.connect('robots.db')
    cursor = conn.cursor()
    
    try:
        # 使用IN语句批量删除
        placeholders = ','.join('?' for _ in robot_ids)
        query = f'DELETE FROM robots WHERE id IN ({placeholders})'
        
        cursor.execute(query, robot_ids)
        conn.commit()
        
        # 返回成功删除的记录数
        return cursor.rowcount
    except Exception as e:
        # 处理异常
        print(f"批量删除数据时发生错误: {e}")
        return 0
    finally:
        conn.close()

        

# 程序入口点
if __name__ == '__main__':
    # 初始化数据库
    init_database()
    # 插入示例数据
    insert_sample_data()
    print("数据库初始化完成并已添加示例数据")