import os
import sys
import pytest

if __name__ == "__main__":
    # 添加项目根目录到路径
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # 运行 pytest
    pytest.main()
    
    # 生成 Allure 报告
    os.system("allure generate ./reports/tmp -o ./reports/UIReport --clean")
    
    # 启动 Allure 服务查看报告
    os.system("allure serve ./reports/tmp")
