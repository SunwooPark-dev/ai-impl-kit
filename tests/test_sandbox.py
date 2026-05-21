import pytest
import asyncio
from ai_impl_kit.tools.sandbox import SafePythonSandbox, SandboxException

@pytest.mark.asyncio
async def test_sandbox_success_run():
    sandbox = SafePythonSandbox()
    code = """
import math
print(math.sqrt(256))
"""
    result = await sandbox.run(code, timeout=2.0)
    assert result["success"] is True
    assert result["exit_code"] == 0
    assert "16.0" in result["stdout"]

@pytest.mark.asyncio
async def test_sandbox_import_restriction():
    sandbox = SafePythonSandbox()
    
    # 1. os 모듈 차단 검증
    code_os = "import os; print(os.getcwd())"
    result = await sandbox.run(code_os)
    assert result["success"] is False
    assert "Security Restriction" in result["stderr"] or "ImportError" in result["stderr"]

    # 2. subprocess 모듈 차단 검증
    code_sub = "import subprocess; subprocess.run(['ls'])"
    result = await sandbox.run(code_sub)
    assert result["success"] is False
    assert "Security Restriction" in result["stderr"]

@pytest.mark.asyncio
async def test_sandbox_timeout_prevention():
    sandbox = SafePythonSandbox()
    
    # 무한 루프 코드 주입 후 타임아웃 감시 검증 (1초 제한)
    code_loop = """
while True:
    pass
"""
    with pytest.raises(SandboxException) as excinfo:
        await sandbox.run(code_loop, timeout=1.0)
    assert "Execution Timeout" in str(excinfo.value)

@pytest.mark.asyncio
async def test_sandbox_file_access_restriction():
    sandbox = SafePythonSandbox()
    
    # 샌드박스 루트 외부 디렉토리 쓰기 및 절대 경로 파일 접근 제한 검증
    code_write = """
with open("/tmp/evil.txt", "w") as f:
    f.write("hack")
"""
    result = await sandbox.run(code_write)
    assert result["success"] is False
    assert "Security Restriction" in result["stderr"] or "PermissionError" in result["stderr"]
