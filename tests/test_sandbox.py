import pytest
import asyncio
import sys
from pathlib import Path

# Add src to sys.path
ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from ai_impl_kit.runtime.sandbox import PythonSandbox, SandboxPythonTool, SandboxSecurityError

def test_sandbox_verify_code_valid():
    # 안전한 코드들
    valid_codes = [
        "print('hello world')",
        "x = 1 + 2\ny = x * 3\nprint(y)",
        "items = [i for i in range(5)]\nprint(items)",
        "def test(a, b):\n    return a + b\nprint(test(5, 10))"
    ]
    for code in valid_codes:
        # 에러가 발생하지 않아야 함
        PythonSandbox.verify_code(code)

def test_sandbox_verify_code_forbidden_import():
    # 임포트 금지 모듈 시도
    invalid_imports = [
        "import os",
        "import sys",
        "import subprocess",
        "from os import path",
        "from sys import exit",
        "import os.path as osp",
        "import urllib.request"
    ]
    for code in invalid_imports:
        with pytest.raises(SandboxSecurityError) as excinfo:
            PythonSandbox.verify_code(code)
        assert "forbidden" in str(excinfo.value)

def test_sandbox_verify_code_forbidden_call():
    # 금지 빌트인 호출 시도
    invalid_calls = [
        "eval('1+1')",
        "exec('print(1)')",
        "open('test.txt', 'w')",
        "compile('print(1)', 'test', 'exec')",
        "__import__('os')",
        "globals()"
    ]
    for code in invalid_calls:
        with pytest.raises(SandboxSecurityError) as excinfo:
            PythonSandbox.verify_code(code)
        assert "forbidden" in str(excinfo.value)

@pytest.mark.asyncio
async def test_sandbox_execute_code_success():
    code = "print('hello from sandbox')"
    result = await PythonSandbox.execute_code(code)
    assert result["exit_code"] == 0
    assert "hello from sandbox" in result["stdout"]
    assert result["stderr"] == ""

@pytest.mark.asyncio
async def test_sandbox_execute_code_syntax_error():
    # 문법 오류 코드 실행 시 verify_code 단계에서 SandboxSecurityError 예외 발생
    code = "print('unclosed string"
    with pytest.raises(SandboxSecurityError) as excinfo:
        await PythonSandbox.execute_code(code)
    assert "Syntax error" in str(excinfo.value)

@pytest.mark.asyncio
async def test_sandbox_execute_code_runtime_error():
    # 런타임 오류는 subprocess가 정상 작동하여 exit_code가 0이 아니고 stderr에 찍혀야 함
    code = "raise ValueError('custom error')"
    result = await PythonSandbox.execute_code(code)
    assert result["exit_code"] != 0
    assert "ValueError: custom error" in result["stderr"]

@pytest.mark.asyncio
async def test_sandbox_execute_code_timeout():
    # 무한 루프 시 타임아웃
    code = "import time\nwhile True:\n    time.sleep(0.1)"
    with pytest.raises(TimeoutError) as excinfo:
        await PythonSandbox.execute_code(code, timeout=1.0)
    assert "timed out" in str(excinfo.value)

@pytest.mark.asyncio
async def test_sandbox_tool_integration():
    tool = SandboxPythonTool()
    assert tool.name == "python_sandbox"
    assert "Execute arbitrary Python code" in tool.description
    assert "code" in tool.parameters["properties"]

    # 도구 정상 작동 테스트
    result = await tool.execute("print(10 + 20)")
    assert result["exit_code"] == 0
    assert "30" in result["stdout"]

    # 도구 보안 에러 리턴 테스트
    security_result = await tool.execute("import os")
    assert security_result["exit_code"] == -1
    assert "forbidden" in security_result["stderr"]
