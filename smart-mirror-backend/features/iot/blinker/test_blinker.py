# 简单的blinker库测试脚本
print("测试blinker库导入...")
try:
    from blinker import Blinker
    print("✓ blinker库导入成功")
    
    # 测试基本初始化
    BLINKER_WIFI = False
    blinker = Blinker("test-key")
    print("✓ Blinker初始化成功")
    
    print("所有测试通过!")
except Exception as e:
    print(f"✗ 测试失败: {e}")
    import traceback
    traceback.print_exc()