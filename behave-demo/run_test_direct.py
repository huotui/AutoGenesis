import subprocess
import sys
import os

os.environ['PYTHONIOENCODING'] = 'utf-8'

result = subprocess.run(
    [sys.executable, '-m', 'uv', 'run', 'behave', 'features/web_test.feature'],
    cwd=r'D:\workspace\trae\AutoGenesis\behave-demo',
    capture_output=True,
    text=True,
    encoding='utf-8',
    timeout=120
)

with open(r'D:\workspace\trae\AutoGenesis\behave-demo\test_bing_result.txt', 'w', encoding='utf-8') as f:
    f.write('=== STDOUT ===\n')
    f.write(result.stdout)
    f.write('\n=== STDERR ===\n')
    f.write(result.stderr)
    f.write(f'\n=== Return Code: {result.returncode} ===\n')

print(f'Return code: {result.returncode}')
print('Output saved to test_bing_result.txt')
