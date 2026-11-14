from __future__ import annotations

import json
import re
import subprocess
import sys
import urllib.error
import urllib.request

from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


@dataclass
class UpdateResult:
    available: bool
    message: str
    current_version: str = ""
    latest_version: str = ""
    commits: int = 0
    safe_to_install: bool = False
    install_type: str = ""
    release: dict[str, Any] | None = None


class UpdateManager:
    """
    Trixie DevSuite automatic update engine.

    Supports:
    - Git source installations
    - Frozen Windows executable installations
    """

    GITHUB_API = "https://api.github.com"
    USER_AGENT = "Trixie-DevSuite-Updater"

    def __init__(
        self,
        current_version: str,
        repo_path: str | Path | None = None,
        github_repository: str | None = None,
    ):
        self.current_version = current_version
        self.repo_path = Path(repo_path or Path(__file__).resolve().parent)
        self.github_repository = github_repository or self._detect_github_repository()

        self.install_type = (
            "exe" if getattr(sys, "frozen", False) else "source"
        )

    # ---------------------------------------------------------
    # INSTALLATION DETECTION
    # ---------------------------------------------------------

    @property
    def is_executable(self) -> bool:
        return self.install_type == "exe"

    @property
    def is_source(self) -> bool:
        return self.install_type == "source"

    # ---------------------------------------------------------
    # GIT HELPERS
    # ---------------------------------------------------------

    def _git(self, *args: str) -> str:
        result = subprocess.run(
            ["git", *args],
            cwd=self.repo_path,
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )

        return result.stdout.strip()

    def _git_path(self, name: str) -> Path:
        path = Path(self._git("rev-parse", "--git-path", name))

        if not path.is_absolute():
            path = self.repo_path / path

        return path.resolve()

    def _detect_github_repository(self) -> str | None:
        try:
            remote = self._git("remote", "get-url", "origin")
        except (subprocess.SubprocessError, OSError):
            return None

        # Supports HTTPS and SSH GitHub remotes.
        match = re.search(
            r"github\.com[:/]([^/]+/[^/]+?)(?:\.git)?$",
            remote.strip(),
            re.IGNORECASE,
        )

        return match.group(1) if match else None

    def _git_safety_check(self) -> tuple[bool, str]:
        try:
            # Ensure this is actually a Git working tree.
            self._git("rev-parse", "--show-toplevel")

            # Never update during an unfinished Git operation.
            operation_markers = [
                "MERGE_HEAD",
                "CHERRY_PICK_HEAD",
                "REVERT_HEAD",
                "rebase-merge",
                "rebase-apply",
            ]

            for marker in operation_markers:
                if self._git_path(marker).exists():
                    return False, f"Git operation in progress: {marker}"

            # Includes tracked, modified, staged AND untracked files.
            changes = self._git("status", "--porcelain")

            if changes:
                return False, (
                    "Local changes detected. Commit or stash them "
                    "before installing updates."
                )

            return True, "Working tree is clean."

        except (subprocess.SubprocessError, OSError) as error:
            return False, f"Git safety check failed: {error}"

    # ---------------------------------------------------------
    # VERSION COMPARISON
    # ---------------------------------------------------------

    @staticmethod
    def _version_tuple(version: str) -> tuple[int, ...]:
        """
        Basic numeric version comparison.

        Examples:
            1.0.2 -> (1, 0, 2)
            v1.2.0 -> (1, 2, 0)
        """
        numbers = re.findall(r"\d+", version)

        if not numbers:
            raise ValueError(f"Invalid version: {version}")

        return tuple(int(number) for number in numbers)

    @classmethod
    def _is_newer(cls, latest: str, current: str) -> bool:
        return cls._version_tuple(latest) > cls._version_tuple(current)

    # ---------------------------------------------------------
    # SOURCE INSTALLATION UPDATE CHECK
    # ---------------------------------------------------------

    def check_source_updates(self) -> UpdateResult:
        try:
            # Fetch updates without modifying the working files.
            self._git("fetch", "origin")

            branch = self._git("branch", "--show-current")

            if not branch:
                return UpdateResult(
                    False,
                    "Detached HEAD detected. Switch to a branch first.",
                    install_type="source",
                )

            upstream = self._git(
                "rev-parse",
                "--abbrev-ref",
                "--symbolic-full-name",
                "@{upstream}",
            )

            # Determine whether the local branch is ahead or behind.
            counts = self._git(
                "rev-list",
                "--left-right",
                "--count",
                f"HEAD...{upstream}",
            )

            ahead, behind = map(int, counts.split())

            safe, safety_message = self._git_safety_check()

            if behind == 0:
                message = (
                    "Your application is up to date!"
                    if ahead == 0
                    else "Local branch contains commits not on the remote."
                )

                return UpdateResult(
                    available=False,
                    message=message,
                    safe_to_install=False,
                    install_type="source",
                )

            if ahead:
                return UpdateResult(
                    available=True,
                    message=(
                        "Updates are available, but your local branch "
                        "has diverged from the remote."
                    ),
                    commits=behind,
                    safe_to_install=False,
                    install_type="source",
                )

            return UpdateResult(
                available=True,
                message=(
                    f"{behind} update(s) available. "
                    + (safety_message if safe else safety_message)
                ),
                commits=behind,
                safe_to_install=safe,
                install_type="source",
            )

        except subprocess.CalledProcessError as error:
            detail = error.stderr.strip() if error.stderr else str(error)

            return UpdateResult(
                False,
                f"Git update check failed: {detail}",
                install_type="source",
            )

        except (OSError, ValueError) as error:
            return UpdateResult(
                False,
                f"Update check failed: {error}",
                install_type="source",
            )

    def install_source_updates(self) -> tuple[bool, str]:
        """
        Installs source updates using fast-forward only.

        Never resets, stashes, or discards local files.
        """
        try:
            safe, message = self._git_safety_check()

            if not safe:
                return False, message

            upstream = self._git(
                "rev-parse",
                "--abbrev-ref",
                "--symbolic-full-name",
                "@{upstream}",
            )

            counts = self._git(
                "rev-list",
                "--left-right",
                "--count",
                f"HEAD...{upstream}",
            )

            ahead, behind = map(int, counts.split())

            if ahead:
                return False, "Local branch has diverged from the remote."

            if behind == 0:
                return False, "No updates are available."

            self._git("merge", "--ff-only", upstream)

            return True, "Trixie DevSuite updated successfully!"

        except subprocess.CalledProcessError as error:
            detail = error.stderr.strip() if error.stderr else str(error)
            return False, f"Installation failed: {detail}"

        except (OSError, ValueError) as error:
            return False, str(error)

    # ---------------------------------------------------------
    # GITHUB RELEASE UPDATE CHECK
    # ---------------------------------------------------------

    def _github_request(self, endpoint: str) -> dict[str, Any]:
        if not self.github_repository:
            raise RuntimeError("GitHub repository could not be identified.")

        url = f"{self.GITHUB_API}/repos/{self.github_repository}/{endpoint}"

        request = urllib.request.Request(
            url,
            headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": self.USER_AGENT,
            },
        )

        with urllib.request.urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))

    def check_release_updates(self) -> UpdateResult:
        try:
            release = self._github_request("releases/latest")

            latest = release.get("tag_name", "").strip()

            if not latest:
                return UpdateResult(
                    False,
                    "The latest GitHub release has no version tag.",
                    install_type="exe",
                )

            available = self._is_newer(latest, self.current_version)

            return UpdateResult(
                available=available,
                message=(
                    f"Version {latest} is available!"
                    if available
                    else "Your application is up to date!"
                ),
                current_version=self.current_version,
                latest_version=latest,
                safe_to_install=available,
                install_type="exe",
                release=release,
            )

        except urllib.error.HTTPError as error:
            return UpdateResult(
                False,
                f"GitHub returned HTTP {error.code}.",
                install_type="exe",
            )

        except (urllib.error.URLError, OSError, ValueError, RuntimeError) as error:
            return UpdateResult(
                False,
                f"Release check failed: {error}",
                install_type="exe",
            )

    # ---------------------------------------------------------
    # PUBLIC UPDATE CHECK
    # ---------------------------------------------------------

    def check_for_updates(self) -> UpdateResult:
        if self.is_executable:
            return self.check_release_updates()

        return self.check_source_updates()