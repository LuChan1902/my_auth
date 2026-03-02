import time
import sys
import numpy as np
import matplotlib.pyplot as plt
from MDSplus import Connection

# 配置
PROXY = '127.0.0.1:8000'
TREE = 'test_tree'
SHOT = 100
NODES = ['PARA_NODE', 'SIG_NODE', 'TEXT_NODE'] # 咱们之前创建的那三个节点

print(f"{'='*60}")
print(f" MDSplus 网关节点性能测试报告")
print(f"{'='*60}")
print(f"{'节点名':<12} | {'大小 (Bytes)':<12} | {'延迟 (ms)':<12}")
print(f"{'-'*60}")

latencies = []
sizes = []

try:
    # 连接
    c = Connection(PROXY)
    c.openTree(TREE, SHOT)
    
    # 预热一次 (避免第一次连接慢影响数据)
    c.get('PARA_NODE')

    for node in NODES:
        # 1. 计时开始
        t0 = time.perf_counter()
        
        # 2. 读取数据
        data = c.get(node).data()
        
        # 3. 计时结束
        t1 = time.perf_counter()
        lat = (t1 - t0) * 1000.0
        latencies.append(lat)
        
        # 4. 计算大小
        if isinstance(data, np.ndarray):
            sz = data.nbytes
        elif isinstance(data, (str, bytes)):
            sz = len(data)
        else:
            sz = sys.getsizeof(data)
        sizes.append(sz)
        
        print(f"{node:<12} | {sz:<12} | {lat:.4f} ms")

    # 画图
    plt.figure(figsize=(8, 5))
    bars = plt.bar(NODES, latencies, color=['blue', 'green', 'orange'])
    plt.ylabel('Latency (ms)')
    plt.title('Node Read Latency via Gateway')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # 在柱子上标数字
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                 f'{height:.2f} ms', ha='center', va='bottom')
                 
    plt.savefig('latency_chart.png')
    print(f"{'='*60}")
    print(f"✅ 图表已保存为: latency_chart.png")

except Exception as e:
    print(f"❌ 错误: {e}")
