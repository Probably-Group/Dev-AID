#!/usr/bin/env python3
"""
Interactive Conflict Resolver for Dev-AID Updates

Handles user-modified files with interactive merge options:
- Keep your version (preserve customizations)
- Take upstream version (accept new defaults)
- Manual merge (combine both)
- Show diff (review changes)
- Skip (decide later)

Usage:
    python3 conflict_resolver.py <backup_dir> <update_dir> <file_list> [--dry-run]

Example:
    python3 conflict_resolver.py .dev-aid-backup-20251210 /tmp/dev-aid-update files.txt
"""

import difflib
import sys
from enum import Enum
from pathlib import Path
from typing import List, Optional


class MergeChoice(Enum):
    """User's choice for resolving a conflict"""

    KEEP_YOURS = "yours"
    TAKE_UPSTREAM = "upstream"
    MANUAL_MERGE = "manual"
    SKIP = "skip"


class Color:
    """ANSI color codes for terminal output"""

    GREEN = "\033[0;32m"
    BLUE = "\033[0;34m"
    YELLOW = "\033[1;33m"
    RED = "\033[0;31m"
    CYAN = "\033[0;36m"
    BOLD = "\033[1m"
    NC = "\033[0m"  # No Color

    @staticmethod
    def colorize(text: str, color: str) -> str:
        """Wrap text in color codes"""
        return f"{color}{text}{Color.NC}"


