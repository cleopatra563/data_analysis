import mysql.connector
from mysql.connector import Error

# 配置连接参数（使用默认的root用户和空密码，可根据实际情况修改）
config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'port': 3306,
    'database': '',
    'auth_plugin': 'mysql_native_password'
}

def test_mysql_connection():
    """测试MySQL数据库连接"""
    connection = None
    try:
        # 尝试连接到MySQL服务器（不指定数据库）
        connection = mysql.connector.connect(
            user=config['user'],
            password=config['password'],
            host=config['host'],
            port=config['port'],
            auth_plugin=config['auth_plugin']
        )
        if connection.is_connected():
            db_info = connection.get_server_info()
            print(f"成功连接到MySQL服务器，版本: {db_info}")
            
            # 创建游标对象
            cursor = connection.cursor()
            
            # 显示所有数据库
            print("\n可用的数据库列表:")
            cursor.execute("SHOW DATABASES;")
            databases = cursor.fetchall()
            for db in databases:
                print(f"- {db[0]}")
            
            # 尝试创建用户行为分析数据库（如果不存在）
            database_name = "user_behavior_analysis"
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            print(f"\n已确保数据库 '{database_name}' 存在")
            
            # 切换到创建的数据库
            cursor.execute(f"USE {database_name};")
            print(f"已切换到数据库 '{database_name}'")
            
            # 显示当前数据库中的表
            print(f"\n数据库 '{database_name}' 中的表列表:")
            cursor.execute("SHOW TABLES;")
            tables = cursor.fetchall()
            for table in tables:
                print(f"- {table[0]}")
            
            cursor.close()
            return True, connection, database_name
            
    except Error as e:
        print(f"连接失败: {e}")
        print("提示：请检查MySQL服务是否运行，以及用户名和密码是否正确。")
        return False, None, None

def main():
    print("开始测试MySQL连接...")
    success, connection, database_name = test_mysql_connection()
    
    if success and connection.is_connected():
        print("\n连接测试完成，正在关闭连接...")
        connection.close()
        print("连接已关闭")
    else:
        print("\n连接测试失败，请检查配置")

if __name__ == "__main__":
    main()