"""
维修记录CSV导入工具
将CSV格式的维修记录导入SQLite数据库
"""

import sqlite3
import csv
import argparse
from datetime import datetime

def import_maintenance_from_csv(csv_file, db_file='robots.db'):
    """
    从CSV文件导入维修记录到数据库
    :param csv_file: CSV文件路径
    :param db_file: SQLite数据库文件路径
    :return: 导入成功的记录数
    """
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # 创建维修记录表（如果不存在）
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS maintenance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_id TEXT NOT NULL,
        maintenance_date TEXT NOT NULL,
        fault_code TEXT,
        fault_phenomenon TEXT,
        cause_analysis TEXT,
        measures_taken TEXT,
        replaced_parts TEXT,
        time_consumed REAL,
        maintenance_personnel TEXT,
        FOREIGN KEY (device_id) REFERENCES robots (device_id)
    )
    ''')
    
    imported_count = 0
    
    try:
        with open(csv_file, mode='r', encoding='utf-8-sig') as file:
            # 自动检测CSV方言
            dialect = csv.Sniffer().sniff(file.read(1024))
            file.seek(0)
            reader = csv.DictReader(file, dialect=dialect)
            
            # 检查必要字段
            required_fields = ['device_id', 'maintenance_date']
            for field in required_fields:
                if field not in reader.fieldnames:
                    raise ValueError(f"CSV文件缺少必要列: {field}")
            
            for row in reader:
                # 验证设备是否存在
                cursor.execute('SELECT 1 FROM robots WHERE device_id = ?', (row['device_id'],))
                if not cursor.fetchone():
                    print(f"警告: 设备 {row['device_id']} 不存在，跳过该记录")
                    continue
                
                # 解析日期
                try:
                    maintenance_date = parse_date(row['maintenance_date'])
                except ValueError as e:
                    print(f"警告: {str(e)}，使用原始值")
                    maintenance_date = row['maintenance_date']
                

                print(f"device_id: {row['device_id']}")
                print(f"maintenance_date: {maintenance_date}")
                print(f"fault_code: {row['fault_code']}")
                print(f"fault_phenomenon: {row['fault_phenomenon']}")
                print(f"cause_analysis: {row['cause_analysis']}")
                print(f"measures_taken: {row['measures_taken']}")
                print(f"replaced_parts: {row['replaced_parts']}")
                print(f"time_consumed: {float(row['time_consumed']) if row.get('time_consumed') else None}")
                print(f"maintenance_personnel: {row['maintenance_personnel']}")
                

                # 插入记录
                cursor.execute('''
                INSERT INTO maintenance (
                    device_id, maintenance_date, fault_code, fault_phenomenon,
                    cause_analysis, measures_taken, replaced_parts,
                    time_consumed, maintenance_personnel
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row['device_id'],
                    maintenance_date,
                    row.get('fault_code', ''),
                    row.get('fault_phenomenon', ''),
                    row.get('cause_analysis', ''),
                    row.get('measures_taken', ''),
                    row.get('replaced_parts', ''),
                    float(row['time_consumed']) if row.get('time_consumed') else None,
                    row.get('maintenance_personnel', '')
                ))
                
                imported_count += 1
            
            conn.commit()
            print(f"成功导入 {imported_count} 条维修记录")
            
    except Exception as e:
        conn.rollback()
        print(f"导入失败: {str(e)}")
        return 0
    finally:
        conn.close()
    
    return imported_count

def parse_date(date_str):
    """
    尝试解析多种日期格式
    :param date_str: 日期字符串
    :return: 格式化为YYYY-MM-DD的日期字符串
    """
    date_formats = [
        '%Y-%m-%d', '%Y/%m/%d', '%d/%m/%Y', 
        '%m/%d/%Y', '%Y%m%d', '%d-%m-%Y'
    ]
    
    for fmt in date_formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            continue
    
    raise ValueError(f"无法识别的日期格式: {date_str}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='导入维修记录CSV到数据库')
    parser.add_argument('csv_file', help='CSV文件路径')
    parser.add_argument('--db', default='robots.db', help='SQLite数据库文件路径 (默认: robots.db)')
    args = parser.parse_args()
    
    print(f"开始从 {args.csv_file} 导入维修记录...")
    count = import_maintenance_from_csv(args.csv_file, args.db)
    print(f"导入完成，共导入 {count} 条记录")