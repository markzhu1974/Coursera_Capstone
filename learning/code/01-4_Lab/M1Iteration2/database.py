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


# 程序入口点
if __name__ == '__main__':
    # 初始化数据库
    init_database()
    # 插入示例数据
    insert_sample_data()
    print("数据库初始化完成并已添加示例数据")