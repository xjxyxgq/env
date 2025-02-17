#! /opt/anaconda3/envs/cmpool/bin/python3
# -*- coding: utf-8 -*-
import random
import mysql.connector

def read_unique_ips():
    with open('unique_ips.txt', 'r') as f:
        return [line.strip() for line in f]

# 创建更多的集群名称
def generate_cluster_names():
    # 假设我们有1000个IP，每个集群最多5台机器
    # 那么至少需要 200 个集群 (1000/5)
    # 为了更均匀分配，我们创建250个集群
    return [f"cluster-{i:03d}" for i in range(1, 251)]

def distribute_ips_to_clusters(ips, cluster_names):
    """将IP均匀分配到集群中，确保每个集群不超过5台机器"""
    data = []
    ip_index = 0
    
    # 随机打乱IP列表和集群名称
    random.shuffle(ips)
    random.shuffle(cluster_names)
    
    # 计算基础分配数量（每个集群的最小机器数）
    total_ips = len(ips)
    total_clusters = len(cluster_names)
    base_count = min(total_ips // total_clusters, 5)  # 不超过5台
    
    # 分配IP到集群
    for cluster_name in cluster_names:
        # 随机决定这个集群分配几台机器（1到5之间）
        cluster_size = min(random.randint(1, 5), len(ips) - ip_index)
        if cluster_size <= 0:
            break
            
        # 分配IP到当前集群
        cluster_ips = ips[ip_index:ip_index + cluster_size]
        for ip in cluster_ips:
            data.append((cluster_name, ip))
        
        ip_index += cluster_size
        
        # 如果所有IP都已分配完，就退出
        if ip_index >= len(ips):
            break
    
    return data

# 数据库连接配置
db_config = {
    'host': '127.0.0.1',
    'port': 3311,
    'user': 'root',
    'password': 'nov24feb11',
    'database': 'cmpool'
}

def main():
    # 读取IP列表
    unique_ips = read_unique_ips()
    
    # 生成集群名称
    cluster_names = generate_cluster_names()
    
    # 分配IP到集群
    data = distribute_ips_to_clusters(unique_ips, cluster_names)
    
    # 创建表的SQL
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS cluster_ips (
        cluster_name VARCHAR(50) NOT NULL,
        ip VARCHAR(15) NOT NULL,
        PRIMARY KEY (cluster_name, ip),
        UNIQUE KEY unique_ip (ip)
    );
    """
    
    # 连接数据库并插入数据
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # 创建表
        cursor.execute(create_table_sql)
        
        # 清空现有数据
        cursor.execute("TRUNCATE TABLE cluster_ips")
        
        # 插入数据
        insert_query = "INSERT INTO cluster_ips (cluster_name, ip) VALUES (%s, %s)"
        cursor.executemany(insert_query, data)
        
        conn.commit()
        
        # 打印统计信息
        cursor.execute("""
            SELECT cluster_name, COUNT(*) as count 
            FROM cluster_ips 
            GROUP BY cluster_name 
            ORDER BY count DESC 
            LIMIT 5
        """)
        print("\nSample cluster sizes (top 5):")
        print(f"{'Cluster Name':<15} {'Machine Count':<5}")
        print("-" * 25)
        for cluster_name, count in cursor.fetchall():
            print(f"{cluster_name:<15} {count:<5}")
            
        print(f"\nTotal clusters created: {len(set(x[0] for x in data))}")
        print(f"Total IPs distributed: {len(data)}")
        
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
    
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    main() 