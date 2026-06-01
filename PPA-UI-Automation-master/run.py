import os
import sys
import pytest
import argparse

if __name__ == "__main__":
    # 添加项目根目录到路径
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='运行测试用例')
    parser.add_argument(
        '--format',
        choices=['mcp', 'native', 'all'],
        default='all',
        help='选择测试格式: mcp(默认), native(原生Playwright), all(所有)'
    )
    parser.add_argument(
        '--test',
        type=str,
        help='指定运行特定测试文件,如: testcase/test_bing.py'
    )
    args = parser.parse_args()
    
    # 构建 pytest 参数
    pytest_args = ['-vs', '--alluredir=./reports/tmp', '--clean-alluredir', '--asyncio-mode=auto']
    
    if args.test:
        # 运行指定文件
        pytest_args.append(args.test)
    elif args.format == 'mcp':
        # 只运行 MCP 格式 (文件名不包含 _native)
        pytest_args.extend(['-k', 'not native'])
    elif args.format == 'native':
        # 只运行原生 Playwright 格式 (文件名包含 _native)
        pytest_args.extend(['-k', 'native'])
    # else: all - 不添加过滤条件,运行所有测试
    
    print(f"\n{'='*60}")
    print(f"运行测试 - 格式: {args.format}")
    print(f"{'='*60}\n")
    
    # 运行 pytest
    pytest.main(pytest_args)
    
    # 生成 Allure 报告
    print(f"\n{'='*60}")
    print("生成 Allure 报告...")
    print(f"{'='*60}\n")
    os.system("allure generate ./reports/tmp -o ./reports/UIReport --clean")
    
    # 启动 Allure 服务查看报告
    print(f"\n{'='*60}")
    print("启动 Allure 报告服务...")
    print(f"{'='*60}\n")
    os.system("allure serve ./reports/tmp")
