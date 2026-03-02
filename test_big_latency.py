import time
import sys
import numpy as np
from MDSplus import Connection

PROXY = '127.0.0.1:8000'
TREE = 'test_tree'
NODE = 'BIG_NODE'
ROUNDS = 5 

print(f"{'='*70}")
print(f" MDSplus 100MB 大数据压力测试 (Port 8000)")
print(f"{'='*70}")
print(f"{'轮次':<6} | {'耗时 (秒)':<12} | {'延迟 (ms)':<15} | {'吞吐量 (MB/s)':<15}")
print(f"{'-'*70}")

latencies = []
throughputs = []

try:
    c = Connection(PROXY)
    c.openTree(TREE, 100)
    
    # 获取一下数据大小
    print(">>> 正在预热 (第一次读取)...")
    data = c.get(NODE).data()
    
    # 真实计算字节数
    if hasattr(data, 'nbytes'):
        data_size_bytes = data.nbytes
    else:
        data_size_bytes = len(data) * 4 # 估算
        
    data_size_mb = data_size_bytes / (1024 * 1024)
    print(f">>> 数据大小确认: {data_size_bytes:,} Bytes ({data_size_mb:.2f} MiB)")
    print(f"{'-'*70}")

    for i in range(ROUNDS):
        t0 = time.perf_counter()
        
        # 读取 100MB
        temp = c.get(NODE).data()
        
        t1 = time.perf_counter()
        duration = t1 - t0
        latency_ms = duration * 1000.0
        
        # 计算吞吐量
        throughput = data_size_mb / duration if duration > 0 else 0
        
        latencies.append(latency_ms)
        throughputs.append(throughput)
        
        print(f"#{i+1:<5} | {duration:.4f} s     | {latency_ms:.2f} ms      | {throughput:.2f} MB/s")

    avg_lat = np.mean(latencies)
    max_lat = np.max(latencies)
    avg_thru = np.mean(throughputs)

    print(f"{'='*70}")
    print(f"📊 测试总结:")
    print(f"  - 平均延迟: {avg_lat:.2f} ms")
    print(f"  - 最大延迟: {max_lat:.2f} ms")
    print(f"  - 平均带宽: {avg_thru:.2f} MB/s")

except Exception as e:
    print(f"❌ [错误] {e}")
