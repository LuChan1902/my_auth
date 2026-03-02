from MDSplus import Connection
import sys

# 目标：连接网关 8000，验证是否能透传数据
PROXY_HOST = '127.0.0.1:8000'
TREE_NAME = 'test_tree'
SHOT_NUM = 100
NODE_NAME = 'para_node'

print(f">>> Connecting to Proxy at {PROXY_HOST}...")

try:
    # 1. 建立连接
    conn = Connection(PROXY_HOST)
    print("   [PASS] Connection established.")

    # 2. 打开树
    print(f">>> Opening Tree '{TREE_NAME}' shot {SHOT_NUM}...")
    conn.openTree(TREE_NAME, SHOT_NUM)
    print("   [PASS] Tree opened successfully.")

    # 3. 读取数据
    print(f">>> Reading data from '{NODE_NAME}'...")
    data = conn.get(NODE_NAME).data()
    
    # 4. 打印结果
    print(f"   [SUCCESS] Data Received: {data}")

except Exception as e:
    print(f"\n[FAIL] An error occurred: {e}")
