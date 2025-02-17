#! /opt/anaconda3/envs/cmpool/bin/python3
# -*- coding: utf-8 -*-
import pandas as pd
import random
import faker
from ipaddress import IPv4Address

# 生成假数据
fake = faker.Faker()

# 部门和团队的随机数据
departments = ['IT', '研发', '市场', '运营', '人事']
teams = ['A团队', 'B团队', 'C团队', 'D团队', 'E团队']
applications = ['应用A', '应用B', '应用C', '应用D', '应用E']
server_types = ['物理机', '虚拟机']

# 生成唯一的IP地址列表
def generate_unique_ips(count):
    ips = set()
    while len(ips) < count:
        ip_int = random.randint(167772160, 3232235519)  # 10.0.0.0 到 192.168.255.255 范围
        ip = str(IPv4Address(ip_int))
        ips.add(ip)
    return list(ips)

# 生成1000个唯一的IP地址
unique_ips = generate_unique_ips(1000)

# 生成1000行数据
data = []
for ip in unique_ips:
    department = random.choice(departments)
    team = random.choice(teams)
    application = random.choice(applications)
    server_type = random.choice(server_types)
    max_cpu = round(random.uniform(0, 100), 2)
    avg_cpu = round(random.uniform(0, 100), 2)
    max_memory = round(random.uniform(0, 100), 2)
    avg_memory = round(random.uniform(0, 100), 2)
    max_disk = round(random.uniform(0, 100), 2)
    avg_disk = round(random.uniform(0, 100), 2)
    
    data.append([department, team, ip, application, server_type, max_cpu, avg_cpu, max_memory, avg_memory, max_disk, avg_disk])

# 创建DataFrame并保存
df = pd.DataFrame(data, columns=[
    '部门', '团队', 'IP地址', '应用', '服务器类型', 
    '最大CPU', '平均CPU', '最大内存', '平均内存', '最大磁盘', '平均磁盘'
])

# 保存为Excel文件
df.to_excel('server_data.xlsx', index=False, engine='openpyxl')

# 保存IP列表供其他脚本使用
with open('unique_ips.txt', 'w') as f:
    for ip in unique_ips:
        f.write(f"{ip}\n")

print("Excel file output done: server_data.xlsx")
print("IP list saved: unique_ips.txt")
