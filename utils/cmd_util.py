import subprocess


def run(
        cmd: str | list[str],
        *,
        timeout: int = 30,
        encoding: str = "utf-8",
        shell: bool = True,
) -> tuple[int, str, str]:
    """
    执行命令，返回 (returncode, stdout, stderr)

    Args:
        cmd:      命令字符串或列表，如 "ollama list" 或 ["ollama", "list"]
        timeout:  超时秒数，默认 30s
        encoding: 输出编码，Windows 中文环境可改为 "gbk"
        shell:    是否通过 shell 执行，默认 True
    """
    result = subprocess.run(
        cmd,
        shell=shell,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        encoding=encoding,
        errors="replace",
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def run_background(cmd: str | list[str], *, shell: bool = True) -> subprocess.Popen:
    """
    在后台启动进程（不等待结束），返回 Popen 对象
    适合启动服务类进程，如 ollama serve
    """
    return subprocess.Popen(
        cmd,
        shell=shell,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

