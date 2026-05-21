import os
import sys
import tempfile
import subprocess
import asyncio
from typing import List, Optional, Any, Dict
from abc import ABC, abstractmethod

from ai_impl_kit.tools.base import AgentTool

class SandboxException(Exception):
    """샌드박스 실행 중 발생한 예외"""
    pass

class CodeSandbox(ABC):
    """
    코드를 격리하여 안전하게 실행하기 위한 샌드박스 추상 인터페이스.
    """
    @abstractmethod
    async def run(self, code: str, timeout: float = 3.0) -> Dict[str, Any]:
        """
        코드를 실행하고 결과를 dict 형태로 반환합니다.
        """
        pass

class SafePythonSandbox(CodeSandbox):
    """
    파이썬 코드를 서브프로세스와 임시 디렉토리를 활용해 격리 실행하는 안전한 파이썬 샌드박스.
    악성 모듈 임포트 제한, 무한루프 타임아웃, 격리 디렉토리 강제 제한을 수행합니다.
    """
    def __init__(self, allowed_modules: Optional[List[str]] = None):
        # 기본적으로 수치 계산 및 데이터 처리(math, json 등)는 허용, 시스템 접근 모듈은 전면 차단
        self.allowed_modules = allowed_modules or ["math", "json", "datetime", "re", "collections", "itertools"]
        # 시스템 파괴 우려 모듈 블랙리스트
        self.blocked_modules = ["os", "sys", "subprocess", "shutil", "builtins.eval", "builtins.exec", "importlib", "ctypes", "socket", "urllib", "requests"]

    async def run(self, code: str, timeout: float = 3.0) -> Dict[str, Any]:
        # 격리된 일회성 임시 디렉토리 생성
        with tempfile.TemporaryDirectory(prefix="safe_sandbox_") as temp_dir:
            script_path = os.path.join(temp_dir, "executed_code.py")
            
            # 위험한 모듈 임포트 방지 코드를 전처리로 강제 주입
            secure_prelude = f"""
# 샌드박스 격리 격벽 코드
import sys
import os

# 허용되지 않은 모듈 임포트 가로채기 및 제한
blocked_modules = {self.blocked_modules}
allowed_modules = {self.allowed_modules}

original_import = __import__
def secure_import(name, globals=None, locals=None, fromlist=(), level=0):
    root_module = name.split('.')[0]
    if root_module in blocked_modules:
        raise ImportError(f"Security Restriction: Importing module '{{root_module}}' is strictly forbidden.")
    # 기본 허용 목록 또는 기본 파이썬 모듈 제외한 시스템 접근 모듈 가로채기
    if root_module not in allowed_modules and root_module not in ['math', 'json', 'datetime', 're', 'collections', 'itertools', 'typing']:
        # 일부 내부 헬퍼 허용
        if root_module not in ['_weakref', 'encodings', 'io', 'abc', 'site']:
            raise ImportError(f"Security Restriction: Module '{{root_module}}' is not allowed in this sandbox.")
    return original_import(name, globals, locals, fromlist, level)

# 빌트인 함수 오버라이딩 (eval, exec, open 우회 제한)
original_open = open
_sandbox_root = os.path.abspath('.')
def secure_open(file, mode='r', *args, **kwargs):
    # 절대 경로 접근 차단 (오직 현재 임시 디렉토리 내부 상대경로만 쓰기/읽기 허용)
    resolved = _os.path.abspath(file)
    if not resolved.startswith(_sandbox_root):
        raise PermissionError(f"Security Restriction: Cannot access file '{{file}}' outside sandbox root.")
    return original_open(file, mode, *args, **kwargs)

import builtins
builtins.__import__ = secure_import
builtins.open = secure_open
# 샌드박스 내에서 exec/eval 차단 (위험 이중 스크립팅 방지)
def forbidden(*args, **kwargs):
    raise PermissionError("Security Restriction: Use of eval() or exec() inside the sandbox is strictly forbidden.")
builtins.eval = forbidden
builtins.exec = forbidden

# 전역 네임스페이스에서 격벽 설정용 도구 숨기기 및 sys.modules 완전 정리
_os = os
_sys = sys

for mod in list(sys.modules.keys()):
    if mod.split('.')[0] in blocked_modules:
        sys.modules.pop(mod, None)

del os
del sys

# -----------------
# USER CODE START
# -----------------
"""
            # 안전 전처리 코드 + 유저 코드를 결합하여 임시 파일 작성
            full_code = secure_prelude + code

            with open(script_path, "w", encoding="utf-8") as f:
                f.write(full_code)

            # 네트워크 및 불필요 리소스를 제거한 클린 환경 변수 구성
            clean_env = {
                "PATH": os.environ.get("PATH", ""),
                "PYTHONIOENCODING": "utf-8"
            }

            try:
                # 서브프로세스를 비동기식으로 구동
                proc = await asyncio.create_subprocess_exec(
                    sys.executable,
                    script_path,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=temp_dir,  # 실행 디렉토리를 임시 폴더로 고정 (chroot와 유사한 공간 제한)
                    env=clean_env
                )

                try:
                    # 지정된 시간 타임아웃 감시 실행
                    stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
                except asyncio.TimeoutError:
                    # 타임아웃 초과 시 서브프로세스 강제 강제 킬 (데드락 방지)
                    try:
                        proc.kill()
                        await proc.wait()  # Windows 환경에서의 파일 잠금 대기
                    except ProcessLookupError:
                        pass
                    raise SandboxException(f"Execution Timeout: Code execution exceeded {timeout} seconds limit.")

                stdout_str = stdout.decode("utf-8", errors="replace")
                stderr_str = stderr.decode("utf-8", errors="replace")
                exit_code = proc.returncode

                return {
                    "success": exit_code == 0,
                    "exit_code": exit_code,
                    "stdout": stdout_str,
                    "stderr": stderr_str
                }

            except Exception as e:
                if isinstance(e, SandboxException):
                    raise e
                raise SandboxException(f"Sandbox Runtime Error: {str(e)}")

class PythonExecutionTool(AgentTool):
    """
    LLM이 생성한 파이썬 코드를 SafePythonSandbox에서 안전하게 실행해주는 AgentTool 구현체.
    """
    def __init__(self, name: str = "execute_python_code", description: Optional[str] = None):
        desc = description or "Executes Python code in a safe sandbox. Use this for math calculations, text processing, or logic tasks. Only specific modules like math/json/datetime are allowed. Returns stdout and stderr."
        parameters = {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "The pure Python code to execute. Example: 'print(math.sqrt(144))'"
                }
            },
            "required": ["code"]
        }
        super().__init__(name, desc, parameters)
        self.sandbox = SafePythonSandbox()

    async def execute(self, **kwargs: Any) -> Dict[str, Any]:
        code = kwargs.get('code', '')
        try:
            res = await self.sandbox.run(code)
            return res
        except SandboxException as se:
            return {
                "success": False,
                "error": str(se),
                "stdout": "",
                "stderr": str(se)
            }
