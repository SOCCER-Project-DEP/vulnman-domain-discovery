import subprocess

# Do not use any libs that are not in stdlib

# Execute commands using subprocess.run
commands = [
    ["git", "pull", "origin", "main"],
    ["poetry", "config", "virtualenvs.in-project", "true"],
    ["poetry", "install"],
]
if __name__ == "__main__":
    for cmd in commands:
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            print("Return Code:", res.returncode)
            print("Standard Output:", res.stdout)
            print("Standard Error:", res.stderr)
            exit(1)