import subprocess
import sys

result = subprocess.run(
    [sys.executable, '-m', 'pytest', 'tests/', '-v', '--tb=short'],
    capture_output=True,
    text=True,
    cwd=r'D:\workspace\trae\AutoGenesis\playwright-mcp-server'
)

print("STDOUT:")
print(result.stdout[-8000:] if len(result.stdout) > 8000 else result.stdout)
print("\nSTDERR:")
print(result.stderr[-2000:] if len(result.stderr) > 2000 else result.stderr)
print(f"\nReturn code: {result.returncode}")
