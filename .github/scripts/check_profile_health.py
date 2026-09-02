import sys
import urllib.request
import urllib.error
from pathlib import Path


README_FILE = Path("README.md")

TIMEOUT = 12

TARGETS = [
    {
        "name": "Mussab Core",
        "url": "https://raw.githubusercontent.com/mosabalhashmmey-alt/mosabalhashmmey-alt/main/.github/assets/mussab-core.svg",
    },
    {
        "name": "Live Engine",
        "url": "https://raw.githubusercontent.com/mosabalhashmmey-alt/mosabalhashmmey-alt/main/.github/assets/live-engine.svg",
    },
    {
        "name": "Project Command Center",
        "url": "https://raw.githubusercontent.com/mosabalhashmmey-alt/mosabalhashmmey-alt/main/.github/assets/project-command-center.svg",
    },
    {
        "name": "Secret Terminal",
        "url": "https://raw.githubusercontent.com/mosabalhashmmey-alt/mosabalhashmmey-alt/main/.github/assets/secret-terminal.svg",
    },
    {
        "name": "Neon Contribution Snake",
        "url": "https://raw.githubusercontent.com/mosabalhashmmey-alt/mosabalhashmmey-alt/output/github-contribution-grid-snake-dark.svg",
    },
]


def check_url(name, url):
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "mussab-profile-health-check",
        },
        method="GET",
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=TIMEOUT,
        ) as response:
            status = response.getcode()

            if 200 <= status < 400:
                print(f"[OK] {name}")
                print(f"     HTTP {status}")
                return True

            print(f"[FAIL] {name}")
            print(f"       HTTP {status}")
            return False

    except urllib.error.HTTPError as error:
        print(f"[FAIL] {name}")
        print(f"       HTTP {error.code}")
        return False

    except urllib.error.URLError as error:
        print(f"[FAIL] {name}")
        print(f"       Network error: {error.reason}")
        return False

    except Exception as error:
        print(f"[FAIL] {name}")
        print(f"       Unexpected error: {error}")
        return False


def check_local_files():
    required_files = [
        Path(".github/assets/mussab-core.svg"),
        Path(".github/assets/live-engine.svg"),
        Path(".github/assets/project-command-center.svg"),
        Path(".github/assets/secret-terminal.svg"),
        Path(".github/data/projects.json"),
        Path(".github/scripts/generate_live_engine.py"),
        Path(".github/scripts/generate_project_center.py"),
    ]

    all_ok = True

    print("")
    print("LOCAL FILE CHECK")
    print("================")

    for file_path in required_files:
        if file_path.exists():
            print(f"[OK] {file_path}")
        else:
            print(f"[FAIL] Missing: {file_path}")
            all_ok = False

    return all_ok


def check_readme():
    print("")
    print("README CHECK")
    print("============")

    if not README_FILE.exists():
        print("[FAIL] README.md not found")
        return False

    content = README_FILE.read_text(
        encoding="utf-8"
    )

    expected_markers = [
        "mussab-core.svg",
        "live-engine.svg",
        "project-command-center.svg",
        "secret-terminal.svg",
        "github-contribution-grid-snake",
    ]

    all_ok = True

    for marker in expected_markers:
        if marker in content:
            print(f"[OK] README references {marker}")
        else:
            print(f"[WARN] README does not reference {marker}")
            all_ok = False

    return all_ok


def main():
    print("")
    print("======================================")
    print(" MUSSAB // PROFILE HEALTH SYSTEM")
    print("======================================")
    print("")

    failed_checks = []

    local_files_ok = check_local_files()

    if not local_files_ok:
        failed_checks.append(
            "One or more required local files are missing"
        )

    readme_ok = check_readme()

    if not readme_ok:
        failed_checks.append(
            "README references are incomplete"
        )

    print("")
    print("REMOTE ASSET CHECK")
    print("==================")

    for target in TARGETS:
        result = check_url(
            target["name"],
            target["url"],
        )

        if not result:
            failed_checks.append(
                f"{target['name']} is unreachable"
            )

    print("")
    print("======================================")

    if failed_checks:
        print("PROFILE HEALTH: DEGRADED")
        print("======================================")
        print("")

        for issue in failed_checks:
            print(f"- {issue}")

        print("")
        sys.exit(1)

    print("PROFILE HEALTH: HEALTHY")
    print("======================================")
    print("")
    print("All monitored profile systems are online.")

    sys.exit(0)


if __name__ == "__main__":
    main()
