import sys
import numpy as np
from MDSplus import Connection

PROXY = '127.0.0.1:8000'
TREE = 'test_tree'
SHOT = 100
NODES = ['PARA_NODE', 'SIG_NODE', 'TEXT_NODE']

# MDSplus 固定协议头大小
MDS_HEADER_SIZE = 48 

print(f"{'='*85}")
print(f" MDSplus 真实网络数据包大小分析")
print(f"{'='*85}")
print(f"{'节点名称':<12} | {'数据载荷 (Payload)':<20} | {'协议头':<8} | {'真实传输大小 (Total)':<20}")
print(f"{'-'*85}")

try:
    c = Connection(PROXY)
    c.openTree(TREE, SHOT)

    for node in NODES:
        # 读取数据
        data = c.get(node).data()
        
        # 1. 计算数据载荷 (Payload)
        if hasattr(data, 'nbytes'):
            payload = data.nbytes  # 数组类型 (Signal/Numeric)
        elif isinstance(data, (str, bytes)):
            payload = len(data)    # 字符串类型
        elif isinstance(data, (list, tuple)):
            payload = len(data) * 4 # 列表估算
        else:
            payload = sys.getsizeof(data) # 标量估算
            
        # 2. 计算真实包大小
        total_packet_size = payload + MDS_HEADER_SIZE
        
        print(f"{node:<12} | {payload:<20} Bytes | {MDS_HEADER_SIZE} Bytes | {total_packet_size:<20} Bytes")

    print(f"{'='*85}")
    print(f"说明:")
    print(f"1. PARA_NODE:  7个数字 x 4字节 = 28 Bytes")
    print(f"2. TEXT_NODE:  字符串长度 = ~23 Bytes")
    print(f"3. SIG_NODE:   最关键！1000个点 x 4字节 = 4000 Bytes (公式被服务端展开了)")

except Exception as e:
    print(f"❌ 错误: {e}")
