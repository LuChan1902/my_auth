from MDSplus import Connection

def test_connection(password):
    print(f">>> 提交鉴权凭证: [{password}]")
    try:
        conn = Connection('127.0.0.1:8000')
        
        # 1. 触发网关 DPI 安检
        conn.get(f'"{password}"')
        
        # 2. 安检通过，开始真实的业务逻辑
        conn.openTree('test_tree', 100)
        
        # 3. 读取数值节点
        para_data = conn.get('para_node').data()
        print(f"    [+] para_node (数值型) 读取成功: {para_data}")
        
        # 4. 读取文本节点
        text_data = conn.get('text_node').data()
        # 将字节流解码为字符串显示，证明数据完整性
        if isinstance(text_data, bytes):
            text_data = text_data.decode('utf-8')
        print(f"    [+] text_node (文本型) 读取成功: {text_data}")
        
    except Exception as e:
        print(f"    [-] 访问被拒绝，连接已断开")
    print("-" * 50)

# 测试一：合法凭证
test_connection("654321")

# 测试二：非法凭证
test_connection("000000")
