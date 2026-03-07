"""
GitHub Commits Farm - README modifier
Specific repo: https://github.com/CastDev-j/truquito
Generates dated commits from 2022 to present.
"""

import argparse
import os
import random
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# Fixed configuration
GITHUB_USERNAME = "CastDev-j"
USER_EMAIL = "23031429@itcelaya.edu.mx"
USER_NAME = "CastDev"
REPOSITORY_NAME = "truquito"
README_PATH = "README.md"

# Default commit range
DEFAULT_START_DATE = datetime(2022, 1, 1, 12, 0, 0)

# Commit range per day
MIN_COMMITS_PER_DAY = 3
MAX_COMMITS_PER_DAY = 15


def run_git_command(command, cwd, env=None):
    """Run a git command and return the completed process."""
    result = subprocess.run(
        command,
        cwd=cwd,
        shell=True,
        capture_output=True,
        text=True,
        env=env,
    )
    return result


def setup_git_env(date):
    """Prepare env variables so git writes author/committer dates."""
    env = os.environ.copy()
    timestamp = date.strftime("%Y-%m-%d %H:%M:%S")
    env["GIT_AUTHOR_DATE"] = timestamp
    env["GIT_COMMITTER_DATE"] = timestamp
    return env


def generate_readme_content(commit_number, total_commits, current_date):
    """Generate varied README content to ensure each commit changes the file."""
    templates = [
        f"""# Truquito Project\n\n## Commit #{commit_number} of {total_commits}\n**Date:** {current_date.strftime('%Y-%m-%d %H:%M:%S')}\n\n### Activity Log:\n- Updated project configuration\n- Modified documentation\n- Added new features\n- Fixed bugs\n- Performance improvements\n\n---\n*Automated commit #{commit_number}*\n""",
        f"""# Truquito - Magic Happens Here\n\n## Commit Statistics\n- **Commit Number:** {commit_number}/{total_commits}\n- **Timestamp:** {current_date.strftime('%Y-%m-%d %H:%M:%S')}\n- **Author:** {USER_NAME}\n\n### Changes in this commit:\n```javascript\nconsole.log('Making magic happen...');\n// Commit #{commit_number}\n```\n""",
        f"""# {REPOSITORY_NAME}\n\n### Status Update\n- Commit ID: `{commit_number}`\n- Date: `{current_date.strftime('%Y-%m-%d %H:%M:%S')}`\n- Maintainer: `{GITHUB_USERNAME}`\n\nThis is an automated update for contribution history.\n""",
    ]
    return random.choice(templates)


def ensure_git_repo(repo_path):
    check = run_git_command("git rev-parse --is-inside-work-tree", cwd=repo_path)
    return check.returncode == 0 and check.stdout.strip() == "true"


def choose_repo_path(base_dir, preferred_name):
    preferred_path = base_dir / preferred_name
    if preferred_path.exists() and ensure_git_repo(preferred_path):
        return preferred_path
    if ensure_git_repo(base_dir):
        return base_dir
    return None


def build_schedule(start_date, end_date, min_commits, max_commits):
    if min_commits < 0 or max_commits < 0:
        raise ValueError("min_commits and max_commits must be >= 0")
    if min_commits > max_commits:
        raise ValueError("min_commits cannot be greater than max_commits")
    if start_date > end_date:
        raise ValueError("start_date cannot be after end_date")

    schedule = []
    days = (end_date.date() - start_date.date()).days + 1

    for day_offset in range(days):
        current_day = start_date.date() + timedelta(days=day_offset)
        num_commits = random.randint(min_commits, max_commits)

        for _ in range(num_commits):
            commit_time = datetime(
                current_day.year,
                current_day.month,
                current_day.day,
                random.randint(0, 23),
                random.randint(0, 59),
                random.randint(0, 59),
            )
            if start_date <= commit_time <= end_date:
                schedule.append(commit_time)

    schedule.sort()
    return schedule


def set_local_git_identity(repo_path):
    run_git_command(f'git config user.name "{USER_NAME}"', cwd=repo_path)
    run_git_command(f'git config user.email "{USER_EMAIL}"', cwd=repo_path)


