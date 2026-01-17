import sqlite3
import datetime

# =========================================
# 1. 配置参数（可根据业务需求调整）
# =========================================

# 定义观察日期
OBSERVATION_DATE = '2023-06-30'

# 活跃行为定义：这里仅包含login行为
ACTIVE_BEHAVIOR = 'login'

# 时间周期配置（单位：天）
ACTIVE_WINDOW = 1          # 活跃用户的观察窗口（日活）
RETENTION_BASE_PERIOD = 1   # 留存用户的基准周期（前一天）
RETENTION_TARGET_PERIOD = 1 # 留存用户的目标周期（次日）
CHURN_THRESHOLD = 7         # 流失用户的连续不活跃天数阈值
RETURN_CHURN_PERIOD = 7     # 回流用户的流失观察窗口（至少7天不活跃）

# =========================================
# 2. 连接到SQLite数据库
# =========================================

def connect_to_database():
    """连接到SQLite数据库"""
    try:
        conn = sqlite3.connect('user_behavior_analysis.db')
        # 启用外键约束
        conn.execute("PRAGMA foreign_keys = ON;")
        print("成功连接到SQLite数据库")
        return conn
    except sqlite3.Error as e:
        print(f"数据库连接失败: {e}")
        return None

# =========================================
# 3. 计算活跃用户
# =========================================

def calculate_active_users(conn):
    """计算活跃用户"""
    cursor = conn.cursor()
    
    # 计算观察日期的起始时间
    obs_start_date = datetime.datetime.strptime(OBSERVATION_DATE, '%Y-%m-%d') - datetime.timedelta(days=ACTIVE_WINDOW)
    obs_start_str = obs_start_date.strftime('%Y-%m-%d')
    
    query = '''
    SELECT DISTINCT user_id
    FROM user_behavior_logs
    WHERE behavior_type = ?
    AND behavior_time BETWEEN datetime(?) AND datetime(?)
    '''
    
    cursor.execute(query, (ACTIVE_BEHAVIOR, f'{obs_start_str} 00:00:00', f'{OBSERVATION_DATE} 23:59:59'))
    active_users = {row[0] for row in cursor.fetchall()}
    
    cursor.close()
    return active_users

# =========================================
# 4. 计算留存用户（次日留存示例）
# =========================================

def calculate_retention_users(conn):
    """计算留存用户"""
    cursor = conn.cursor()
    
    # 计算基准日期
    base_date = datetime.datetime.strptime(OBSERVATION_DATE, '%Y-%m-%d') - datetime.timedelta(days=RETENTION_BASE_PERIOD + RETENTION_TARGET_PERIOD)
    base_date_str = base_date.strftime('%Y-%m-%d')
    
    # 计算目标日期
    target_date = datetime.datetime.strptime(OBSERVATION_DATE, '%Y-%m-%d') - datetime.timedelta(days=RETENTION_TARGET_PERIOD)
    target_date_str = target_date.strftime('%Y-%m-%d')
    
    query = '''
    SELECT DISTINCT b.user_id
    FROM (
        SELECT user_id
        FROM user_behavior_logs
        WHERE behavior_type = ?
        AND behavior_time BETWEEN datetime(?) AND datetime(?)
    ) b
    INNER JOIN user_behavior_logs u ON b.user_id = u.user_id
    WHERE u.behavior_type = ?
    AND u.behavior_time BETWEEN datetime(?) AND datetime(?)
    '''
    
    cursor.execute(query, (
        ACTIVE_BEHAVIOR, f'{base_date_str} 00:00:00', f'{target_date_str} 23:59:59',
        ACTIVE_BEHAVIOR, f'{target_date_str} 00:00:00', f'{OBSERVATION_DATE} 23:59:59'
    ))
    retained_users = {row[0] for row in cursor.fetchall()}
    
    cursor.close()
    return retained_users

# =========================================
# 5. 计算回流用户
# =========================================

