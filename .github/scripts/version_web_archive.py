import re
import shutil
import subprocess
import sys
from pathlib import Path


def main() -> None:
    source_dir = Path(sys.argv[1]).resolve()
    web_dir = source_dir / "build" / "web"
    archives = [
        path for path in web_dir.glob("*.tar.gz")
        if not re.search(r"-[0-9a-f]{12}\.tar\.gz$", path.name)
    ]
    if len(archives) != 1:
        raise RuntimeError(
            f"Expected one Pygbag archive in {web_dir}, found {len(archives)}"
        )

    commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"],
        cwd=source_dir,
        text=True
    ).strip()
    source_archive = archives[0]
    archive_name = (
        f"{source_archive.name[:-len('.tar.gz')]}-{commit[:12]}.tar.gz"
    )
    shutil.copyfile(source_archive, web_dir / archive_name)

    index_file = web_dir / "index.html"
    html = index_file.read_text(encoding="utf-8")
    if html.count(source_archive.name) != 1:
        raise RuntimeError(
            f"Expected one reference to {source_archive.name} in {index_file}"
        )
    index_file.write_text(
        html.replace(source_archive.name, archive_name),
        encoding="utf-8"
    )


if __name__ == "__main__":
    main()
