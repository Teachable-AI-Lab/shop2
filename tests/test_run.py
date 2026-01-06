def test_run_executes_without_error():
    import subprocess
    import sys

    result = subprocess.run(
        [sys.executable, "run.py"],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    assert "Task Completed" in result.stdout
