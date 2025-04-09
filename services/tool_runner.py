# services/tool_runner.py

import subprocess
import json
import os

def run_bandit(path):
    output_file = os.path.join(path, "bandit.json")
    subprocess.run(["bandit", "-r", path, "-f", "json", "-o", output_file])
    return parse_bandit(output_file)

def run_flake8(path):
    output_file = os.path.join(path, "flake8.json")
    subprocess.run([
        "flake8", path,
        "--format=json",
        f"--output-file={output_file}"
    ])
    return parse_flake8(output_file)

def run_radon(path):
    output_file = os.path.join(path, "radon.json")
    output = subprocess.check_output(["radon", "cc", path, "-j"])
    with open(output_file, "w") as f:
        f.write(output.decode())
    return parse_radon(output_file)

def parse_bandit(file_path):
    issues = []
    with open(file_path) as f:
        data = json.load(f)
        for res in data.get("results", []):
            issues.append({
                "tool": "bandit",
                "file": res["filename"],
                "line": res["line_number"],
                "severity": res["issue_severity"],
                "message": res["issue_text"]
            })
    return issues
def parse_flake8(file_path):
    issues = []
    merged_data = {}

    try:
        with open(file_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    fragment = json.loads(line)
                    merged_data.update(fragment)
                except json.JSONDecodeError as e:
                    print(f"⚠️ Skipping invalid JSON line: {line}\nError: {e}")
    except FileNotFoundError:
        print(f"❌ Flake8 result file not found: {file_path}")
        return []

    for file, errs in merged_data.items():
        for err in errs:
            issues.append({
                "tool": "flake8",
                "file": file,
                "line": err["line_number"],
                "severity": "LOW",  # Flake8 doesn't classify severity
                "message": err["text"]
            })

    return issues

def parse_radon(file_path):
    issues = []
    with open(file_path) as f:
        data = json.load(f)
        for file, funcs in data.items():
            for func in funcs:
                issues.append({
                    "tool": "radon",
                    "file": file,
                    "line": func["lineno"],
                    "severity": classify_radon(func["rank"]),
                    "message": f"{func['name']} - Complexity: {func['complexity']} - Rank: {func['rank']}"
                })
    return issues

def classify_radon(rank):
    if rank in ["A", "B"]:
        return "LOW"
    elif rank in ["C", "D"]:
        return "MEDIUM"
    return "HIGH"
