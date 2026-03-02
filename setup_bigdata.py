import numpy as np
from MDSplus import Tree, Connection, Data

PROXY = '127.0.0.1:8000'
TREE = 'test_tree'
NODE_NAME = 'BIG_NODE'

print(f">>> 正在准备 100MB 数据节点...")

try:
    # 1. 修改树结构，添加节点 (如果不存在)
    # 注意：这里我们直连本地文件系统修改结构，避免网关权限问题干扰结构编辑
    try:
        t = Tree(TREE, -1, 'EDIT')
        try:
            t.addNode(NODE_NAME, 'NUMERIC')
            t.write()
            print(f"   [结构] 节点 {NODE_NAME} 创建成功。")
        except Exception as e:
            print(f"   [结构] 节点已存在或创建跳过 ({e})")
        finally:
            t.close()
    except Exception as e:
        print(f"   [警告] 无法编辑树结构 (可能已存在): {e}")

    # 2. 生成 100MB 数据 (2500万个 float32)
    # 25,000,000 * 4 bytes = 100,000,000 bytes = 95.36 MiB
    print(f"   [生成] 正在生成 25,000,000 个浮点数 (约 100MB RAM)...")
    big_data = np.random.rand(25000000).astype(np.float32)
    
    # 3. 通过网关写入数据
    print(f"   [写入] 正在通过网关 ({PROXY}) 写入数据，请稍候...")
    conn = Connection(PROXY)
    conn.openTree(TREE, 100)
    
    # putData 可能比较慢，请耐心等待
    conn.get(NODE_NAME).putData(big_data)
    
    print(f"✅ [成功] 100MB 数据已写入 {NODE_NAME}！")

except Exception as e:
    print(f"❌ [失败] {e}")
