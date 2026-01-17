import sqlite3
import datetime

# 创建或连接到SQLite数据库
def create_sqlite_database():
    """创建SQLite数据库和用户行为分析所需的表"""
    try:
        # 连接到SQLite数据库（如果不存在则创建）
        conn = sqlite3.connect('user_behavior_analysis.db')
        cursor = conn.cursor()
        
        print("成功连接到SQLite数据库")
        
        # 创建用户行为日志表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_behavior_logs (
                user_id TEXT NOT NULL,
                behavior_type TEXT NOT NULL,
                behavior_time DATETIME NOT NULL,
                device_type TEXT,
                channel TEXT,
                PRIMARY KEY (user_id, behavior_time, behavior_type)
            )
        ''')
        
        # 创建用户标签结果表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_segments (
                user_id TEXT NOT NULL,
                calc_date DATE NOT NULL,
                is_active INTEGER,
                is_retained INTEGER,
                is_returning INTEGER,
                is_churned INTEGER,
                PRIMARY KEY (user_id, calc_date)
            )
        ''')
        
        # 插入一些示例数据
        sample_data = [
            ('user_001', 'login', '2023-06-28 09:30:00', 'mobile', 'appstore'),
            ('user_001', 'login', '2023-06-29 10:15:00', 'mobile', 'appstore'),
            ('user_001', 'login', '2023-06-30 11:00:00', 'mobile', 'appstore'),
            ('user_002', 'login', '2023-06-29 14:20:00', 'desktop', 'google'),
            ('user_002', 'login', '2023-06-30 15:45:00', 'desktop', 'google'),
            ('user_003', 'login', '2023-06-25 08:50:00', 'mobile', 'wechat'),
            ('user_003', 'login', '2023-06-30 09:10:00', 'mobile', 'wechat'),
            ('user_004', 'login', '2023-06-20 13:30:00', 'desktop', 'baidu'),
            ('user_004', 'login', '2023-06-30 16:20:00', 'mobile', 'appstore'),
            ('user_005', 'login', '2023-06-21 10:00:00', 'mobile', 'weibo'),
            ('user_006', 'login', '2023-06-15 17:45:00', 'desktop', 'direct'),
            ('user_007', 'login', '2023-06-30 08:30:00', 'mobile', 'appstore'),
            ('user_008', 'login', '2023-06-28 11:20:00', 'mobile', 'wechat'),
            ('user_009', 'login', '2023-06-20 09:00:00', 'desktop', 'google'),
            ('user_010', 'login', '2023-06-30 10:30:00', 'desktop', 'direct')
        ]
        
        # 插入示例数据（如果表为空）
        cursor.execute('SELECT COUNT(*) FROM user_behavior_logs')
        if cursor.fetchone()[0] == 0:
            cursor.executemany('''
                INSERT OR IGNORE INTO user_behavior_logs 
                (user_id, behavior_type, behavior_time, device_type, channel) 
                VALUES (?, ?, ?, ?, ?)
            ''', sample_data)
            print(f"已插入 {len(sample_data)} 条示例数据")
        else:
            print("表中已有数据，跳过插入示例数据")
        
        # 提交更改
        conn.commit()
        
        # 查询表结构
        print("\n数据库表结构：")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        for table in tables:
            print(f"\n表: {table[0]}")
            cursor.execute(f"PRAGMA table_info({table[0]});")
            columns = cursor.fetchall()
            for column in columns:
                print(f"  - {column[1]} ({column[2]})")
        
        # 查询示例数据
        print("\n前5条示例数据：")
        cursor.execute("SELECT * FROM user_behavior_logs LIMIT 5;")
        rows = cursor.fetchall()
        for row in rows:
            print(row)
        
        print("\nSQLite数据库创建成功！")
        return conn
        
    except sqlite3.Error as e:
        print(f"SQLite操作失败: {e}")
        return None
    
def main():
    conn = create_sqlite_database()
    if conn:
        conn.close()
        print("数据库连接已关闭")

if __name__ == "__main__":
    main()