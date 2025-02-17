#! /opt/anaconda3/envs/cmpool/bin/python3
# -*- coding: utf-8 -*-
import pandas as pd
import mysql.connector
from collections import defaultdict

# 确保安装了openpyxl
try:
    import openpyxl
except ImportError:
    print("请先安装 openpyxl: pip install openpyxl")
    exit(1)

# 数据库连接配置
db_config = {
    'host': '127.0.0.1',
    'port': 3311,
    'user': 'root',
    'password': 'nov24feb11',
    'database': 'cmpool'
}

def get_cluster_ips():
    """从MySQL获取集群和IP的对应关系"""
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        cursor.execute("SELECT cluster_name, ip FROM cluster_ips")
        cluster_ip_map = defaultdict(list)
        for cluster_name, ip in cursor.fetchall():
            cluster_ip_map[cluster_name].append(ip)
            
        return cluster_ip_map
        
    except mysql.connector.Error as err:
        print(f"数据库错误: {err}")
        return None
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

def analyze_cluster_usage():
    # Define resource utilization thresholds
    THRESHOLDS = {
        'CPU': 10,    # Maximum CPU utilization threshold
        'MEM': 20,    # Maximum memory utilization threshold
        'DISK': 20    # Maximum disk utilization threshold
    }
    
    # Read Excel data
    try:
        df = pd.read_excel('server_data.xlsx', engine='openpyxl')
    except Exception as e:
        print(f"Failed to read Excel file: {e}")
        return
    
    # Get cluster-IP mapping
    cluster_ip_map = get_cluster_ips()
    if not cluster_ip_map:
        return
    
    # Analyze resource usage for each cluster
    underutilized_clusters = []
    
    for cluster_name, ips in cluster_ip_map.items():
        # Get resource usage data for all IPs in this cluster
        cluster_data = df[df['IP地址'].isin(ips)]
        
        if cluster_data.empty:
            continue
            
        # Calculate cluster-level maximum resource usage
        max_cpu = cluster_data['最大CPU'].max()
        max_mem = cluster_data['最大内存'].max()
        max_disk = cluster_data['最大磁盘'].max()
        
        # Check if resource utilization is below thresholds
        if (max_cpu < THRESHOLDS['CPU'] or 
            max_mem < THRESHOLDS['MEM'] or 
            max_disk < THRESHOLDS['DISK']):
            
            underutilized_clusters.append({
                'cluster_name': cluster_name,
                'ip_count': len(ips),
                'max_cpu': max_cpu,
                'max_mem': max_mem,
                'max_disk': max_disk
            })
    
    # Output analysis results
    if underutilized_clusters:
        print("\nClusters with Underutilized Resources:")
        print("-" * 80)
        print(f"{'Cluster Name':<15} {'IP Count':<8} {'Max CPU%':<10} {'Max Mem%':<10} {'Max Disk%':<10}")
        print("-" * 80)
        
        for cluster in underutilized_clusters:
            print(f"{cluster['cluster_name']:<15} "
                  f"{cluster['ip_count']:<8} "
                  f"{cluster['max_cpu']:<10.2f} "
                  f"{cluster['max_mem']:<10.2f} "
                  f"{cluster['max_disk']:<10.2f}")
    else:
        print("No clusters found with underutilized resources")

if __name__ == "__main__":
    analyze_cluster_usage() 