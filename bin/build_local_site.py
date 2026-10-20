"""Render a content folder through the Distinctive projector into a local directory.

The content folder is laid out the way the CMS stores items: ``<section>/<slug>.md`` for
commentary, rulings and Wire items, and ``<slug>.md`` at the top level for standing pages.
Each file is YAML front matter plus a Markus body, exactly what an editor writes.

    python3 bin/build_local_site.py                      # tests/fixtures/sample-content -> web/dist-local
    python3 bin/build_local_site.py --content DIR --out DIR
    python3 bin/build_local_site.py --as-deployed           # placeholder sponsor hidden, as on the live site
    python3 -m http.server --directory web/dist-local 8080

Needs the Python requirements in ``requirements-publication.txt``.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPOSITORY / "web"))

from papyrus_content.projection.model import ItemSummary, ProjectedItem, SiteIndex  # noqa: E402
from papyrus_content.projection.stored import projection_metadata  # noqa: E402

import projector as distinctive_projector  # noqa: E402

FRONT_MATTER_PATTERN = re.compile(r"\A---\n(.*?)\n---\n?(.*)\Z", re.S)


def split_front_matter(source_text: str) -> tuple[str, str]:
    match = FRONT_MATTER_PATTERN.match(source_text)
    return (match.group(1), match.group(2)) if match else ("", source_text)


def projected_item_from_file(content_directory: Path, path: Path) -> ProjectedItem:
    relative = path.relative_to(content_directory)
    section = relative.parts[0] if len(relative.parts) > 1 else None
    source_text = path.read_text(encoding="utf-8")
    front_matter_yaml, _body = split_front_matter(source_text)
    stored = projection_metadata(front_matter_yaml)
    summary = ItemSummary(
        item_id=relative.with_suffix("").as_posix(),
        type="article" if section else "page",
        section=section,
        slug=relative.stem,
        output_path=relative.as_posix(),
        version_number=1,
        title=stored["frontMatter"].get("title"),
        page_title=stored["pageTitle"],
        front_matter=dict(stored["frontMatter"]),
        aliases=tuple(stored["frontMatter"].get("aliases") or ()),
        published_at=str(stored["frontMatter"].get("date") or "") or None,
    )
    return ProjectedItem(summary=summary, source_text=source_text)


def site_index_from_directory(content_directory: Path) -> tuple[SiteIndex, dict[str, ProjectedItem]]:
    items = [projected_item_from_file(content_directory, path) for path in sorted(content_directory.rglob("*.md"))]
    items_by_id = {item.summary.item_id: item for item in items}
    summaries = tuple(sorted((item.summary for item in items), key=lambda summary: summary.output_path))
    return SiteIndex(items=summaries, load_item=items_by_id.__getitem__), items_by_id


def render_site(content_directory: Path, show_placeholder_sponsor: bool = True) -> dict[str, bytes]:
    configuration = distinctive_projector.read_site_configuration()
    configuration["sponsor"]["showWhilePlaceholder"] = show_placeholder_sponsor
    projector = distinctive_projector.DistinctiveProjector(configuration, distinctive_projector.read_committed_static_files())
    site, items_by_id = site_index_from_directory(content_directory)
    files = dict(projector.static_files())
    for item in items_by_id.values():
        files.update(projector.item_pages(item, site))
    files.update(projector.listing_pages(site))
    return files


def write_site(files: dict[str, bytes], output_directory: Path) -> None:
    if output_directory.exists():
        shutil.rmtree(output_directory)
    for key, body in files.items():
        destination = output_directory / key
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(body)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--content", type=Path, default=REPOSITORY / "tests" / "fixtures" / "sample-content")
    parser.add_argument("--out", type=Path, default=REPOSITORY / "web" / "dist-local")
    parser.add_argument("--as-deployed", action="store_true", help="hide the placeholder sponsor, as the live site does")
    arguments = parser.parse_args()
    files = render_site(arguments.content, show_placeholder_sponsor=not arguments.as_deployed)
    write_site(files, arguments.out)
    print(f"Wrote {len(files)} files to {arguments.out}")


if __name__ == "__main__":
    main()
