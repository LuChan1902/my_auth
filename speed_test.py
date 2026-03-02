import time
import statistics
from MDSplus import Connection

PROXY = '127.0.0.1:8000'
NODE = 'para_node'

print(f">>> 正在连接网关 {PROXY}...")
conn = Connection(PROXY)
conn.openTree('test_tree', 100)
print(f">>> 连接成功，开始 100 次连续读取测试...\n")

latencies = []

# 预热一次 (排除连接建立的开销)
conn.get(NODE).data()

# 循环测试 100 次
for i in range(100):
    # 记录开始时间 (微秒级精度)
    t_start = time.perf_counter()
    
    # 执行数据读取
    data = conn.get(NODE).data()
    
    # 记录结束时间
    t_end = time.perf_counter()
    
    # 计算耗时 (毫秒)
    cost_ms = (t_end - t_start) * 1000
    latencies.append(cost_ms)
    
    # 打印前3次的数据，证明通了 (满足你“读取三个数据”的要求)
    if i < 3:
        print(f"  [第 {i+1} 次读取] 耗时: {cost_ms:.4f} ms | 数据: {data}")

# 统计结果
avg_lat = statistics.mean(latencies)
max_lat = max(latencies)
min_lat = min(latencies)

print(f"\n" + "="*30)
print(f" 📊 传输效率测试报告")
print(f"="*30)
print(f" 平均延迟 (Avg): {avg_lat:.4f} ms")
print(f" 最大延迟 (Max): {max_lat:.4f} ms")
print(f" 最小延迟 (Min): {min_lat:.4f} ms")
print(f"="*30)
