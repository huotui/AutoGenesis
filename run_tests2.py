import subprocess
import sys
import os

os.chdir(r'D:\workspace\trae\AutoGenesis\playwright-mcp-server')

result = subprocess.run(
    [sys.executable, '-m', 'pytest', 'tests/', '-v', '--tb=short'],
    capture_output=True,
    text=True,
    cwd=r'D:\workspace\trae\AutoGenesis\playwright-mcp-server'
)

with open(r'D:\workspace\trae\AutoGenesis\test_results.txt', 'w', encoding='utf-8') as f:
    f.write("=== TEST RESULTS ===\n\n")
    f.write(result.stdout)
    f.write("\n\n=== ERRORS ===\n\n")
    f.write(result.stderr)
    f.write(f"\n\n=== RETURN CODE: {result.returncode} ===\n")

print(f"Tests completed with return code: {result.returncode}")
print(f"Full results saved to: D:\\workspace\\trae\\AutoGenesis\\test_results.txt")

# Print summary lines
lines = result.stdout.split('\n')
for line in lines:
    if any(keyword in line for keyword in ['PASSED', 'FAILED', 'ERROR', 'passed', 'failed', 'error', '===']):
        print(line)