def create_commits(repo_path, readme_file, schedule, dry_run=False):
    total = len(schedule)
    if total == 0:
        print("No commits to create with the selected range.")
        return 0

    readme_file.parent.mkdir(parents=True, exist_ok=True)
    successful = 0

    for index, commit_date in enumerate(schedule, start=1):
        content = generate_readme_content(index, total, commit_date)
        readme_file.write_text(content, encoding="utf-8")

        env = setup_git_env(commit_date)
        run_git_command(f'git add "{readme_file.name}"', cwd=repo_path, env=env)

        commit_message = f"chore: update README ({index}/{total})"

        if dry_run:
            print(f"[DRY-RUN] {commit_date} -> {commit_message}")
            successful += 1
            continue

        commit_result = run_git_command(
            f'git commit -m "{commit_message}"',
            cwd=repo_path,
            env=env,
        )

        if commit_result.returncode == 0:
            successful += 1
            if index % 25 == 0 or index == total:
                print(f"Progress: {index}/{total} commits created")
        else:
            stderr = commit_result.stderr.strip() or "Unknown git commit error"
            print(f"Warning on commit {index}: {stderr}")

    return successful


def maybe_push(repo_path, should_push):
    if not should_push:
        return

    push_result = run_git_command("git push", cwd=repo_path)
    if push_result.returncode != 0:
        stderr = push_result.stderr.strip() or "Unknown push error"
        print(f"Push failed: {stderr}")
    else:
        print("Push completed successfully.")


def parse_args():
    parser = argparse.ArgumentParser(description="Generate dated README commits.")
    parser.add_argument(
        "--repo-path",
        default="",
        help="Target repo path. Default: auto-detect truquito or current repo.",
    )
    parser.add_argument(
        "--start-date",
        default=DEFAULT_START_DATE.strftime("%Y-%m-%d"),
        help="Start date in YYYY-MM-DD format (default: 2022-01-01).",
    )
    parser.add_argument(
        "--end-date",
        default=datetime.now().strftime("%Y-%m-%d"),
        help="End date in YYYY-MM-DD format (default: today).",
    )
    parser.add_argument(
        "--min-commits",
        type=int,
        default=MIN_COMMITS_PER_DAY,
        help=f"Minimum commits per day (default: {MIN_COMMITS_PER_DAY}).",
    )
    parser.add_argument(
        "--max-commits",
        type=int,
        default=MAX_COMMITS_PER_DAY,
        help=f"Maximum commits per day (default: {MAX_COMMITS_PER_DAY}).",
    )
    parser.add_argument(
        "--push",
        action="store_true",
        help="Run git push after generating commits.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate commits without creating git commits.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Optional random seed for reproducible schedules.",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    try:
        start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
        start_date = start_date.replace(hour=0, minute=0, second=0)
        end_date = datetime.strptime(args.end_date, "%Y-%m-%d")
        end_date = end_date.replace(hour=23, minute=59, second=59)
    except ValueError:
        print("Error: Dates must use YYYY-MM-DD format.")
        return 1

    base_dir = Path(__file__).resolve().parent
    if args.repo_path:
        repo_path = Path(args.repo_path).resolve()
    else:
        auto = choose_repo_path(base_dir, REPOSITORY_NAME)
        if auto is None:
            print("Error: No git repository detected in current path or 'truquito' subfolder.")
            return 1
        repo_path = auto

    if not ensure_git_repo(repo_path):
        print(f"Error: '{repo_path}' is not a git repository.")
        return 1

    try:
        schedule = build_schedule(
            start_date=start_date,
            end_date=end_date,
            min_commits=args.min_commits,
            max_commits=args.max_commits,
        )
    except ValueError as exc:
        print(f"Error: {exc}")
        return 1

    readme_file = repo_path / README_PATH

    print(f"Repository: {repo_path}")
    print(f"README: {readme_file}")
    print(f"Commits planned: {len(schedule)}")
    print(f"Dry run: {args.dry_run}")

    if not args.dry_run:
        set_local_git_identity(repo_path)

    successful = create_commits(
        repo_path=repo_path,
        readme_file=readme_file,
        schedule=schedule,
        dry_run=args.dry_run,
    )

    print(f"Finished. Successful commits: {successful}/{len(schedule)}")

    if not args.dry_run:
        maybe_push(repo_path, args.push)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