def calculate_returning_users(conn):
    """计算回流用户"""
    cursor = conn.cursor()
    
    # 计算观察日期的起始时间
    obs_start_date = datetime.datetime.strptime(OBSERVATION_DATE, '%Y-%m-%d') - datetime.timedelta(days=ACTIVE_WINDOW)
    obs_start_str = obs_start_date.strftime('%Y-%m-%d')
    
    # 计算流失观察窗口的起始时间
    return_start_date = datetime.datetime.strptime(OBSERVATION_DATE, '%Y-%m-%d') - datetime.timedelta(days=ACTIVE_WINDOW + RETURN_CHURN_PERIOD)
    return_start_str = return_start_date.strftime('%Y-%m-%d')
    
    query = '''
    SELECT DISTINCT user_id
    FROM user_behavior_logs
    GROUP BY user_id
    HAVING 
        -- 在观察周期内活跃
        MAX(CASE WHEN behavior_type = ? 
                 AND behavior_time BETWEEN datetime(?) AND datetime(?) 
                 THEN behavior_time END) IS NOT NULL
        -- 在前@return_churn_period天内不活跃
        AND MAX(CASE WHEN behavior_type = ? 
                 AND behavior_time BETWEEN datetime(?) AND datetime(?) 
                 THEN behavior_time END) IS NULL
        -- 更早的时间曾活跃过
        AND MAX(CASE WHEN behavior_type = ? 
                 AND behavior_time < datetime(?) 
                 THEN behavior_time END) IS NOT NULL
    '''
    
    cursor.execute(query, (
        ACTIVE_BEHAVIOR, f'{obs_start_str} 00:00:00', f'{OBSERVATION_DATE} 23:59:59',
        ACTIVE_BEHAVIOR, f'{return_start_str} 00:00:00', f'{obs_start_str} 00:00:00',
        ACTIVE_BEHAVIOR, f'{return_start_str} 00:00:00'
    ))
    returning_users = {row[0] for row in cursor.fetchall()}
    
    cursor.close()
    return returning_users

# =========================================
# 6. 计算流失用户
# =========================================

def calculate_churned_users(conn):
    """计算流失用户"""
    cursor = conn.cursor()
    
    # 计算流失观察窗口的起始时间
    churn_start_date = datetime.datetime.strptime(OBSERVATION_DATE, '%Y-%m-%d') - datetime.timedelta(days=CHURN_THRESHOLD)
    churn_start_str = churn_start_date.strftime('%Y-%m-%d')
    
    query = '''
    SELECT DISTINCT user_id
    FROM user_behavior_logs
    GROUP BY user_id
    HAVING 
        -- 在观察周期内不活跃
        MAX(CASE WHEN behavior_type = ? 
                 AND behavior_time BETWEEN datetime(?) AND datetime(?) 
                 THEN behavior_time END) IS NULL
        -- 更早的时间曾活跃过
        AND MAX(CASE WHEN behavior_type = ? 
                 AND behavior_time < datetime(?) 
                 THEN behavior_time END) IS NOT NULL
    '''
    
    cursor.execute(query, (
        ACTIVE_BEHAVIOR, f'{churn_start_str} 00:00:00', f'{OBSERVATION_DATE} 23:59:59',
        ACTIVE_BEHAVIOR, f'{churn_start_str} 00:00:00'
    ))
    churned_users = {row[0] for row in cursor.fetchall()}
    
    cursor.close()
    return churned_users

# =========================================
# 7. 获取所有用户列表
# =========================================

def get_all_users(conn):
    """获取所有用户列表"""
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT user_id FROM user_behavior_logs;")
    users = [row[0] for row in cursor.fetchall()]
    cursor.close()
    return users

# =========================================
# 8. 保存标签结果到数据库
# =========================================