class ConflictResolver:
    """Interactive conflict resolution for Dev-AID updates"""

    def __init__(self, backup_dir: str, update_dir: str, dry_run: bool = False):
        self.backup_dir = Path(backup_dir)
        self.update_dir = Path(update_dir)
        self.dry_run = dry_run
        self.conflicts: List[str] = []
        self.resolutions: dict = {}  # Track what was chosen for each file

    def detect_conflicts(self, file_list: List[str]) -> List[str]:
        """
        Detect files modified by user that would be overwritten

        Args:
            file_list: List of file paths to check (relative to .dev-aid/)

        Returns:
            List of conflicting file paths
        """
        conflicts = []

        for file_path in file_list:
            current = Path(".dev-aid") / file_path
            upstream = self.update_dir / ".dev-aid" / file_path

            if not current.exists():
                continue  # No conflict if file doesn't exist locally

            if not upstream.exists():
                continue  # No conflict if file doesn't exist in update

            # Compare file contents
            try:
                current_content = current.read_bytes()
                upstream_content = upstream.read_bytes()

                if current_content != upstream_content:
                    conflicts.append(file_path)
            except Exception as e:
                print(f"{Color.YELLOW}⚠️  Warning: Could not compare {file_path}: {e}{Color.NC}")

        return conflicts

    def show_diff(self, file_path: str) -> None:
        """
        Show unified diff of conflicting file with color coding

        Args:
            file_path: Relative path to file in .dev-aid/
        """
        current = Path(".dev-aid") / file_path
        upstream = self.update_dir / ".dev-aid" / file_path

        try:
            current_lines = current.read_text().splitlines(keepends=True)
            upstream_lines = upstream.read_text().splitlines(keepends=True)
        except Exception as e:
            print(f"{Color.RED}❌ Error reading files: {e}{Color.NC}")
            return

        # Generate unified diff
        diff = difflib.unified_diff(
            current_lines,
            upstream_lines,
            fromfile=f"current/{file_path}",
            tofile=f"upstream/{file_path}",
            lineterm="",
        )

        print("\n" + "=" * 70)
        print(Color.colorize(f"📝 Diff for: {file_path}", Color.BOLD))
        print("=" * 70)

        line_count = 0
        for line in diff:
            line_count += 1
            # Color code diff lines
            if line.startswith("+++") or line.startswith("---"):
                print(Color.colorize(line, Color.BOLD))
            elif line.startswith("+"):
                print(Color.colorize(line, Color.GREEN))
            elif line.startswith("-"):
                print(Color.colorize(line, Color.RED))
            elif line.startswith("@@"):
                print(Color.colorize(line, Color.CYAN))
            else:
                print(line)

            # Limit output for very large diffs
            if line_count > 100:
                print(
                    Color.colorize("\n... (diff truncated, too large to display) ...", Color.YELLOW)
                )
                print(
                    f"Use a diff tool to view the full diff: git diff --no-index {current} {upstream}"
                )
                break

        print("=" * 70 + "\n")

    def show_file_info(self, file_path: str) -> None:
        """Show metadata about the conflicting file"""
        current = Path(".dev-aid") / file_path
        upstream = self.update_dir / ".dev-aid" / file_path

        print(f"\n{Color.BLUE}File Information:{Color.NC}")
        print(f"  Path: {file_path}")

        if current.exists():
            size = current.stat().st_size
            print(f"  Your version: {size} bytes")

        if upstream.exists():
            size = upstream.stat().st_size
            print(f"  Upstream version: {size} bytes")

    def prompt_user(self, file_path: str) -> MergeChoice:
        """
        Interactive prompt for conflict resolution

        Args:
            file_path: Relative path to conflicting file

        Returns:
            User's merge choice
        """
        self.show_diff(file_path)
        self.show_file_info(file_path)

        print(f"\n{Color.YELLOW}⚠️  Conflict in: {file_path}{Color.NC}")
        print("   Your version differs from upstream")
        print("\nOptions:")
        print(f"  {Color.GREEN}[y]{Color.NC} Keep YOUR version (preserve your changes)")
        print(f"  {Color.BLUE}[u]{Color.NC} Take UPSTREAM version (accept new version)")
        print(f"  {Color.CYAN}[m]{Color.NC} Manual MERGE (create merge file)")
        print(f"  {Color.YELLOW}[d]{Color.NC} Show DIFF again")
        print(f"  {Color.YELLOW}[i]{Color.NC} Show file INFO")
        print(f"  {Color.YELLOW}[s]{Color.NC} SKIP this file for now")
        print(f"  {Color.YELLOW}[?]{Color.NC} Help")

        while True:
            try:
                choice = (
                    input(f"\n{Color.BOLD}Your choice [y/u/m/d/i/s/?]: {Color.NC}").strip().lower()
                )
            except (KeyboardInterrupt, EOFError):
                print(f"\n\n{Color.RED}❌ Update cancelled by user{Color.NC}")
                sys.exit(1)

            if choice == "y":
                return MergeChoice.KEEP_YOURS
            elif choice == "u":
                return MergeChoice.TAKE_UPSTREAM
            elif choice == "m":
                return MergeChoice.MANUAL_MERGE
            elif choice == "d":
                self.show_diff(file_path)
                continue
            elif choice == "i":
                self.show_file_info(file_path)
                continue
            elif choice == "s":
                return MergeChoice.SKIP
            elif choice == "?":
                self.show_help()
                continue
            else:
                print(f"{Color.RED}❌ Invalid choice. Please select y/u/m/d/i/s/?{Color.NC}")

    def show_help(self) -> None:
        """Show detailed help for conflict resolution"""
        print("\n" + "=" * 70)
        print(Color.colorize("📚 Conflict Resolution Help", Color.BOLD))
        print("=" * 70)
        print(
            """
KEEP YOURS (y):
  - Preserves your modifications
  - Ignores upstream changes
  - Use when: You've customized for your project

TAKE UPSTREAM (u):
  - Replaces with new version
  - Discards your changes
  - Use when: Upstream has bug fixes or you want defaults

MANUAL MERGE (m):
  - Creates a file with git-style conflict markers
  - You manually combine changes in your editor
  - Use when: Both versions have important changes
  - Creates: .dev-aid/<file>.merged

SHOW DIFF (d):
  - Displays differences again
  - Helps decide which option to choose
  - Green lines: additions in upstream
  - Red lines: removals from your version

SHOW INFO (i):
  - Displays file metadata (size, path)
  - Useful for large files

SKIP (s):
  - Leave file unchanged for now
  - You can update it manually later
  - Use when: Need more time to decide

IMPORTANT NOTES:
  - Your original file is always backed up
  - You can rollback anytime with: ./.dev-aid/scripts/rollback.sh
  - Manual merge files use git-style conflict markers (<<<<<<, ======, >>>>>>)
  - After manual merge, replace the original file with your merged version
        """
        )
        print("=" * 70)

    def resolve_conflict(self, file_path: str, choice: MergeChoice) -> None:
        """
        Execute the user's merge choice

        Args:
            file_path: Relative path to conflicting file
            choice: User's resolution choice
        """
        current = Path(".dev-aid") / file_path
        upstream = self.update_dir / ".dev-aid" / file_path

        if self.dry_run:
            print(
                f"{Color.CYAN}[DRY-RUN] Would resolve {file_path} with choice: {choice.value}{Color.NC}"
            )
            self.resolutions[file_path] = choice.value
            return

        if choice == MergeChoice.KEEP_YOURS:
            print(f"{Color.GREEN}✅ Keeping your version of {file_path}{Color.NC}")
            self.resolutions[file_path] = "kept_yours"

        elif choice == MergeChoice.TAKE_UPSTREAM:
            print(f"{Color.BLUE}✅ Taking upstream version of {file_path}{Color.NC}")
            try:
                # Ensure parent directory exists
                current.parent.mkdir(parents=True, exist_ok=True)
                # Replace with upstream version
                current.write_bytes(upstream.read_bytes())
                self.resolutions[file_path] = "took_upstream"
            except Exception as e:
                print(f"{Color.RED}❌ Error updating file: {e}{Color.NC}")
                self.resolutions[file_path] = f"error: {e}"

        elif choice == MergeChoice.MANUAL_MERGE:
            print(f"{Color.CYAN}🔧 Creating merge file for {file_path}...{Color.NC}")
            merge_file = self.create_merge_file(file_path)
            if merge_file:
                print(f"{Color.GREEN}✅ Merged file created: {merge_file}{Color.NC}")
                print(f"{Color.YELLOW}   Review and replace {current} when ready{Color.NC}")
                self.resolutions[file_path] = "manual_merge_created"
            else:
                print(f"{Color.RED}❌ Failed to create merge file{Color.NC}")
                self.resolutions[file_path] = "manual_merge_failed"

        elif choice == MergeChoice.SKIP:
            print(f"{Color.YELLOW}⏭️  Skipped {file_path} (will not be updated){Color.NC}")
            self.resolutions[file_path] = "skipped"

    def create_merge_file(self, file_path: str) -> Optional[Path]:
        """
        Create a file with git-style conflict markers

        Args:
            file_path: Relative path to conflicting file

        Returns:
            Path to created merge file, or None on error
        """
        current = Path(".dev-aid") / file_path
        upstream = self.update_dir / ".dev-aid" / file_path
        merged = Path(f".dev-aid/{file_path}.merged")

        try:
            current_content = current.read_text()
            upstream_content = upstream.read_text()

            # Create merge file with conflict markers
            merge_content = f"""<<<<<<< YOUR VERSION
{current_content}
=======
{upstream_content}
>>>>>>> UPSTREAM VERSION
"""

            # Ensure parent directory exists
            merged.parent.mkdir(parents=True, exist_ok=True)

            # Write merge file
            merged.write_text(merge_content)

            return merged

        except Exception as e:
            print(f"{Color.RED}Error creating merge file: {e}{Color.NC}")
            return None

    def resolve_all(self, conflicts: List[str]) -> dict:
        """
        Interactive resolution for all conflicts

        Args:
            conflicts: List of conflicting file paths

        Returns:
            Dictionary of resolutions
        """
        if not conflicts:
            print(f"{Color.GREEN}✅ No conflicts detected!{Color.NC}")
            return {}

        print(f"\n{Color.YELLOW}🔍 Found {len(conflicts)} conflicting files{Color.NC}")
        print("   Resolving each conflict interactively...\n")

        for i, file_path in enumerate(conflicts, 1):
            print(f"\n{Color.BOLD}[{i}/{len(conflicts)}] Resolving: {file_path}{Color.NC}")
            print("-" * 70)

            choice = self.prompt_user(file_path)
            self.resolve_conflict(file_path, choice)

        print(f"\n{Color.GREEN}✅ All conflicts resolved!{Color.NC}\n")

        # Show summary
        self.show_resolution_summary()

        return self.resolutions

    def show_resolution_summary(self) -> None:
        """Show summary of how conflicts were resolved"""
        print("\n" + "=" * 70)
        print(Color.colorize("📊 Resolution Summary", Color.BOLD))
        print("=" * 70)

        kept_yours = sum(1 for v in self.resolutions.values() if v == "kept_yours")
        took_upstream = sum(1 for v in self.resolutions.values() if v == "took_upstream")
        manual_merge = sum(1 for v in self.resolutions.values() if v == "manual_merge_created")
        skipped = sum(1 for v in self.resolutions.values() if v == "skipped")

        print(f"  {Color.GREEN}Kept your version:{Color.NC} {kept_yours}")
        print(f"  {Color.BLUE}Took upstream:{Color.NC} {took_upstream}")
        print(f"  {Color.CYAN}Manual merge:{Color.NC} {manual_merge}")
        print(f"  {Color.YELLOW}Skipped:{Color.NC} {skipped}")
        print(f"  {Color.BOLD}Total conflicts:{Color.NC} {len(self.resolutions)}")

        if manual_merge > 0:
            print(
                f"\n{Color.YELLOW}⚠️  Note: Review .merged files and replace originals when ready{Color.NC}"
            )

        if skipped > 0:
            print(f"\n{Color.YELLOW}⚠️  Note: Skipped files were not updated{Color.NC}")

        print("=" * 70 + "\n")

    def save_resolution_log(
        self, output_path: str = ".dev-aid/.last-update-resolutions.json"
    ) -> None:
        """Save resolution log for audit trail"""
        import json

        log_data = {
            "timestamp": str(
                Path(output_path).stat().st_mtime if Path(output_path).exists() else ""
            ),
            "resolutions": self.resolutions,
            "dry_run": self.dry_run,
        }

        try:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            Path(output_path).write_text(json.dumps(log_data, indent=2))
            print(f"{Color.BLUE}Resolution log saved: {output_path}{Color.NC}")
        except Exception as e:
            print(f"{Color.YELLOW}⚠️  Could not save resolution log: {e}{Color.NC}")


