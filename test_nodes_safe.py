import time
import sys
import numpy as np
from MDSplus import Connection

# 配置
PROXY = '127.0.0.1:8000'
TREE = 'test_tree'
SHOT = 100
NODES = ['PARA_NODE', 'SIG_NODE', 'TEXT_NODE'] 

print(f"{'='*60}")
print(f" MDSplus 节点性能测试 (自动兼容模式)")
print(f"{'='*60}")
print(f"{'节点名':<12} | {'大小 (Bytes)':<12} | {'延迟 (ms)':<12}")
print(f"{'-'*60}")

latencies = []
sizes = []

try:
    c = Connection(PROXY)
    c.openTree(TREE, SHOT)
    c.get('PARA_NODE') # 预热

    for node in NODES:
        t0 = time.perf_counter()
        data = c.get(node).data()
        t1 = time.perf_counter()
        
        lat = (t1 - t0) * 1000.0
        latencies.append(lat)
        
        # 计算大小
        if hasattr(data, 'nbytes'):
            sz = data.nbytes
        elif isinstance(data, (str, bytes)):
            sz = len(data)
        else:
            sz = sys.getsizeof(data)
        sizes.append(sz)
        
        print(f"{node:<12} | {sz:<12} | {lat:.4f} ms")

    print(f"{'='*60}")

    # === 尝试画图 ===
    try:
        import matplotlib.pyplot as plt
        plt.figure(figsize=(8, 5))
        bars = plt.bar(NODES, latencies, color=['#4CAF50', '#2196F3', '#FF9800'])
        plt.ylabel('Latency (ms)')
        plt.title('Node Read Latency')
        plt.grid(axis='y', linestyle='--', alpha=0.5)
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                     f'{height:.2f}', ha='center', va='bottom')
        plt.savefig('latency_chart.png')
        print(f"✅ [高清模式] 图表已生成: latency_chart.png (请下载到本地查看)")
        
    except ImportError:
        # === 备用方案：字符画 ===
        print(f"⚠️  未检测到 Matplotlib，切换为 [字符画模式]：\n")
        print(f"Latency Visualization (Text Mode):")
        print(f"----------------------------------")
        max_lat = max(latencies) if latencies else 1
        for i, node in enumerate(NODES):
            # 计算柱子长度 (最大50个字符)
            bar_len = int((latencies[i] / max_lat) * 50)
            bar_str = '█' * bar_len
            print(f"{node:<10} | {bar_str}  {latencies[i]:.4f} ms")
        print(f"\n✅ 截图以上区域即可用于汇报！")

except Exception as e:
    print(f"❌ 错误: {e}")