def save_user_segments(conn, users, active_users, retained_users, returning_users, churned_users):
    """保存用户标签结果到数据库"""
    cursor = conn.cursor()
    
    # 准备插入数据
    segments_data = []
    for user_id in users:
        is_active = 1 if user_id in active_users else 0
        is_retained = 1 if user_id in retained_users else 0
        is_returning = 1 if user_id in returning_users else 0
        is_churned = 1 if user_id in churned_users else 0
        
        segments_data.append((user_id, OBSERVATION_DATE, is_active, is_retained, is_returning, is_churned))
    
    # 插入或更新标签结果
    cursor.executemany('''
        INSERT OR REPLACE INTO user_segments 
        (user_id, calc_date, is_active, is_retained, is_returning, is_churned)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', segments_data)
    
    conn.commit()
    print(f"已保存 {len(segments_data)} 用户的标签结果")
    cursor.close()

# =========================================
# 9. 查询标签统计结果
# =========================================

def query_segment_statistics(conn):
    """查询标签统计结果"""
    cursor = conn.cursor()
    
    query = '''
    SELECT 
        COUNT(*) AS total_users,
        SUM(is_active) AS active_users,
        SUM(is_retained) AS retained_users,
        SUM(is_returning) AS returning_users,
        SUM(is_churned) AS churned_users
    FROM user_segments
    WHERE calc_date = ?
    '''
    
    cursor.execute(query, (OBSERVATION_DATE,))
    stats = cursor.fetchone()
    
    print("\n=== 用户标签统计 ===")
    print(f"观察日期: {OBSERVATION_DATE}")
    print(f"总用户数: {stats[0]}")
    print(f"活跃用户数: {stats[1]}")
    print(f"留存用户数: {stats[2]}")
    print(f"回流用户数: {stats[3]}")
    print(f"流失用户数: {stats[4]}")
    
    # 计算百分比
    if stats[0] > 0:
        print(f"\n百分比:")
        print(f"活跃用户占比: {stats[1]/stats[0]*100:.1f}%")
        print(f"留存用户占比: {stats[2]/stats[0]*100:.1f}%")
        print(f"回流用户占比: {stats[3]/stats[0]*100:.1f}%")
        print(f"流失用户占比: {stats[4]/stats[0]*100:.1f}%")
    
    cursor.close()

# =========================================
# 10. 查询具体用户的标签
# =========================================

def query_user_segments(conn):
    """查询具体用户的标签"""
    cursor = conn.cursor()
    
    query = '''
    SELECT 
        user_id,
        calc_date,
        CASE WHEN is_active THEN '是' ELSE '否' END AS 活跃用户,
        CASE WHEN is_retained THEN '是' ELSE '否' END AS 留存用户,
        CASE WHEN is_returning THEN '是' ELSE '否' END AS 回流用户,
        CASE WHEN is_churned THEN '是' ELSE '否' END AS 流失用户
    FROM user_segments
    WHERE calc_date = ?
    ORDER BY user_id
    '''
    
    cursor.execute(query, (OBSERVATION_DATE,))
    users = cursor.fetchall()
    
    print("\n=== 具体用户标签 ===")
    for user in users:
        print(f"用户ID: {user[0]}, 计算日期: {user[1]}, 活跃用户: {user[2]}, 留存用户: {user[3]}, 回流用户: {user[4]}, 流失用户: {user[5]}")
    
    cursor.close()

# =========================================
# 11. 主函数
# =========================================

def main():
    print("开始计算用户人群标签...")
    
    # 连接到数据库
    conn = connect_to_database()
    if not conn:
        return
    
    try:
        # 获取所有用户列表
        print(f"获取所有用户列表...")
        all_users = get_all_users(conn)
        print(f"共找到 {len(all_users)} 个用户")
        
        # 计算各类用户
        print(f"计算活跃用户...")
        active_users = calculate_active_users(conn)
        print(f"活跃用户数: {len(active_users)}")
        
        print(f"计算留存用户...")
        retained_users = calculate_retention_users(conn)
        print(f"留存用户数: {len(retained_users)}")
        
        print(f"计算回流用户...")
        returning_users = calculate_returning_users(conn)
        print(f"回流用户数: {len(returning_users)}")
        
        print(f"计算流失用户...")
        churned_users = calculate_churned_users(conn)
        print(f"流失用户数: {len(churned_users)}")
        
        # 保存标签结果
        print(f"保存用户标签结果...")
        save_user_segments(conn, all_users, active_users, retained_users, returning_users, churned_users)
        
        # 查询统计结果
        query_segment_statistics(conn)
        
        # 查询具体用户标签
        query_user_segments(conn)
        
    except Exception as e:
        print(f"计算过程中发生错误: {e}")
        conn.rollback()
    finally:
        # 关闭数据库连接
        conn.close()
        print("\n数据库连接已关闭")

# =========================================
# 12. 运行主函数
# =========================================

if __name__ == "__main__":
    main()