def main():
    """CLI entry point"""
    if len(sys.argv) < 4:
        print("Usage: conflict_resolver.py <backup_dir> <update_dir> <file_list> [--dry-run]")
        print("")
        print("Arguments:")
        print("  backup_dir  - Directory containing backup")
        print("  update_dir  - Directory containing new version")
        print("  file_list   - Text file with list of files to check (one per line)")
        print("  --dry-run   - Preview conflicts without making changes")
        print("")
        print("Example:")
        print(
            "  python3 conflict_resolver.py .dev-aid-backup-20251210 /tmp/dev-aid-update files.txt"
        )
        sys.exit(1)

    backup_dir = sys.argv[1]
    update_dir = sys.argv[2]
    file_list_path = sys.argv[3]
    dry_run = "--dry-run" in sys.argv

    # Read file list
    try:
        with open(file_list_path) as f:
            files = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"{Color.RED}❌ File list not found: {file_list_path}{Color.NC}")
        sys.exit(1)

    if not files:
        print(f"{Color.YELLOW}⚠️  File list is empty{Color.NC}")
        sys.exit(0)

    # Create resolver
    resolver = ConflictResolver(backup_dir, update_dir, dry_run)

    # Detect conflicts
    print(f"{Color.BLUE}🔍 Checking {len(files)} files for conflicts...{Color.NC}")
    conflicts = resolver.detect_conflicts(files)

    if not conflicts:
        print(f"{Color.GREEN}✅ No conflicts detected!{Color.NC}")
        sys.exit(0)

    # Resolve conflicts
    resolutions = resolver.resolve_all(conflicts)

    # Save resolution log
    resolver.save_resolution_log()

    # Write conflict count for shell script
    try:
        Path("/tmp/dev-aid-conflict-count.txt").write_text(str(len(conflicts)))
    except Exception:
        pass  # Not critical

    # Exit code: 0 if all resolved, 1 if any skipped
    skipped_count = sum(1 for v in resolutions.values() if v == "skipped")
    sys.exit(1 if skipped_count > 0 else 0)


if __name__ == "__main__":
    main()
