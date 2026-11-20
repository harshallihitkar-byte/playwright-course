"""
Lesson 12 - Git basics (solution)

This script practises the everyday Git commands in a THROW-AWAY folder, so nothing
in your real projects changes and nothing is uploaded anywhere.
It is the same as typing the commands from the lesson one by one.
"""
import shutil
import subprocess
import tempfile
from pathlib import Path

from portal_helpers import passed


def git(*args, cwd):
    """Run one git command and show it, like typing it in the terminal."""
    print("  $ git", " ".join(args))
    result = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True)
    if result.stdout.strip():
        print("    " + result.stdout.strip().replace("\n", "\n    "))
    return result.stdout


def main():
    if shutil.which("git") is None:
        print("Git is not installed. Install it from https://git-scm.com/download/win and re-run.")
        return

    folder = Path(tempfile.mkdtemp(prefix="git-practice-"))
    print("Practice folder:", folder)

    # Exercise 1: create a repository and make the first commit
    git("init", "-b", "main", cwd=folder)
    git("config", "user.name", "Practice User", cwd=folder)            # only for this practice repo
    git("config", "user.email", "practice@example.com", cwd=folder)
    (folder / "license_bot.py").write_text('print("hello from my bot")\n')
    (folder / ".gitignore").write_text(".venv/\noutput/\n*.log\nauth_state.json\n")
    (folder / "output").mkdir()
    (folder / "output" / "results.xlsx").write_text("pretend excel")
    git("status", "--short", cwd=folder)
    git("add", ".", cwd=folder)
    git("commit", "-m", "First version of license bot", cwd=folder)
    tracked = git("ls-files", cwd=folder).split()
    assert "output/results.xlsx" not in tracked, ".gitignore should keep output/ out of Git"
    passed("Exercise 1 - repo created, first commit, .gitignore works")

    # Exercise 2: change a file, see the difference, commit again
    (folder / "license_bot.py").write_text('print("hello from my bot")\nprint("now with retries")\n')
    git("diff", cwd=folder)
    git("commit", "-am", "Add retries", cwd=folder)
    log = git("log", "--oneline", cwd=folder)
    assert len(log.strip().splitlines()) == 2
    passed("Exercise 2 - second commit, history shows 2 commits")

    # Exercise 3: try an idea on a branch, then merge it back
    git("switch", "-c", "feature/excel-report", cwd=folder)
    (folder / "report.py").write_text("# builds the Excel report\n")
    git("add", "report.py", cwd=folder)
    git("commit", "-m", "Add Excel report", cwd=folder)
    git("switch", "main", cwd=folder)
    git("merge", "feature/excel-report", cwd=folder)
    assert (folder / "report.py").exists()
    git("log", "--oneline", "--graph", cwd=folder)
    passed("Exercise 3 - branch created, committed and merged")

    shutil.rmtree(folder, ignore_errors=True)


if __name__ == "__main__":
    main()
