from MDSplus import Connection
import sys

PROXY = '127.0.0.1:8000'

def try_access(tree_name):
    print(f"\n>>> 正在尝试访问树: '{tree_name}' ...")
    try:
        conn = Connection(PROXY)
        # 这一步会发送 59 字节左右的包 (包含树名)
        conn.openTree(tree_name, 100)
        print(f"   [结果] ✅ 访问成功！(网关放行)")
        
        # 顺便读个数据证明连接健康 (仅对合法的树)
        if tree_name == 'test_tree':
            data = conn.get('para_node').data()
            print(f"   [数据] {data}")
            
    except Exception as e:
        print(f"   [结果] ❌ 访问失败！(被网关拦截)")
        print(f"   [报错] {str(e)[:100]}...")

# 1. 合法访问测试
try_access('test_tree')

# 2. 非法访问测试
try_access('secret')
