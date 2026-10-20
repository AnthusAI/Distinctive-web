"""Distinctive Mark as a Papyrus SiteProjector: render every page from stored item data, in process.

Pages:

* item pages: each commentary article, each TTAB ruling, each Before You File guide and each
  standing page (About, ...),
  with its body converted by Markus and wrapped in the Distinctive Mark chrome;
* listing pages: the front page, the rulings tracker, the Wire, the commentary index, the guides index,
  the subscribe page, the RSS feed and the sitemap;
* static files: the stylesheet, the client script, the icon, robots.txt and 404.html.

Dependency rule: every listing page and every item page is rendered from ``SiteContent``,
which is built from item summaries alone. A listing page's input digest is the digest of
the content it renders; item pages share one digest of everything their chrome and
"More on" cards show, so the engine re-renders them when that moves.
"""

from __future__ import annotations

import dataclasses
import json
import os
import re
import sys
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

MODULE_DIRECTORY = Path(os.environ.get("PAPYRUS_SITE_STATIC_DIR") or Path(__file__).resolve().parent)
sys.path.insert(0, str(MODULE_DIRECTORY))

import distinctive_markup as markup  # noqa: E402
from distinctive_content import (  # noqa: E402
    COMMENTARY_SECTION,
    GUIDES_SECTION,
    RULINGS_SECTION,
    Commentary,
    Guide,
    Ruling,
    SiteContent,
    StandingPage,
    is_standing_page,
)
from papyrus_content.markus_renderer.convert import convert_text_in_process  # noqa: E402
from papyrus_content.markus_renderer.shell import SiteChrome, render_page  # noqa: E402
from papyrus_content.projection.projector import digest_of, static_version  # noqa: E402
from papyrus_content.projection.writers import request_paths_for_key  # noqa: E402

SITE_CONFIGURATION_PATH = MODULE_DIRECTORY / "site-config.json"
STYLESHEET_KEY = "css/site-theme.css"
CLIENT_SCRIPT_KEY = "assets/distinctive.js"
ICON_KEY = "assets/icon.svg"
HOME_PAGE_KEY = "index.html"
RULINGS_PAGE_KEY = "rulings/index.html"
WIRE_PAGE_KEY = "wire/index.html"
COMMENTARY_PAGE_KEY = "commentary/index.html"
GUIDES_PAGE_KEY = "guides/index.html"
SUBSCRIBE_PAGE_KEY = "subscribe/index.html"
NOT_FOUND_PAGE_KEY = "404.html"
FEED_KEY = "feed.xml"
SITEMAP_KEY = "sitemap.xml"
FEED_ENTRY_COUNT = 30
GOOGLE_FONTS_STYLESHEET = (
    "https://fonts.googleapis.com/css2?family=Inter+Tight:wght@500;600;700;800"
    "&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500;600&display=swap"
)
MARKUS_HEADER_PATTERN = re.compile(r'<header class="markus-header">.*?</header>', re.S)
MARKUS_ARTICLE_OPEN_PATTERN = re.compile(r'^\s*<article class="markus-document">')
MARKUS_ARTICLE_CLOSE_PATTERN = re.compile(r"</article>\s*$")


def read_site_configuration() -> dict:
    return json.loads(SITE_CONFIGURATION_PATH.read_text(encoding="utf-8"))


def resolve_site_url(configuration: dict) -> str | None:
    configured = (os.environ.get("PAPYRUS_SITE_PUBLIC_URL") or "").strip() or configuration["publication"].get("siteUrl")
    if not configured:
        return None
    return configured if configured.startswith("http") else f"https://{configured}"


def read_committed_static_files() -> dict[str, bytes]:
    return {
        STYLESHEET_KEY: (MODULE_DIRECTORY / "css" / "site-theme.css").read_bytes(),
        CLIENT_SCRIPT_KEY: (MODULE_DIRECTORY / "assets" / "distinctive.js").read_bytes(),
        ICON_KEY: (MODULE_DIRECTORY / "assets" / "icon.svg").read_bytes(),
    }


def article_body_from_markus(source_text: str) -> str:
    fragment = convert_text_in_process(source_text, theme=None)
    fragment = MARKUS_HEADER_PATTERN.sub("", fragment, count=1)
    fragment = MARKUS_ARTICLE_OPEN_PATTERN.sub("", fragment, count=1)
    return MARKUS_ARTICLE_CLOSE_PATTERN.sub("", fragment, count=1).strip()


def first_heading_level_one_removed(article_html: str) -> str:
    return re.sub(r"^\s*<h1[^>]*>.*?</h1>", "", article_html, count=1, flags=re.S)


class DistinctiveProjector:
    def __init__(self, configuration: dict, static_files: dict[str, bytes]) -> None:
        self._configuration = configuration
        self._settings = markup.SiteSettings(configuration=configuration, site_url=resolve_site_url(configuration))
        self._committed_static_files = static_files
        self.version = static_version(static_files)
        self._content_by_items: tuple[tuple, SiteContent] | None = None

    def _content(self, site) -> SiteContent:
        if self._content_by_items is None or self._content_by_items[0] is not site.items:
            self._content_by_items = (site.items, SiteContent.from_summaries(site.items))
        return self._content_by_items[1]

    def _chrome(self, page_path: str, description: str, extra_head_html: str = "") -> SiteChrome:
        canonical_url = self._settings.absolute_url(page_path)
        canonical = f'<link rel="canonical" href="{markup.escaped(canonical_url)}">' if canonical_url else ""
        publication_name = markup.escaped(self._settings.publication["name"])
        head_html = (
            '<link rel="preconnect" href="https://fonts.googleapis.com">'
            '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            f'<link rel="stylesheet" href="{markup.escaped(GOOGLE_FONTS_STYLESHEET)}">'
            f'<link rel="icon" href="/{ICON_KEY}" type="image/svg+xml">'
            f'<link rel="alternate" type="application/rss+xml" title="{publication_name}" href="/feed.xml">'
            f'<meta name="description" content="{markup.escaped(description)}">'
            f'<meta property="og:site_name" content="{publication_name}">{canonical}{extra_head_html}'
        )
        return SiteChrome(
            site_name=self._settings.publication["name"],
            body_class="ds-body",
            stylesheets=(STYLESHEET_KEY,),
            scripts=(CLIENT_SCRIPT_KEY,),
            asset_root="/",
            head_html=head_html,
            title_template="{title} — {site}™",
            same_title_template="{site}™ — Trademark News &amp; Analysis",
        )

    def _render(self, *, title: str, page_path: str, description: str, body_html: str, extra_head_html: str = "") -> bytes:
        chrome = dataclasses.replace(
            self._chrome(page_path, description, extra_head_html),
            render_body=lambda context, parts: body_html + parts.scripts,
        )
        page_html = render_page(
            title=title,
            fragment="",
            active_href=page_path,
            nav_items=[],
            chrome=chrome,
            css_version=self.version,
        )
        return page_html.encode("utf-8")

    def _inner_page(self, content: SiteContent, section: str | None, main_html: str, notice: str | None = None) -> str:
        return (
            markup.compact_site_header(self._settings, section)
            + main_html
            + markup.site_footer(self._settings, content, notice=notice, show_links=True)
            + markup.confirmation_toast()
        )

    def _story_head(self, entry: Commentary | Ruling, page_path: str) -> str:
        canonical_url = self._settings.absolute_url(page_path)
        structured = {
            "@context": "https://schema.org",
            "@type": "NewsArticle" if isinstance(entry, Ruling) else "Article",
            "headline": entry.title,
            "description": entry.dek,
            "publisher": {"@type": "Organization", "name": self._settings.publication["name"]},
        }
        if entry.date:
            structured["datePublished"] = entry.date.isoformat()
        if entry.author:
            structured["author"] = {"@type": "Person", "name": entry.author}
        if canonical_url:
            structured["mainEntityOfPage"] = canonical_url
        return (
            '<meta property="og:type" content="article">'
            f'<meta property="og:title" content="{markup.escaped(entry.title)}">'
            f'<meta property="og:description" content="{markup.escaped(entry.dek)}">'
            + markup.json_ld_script(structured)
        )

    def item_page_paths(self, summary) -> tuple[str, ...]:
        if summary.section == COMMENTARY_SECTION:
            return (f"{COMMENTARY_SECTION}/{summary.slug}/index.html",)
        if summary.section == RULINGS_SECTION:
            return (f"{RULINGS_SECTION}/{summary.slug}/index.html",)
        if summary.section == GUIDES_SECTION:
            return (f"{GUIDES_SECTION}/{summary.slug}/index.html",)
        if is_standing_page(summary):
            return (f"{summary.slug}/index.html",)
        return ()

    def item_pages(self, item, site) -> dict[str, bytes]:
        content = self._content(site)
        entry = content.entry_for_item(item.summary.item_id)
        if entry is None:
            return {}
        article_html = first_heading_level_one_removed(article_body_from_markus(item.source_text))
        page_key = entry.page_key
        page_path = request_paths_for_key(page_key)[0]
        if isinstance(entry, StandingPage):
            body = self._inner_page(content, None, markup.standing_page_body(entry.title, article_html))
            return {page_key: self._render(title=entry.title, page_path=page_path, description=self._settings.publication["description"], body_html=body)}
        if isinstance(entry, Guide):
            body = self._inner_page(
                content,
                GUIDES_SECTION,
                markup.guide_page_body(self._settings, content, entry, article_html),
                notice="Guides are general information, not legal advice, and reading them does not create an attorney–client relationship. Fees, forms and deadlines change; check the cited source before relying on them.",
            )
            return {page_key: self._render(title=entry.title, page_path=page_path, description=entry.dek or self._settings.publication["description"], body_html=body)}
        section = RULINGS_SECTION if isinstance(entry, Ruling) else COMMENTARY_SECTION
        notice = None
        if isinstance(entry, Ruling):
            notice = "Commentary on this site is general information, not legal advice, and reading it does not create an attorney–client relationship. Read the opinion before relying on it."
        body = self._inner_page(content, section, markup.story_page_body(self._settings, content, entry, article_html), notice=notice)
        body += markup.sticky_signup_bar_and_slide_in(self._settings)
        return {
            page_key: self._render(
                title=entry.title,
                page_path=page_path,
                description=entry.dek or self._settings.publication["description"],
                body_html=body,
                extra_head_html=self._story_head(entry, page_path),
            )
        }

    def _listing_renderers(self, content: SiteContent) -> dict:
        settings = self._settings
        description = settings.publication["description"]
        return {
            HOME_PAGE_KEY: lambda: self._render(
                title=settings.publication["name"],
                page_path="/",
                description=description,
                body_html=(
                    markup.home_site_header(settings, content)
                    + markup.home_page_body(settings, content)
                    + markup.site_footer(settings, content, show_links=True)
                    + markup.confirmation_toast()
                ),
            ),
            RULINGS_PAGE_KEY: lambda: self._render(
                title="TTAB Rulings",
                page_path="/rulings/",
                description="Every Trademark Trial and Appeal Board decision we track, with analysis of the notable ones.",
                body_html=self._inner_page(
                    content,
                    RULINGS_SECTION,
                    markup.rulings_page_body(settings, content),
                    notice="Summaries are drawn from the public record on TTABVUE and are not legal advice. Read the opinion before relying on it.",
                ),
            ),
            WIRE_PAGE_KEY: lambda: self._render(
                title="The Wire",
                page_path="/wire/",
                description="Trademark news from the USPTO, the courts and the press, linked at the source, with a line on why it matters.",
                body_html=self._inner_page(
                    content,
                    "wire",
                    markup.wire_page_body(settings, content),
                    notice="Links on the Wire go to third‑party sites we don’t control. Our notes are commentary, not legal advice.",
                ),
            ),
            COMMENTARY_PAGE_KEY: lambda: self._render(
                title="Commentary",
                page_path="/commentary/",
                description="Doctrine, practice and the business of marks.",
                body_html=self._inner_page(content, COMMENTARY_SECTION, markup.commentary_index_body(settings, content)),
            ),
            GUIDES_PAGE_KEY: lambda: self._render(
                title="Before You File",
                page_path="/guides/",
                description="Plain-language guides for business owners choosing, filing and protecting a trademark in the United States.",
                body_html=self._inner_page(
                    content,
                    GUIDES_SECTION,
                    markup.guides_index_body(settings, content),
                    notice="Guides are general information, not legal advice, and reading them does not create an attorney–client relationship.",
                ),
            ),
            SUBSCRIBE_PAGE_KEY: lambda: self._render(
                title=f"Subscribe to {settings.newsletter['name']}",
                page_path="/subscribe/",
                description=f"{settings.newsletter['name']}: the week’s TTAB decisions, read for you. Free, every Friday.",
                body_html=self._inner_page(content, None, markup.subscribe_page_body(settings, content)),
            ),
            NOT_FOUND_PAGE_KEY: lambda: self._render(
                title="Page not found",
                page_path="/404.html",
                description=description,
                body_html=self._inner_page(content, None, markup.not_found_body()),
            ),
            FEED_KEY: lambda: self._feed_bytes(content),
            SITEMAP_KEY: lambda: self._sitemap_bytes(content),
        }

    def _listing_content_digests(self, content: SiteContent) -> dict[str, str]:
        everything = digest_of([dataclasses.asdict(entry) for entry in [*content.commentary, *content.rulings, *content.wire_items, *content.guides, *content.standing_pages]])
        rulings_only = digest_of([dataclasses.asdict(entry) for entry in content.rulings])
        footer = digest_of([dataclasses.asdict(page) for page in content.standing_pages])
        return {
            HOME_PAGE_KEY: everything,
            RULINGS_PAGE_KEY: digest_of([rulings_only, footer]),
            WIRE_PAGE_KEY: digest_of([[dataclasses.asdict(item) for item in content.wire_items], footer]),
            COMMENTARY_PAGE_KEY: digest_of([[dataclasses.asdict(entry) for entry in content.commentary], footer]),
            GUIDES_PAGE_KEY: digest_of([[dataclasses.asdict(guide) for guide in content.guides], footer]),
            SUBSCRIBE_PAGE_KEY: digest_of([rulings_only, footer]),
            NOT_FOUND_PAGE_KEY: footer,
            FEED_KEY: digest_of([[dataclasses.asdict(entry) for entry in [*content.commentary, *content.rulings]], self._settings.site_url]),
            SITEMAP_KEY: digest_of([[entry.href for entry in [*content.commentary, *content.rulings, *content.guides, *content.standing_pages]], self._settings.site_url]),
        }

    def listing_inputs(self, site) -> dict[str, str]:
        content = self._content(site)
        return {key: digest_of([digest, self.version]) for key, digest in self._listing_content_digests(content).items()}

    def listing_pages(self, site, keys=None) -> dict[str, bytes]:
        content = self._content(site)
        renderers = self._listing_renderers(content)
        return {key: render() for key, render in renderers.items() if keys is None or key in keys}

    def shared_inputs(self, site) -> str:
        content = self._content(site)
        return digest_of(
            [
                [dataclasses.asdict(entry) for entry in [*content.commentary, *content.rulings, *content.guides, *content.standing_pages]],
                self.version,
                self._settings.site_url,
            ]
        )

    def owns_page_key(self, key: str) -> bool:
        return key.endswith(".html") or key in (FEED_KEY, SITEMAP_KEY)

    def static_files(self) -> dict[str, bytes]:
        files = dict(self._committed_static_files)
        files["robots.txt"] = self._robots_text().encode("utf-8")
        return files

    def redirects(self, site) -> dict[str, str]:
        mapping: dict[str, str] = {}
        for summary in site.items:
            paths = self.item_page_paths(summary)
            if not paths:
                continue
            for alias in summary.aliases:
                source = alias if alias.startswith("/") else "/" + alias
                mapping[source] = request_paths_for_key(paths[0])[0]
        return mapping

    def _robots_text(self) -> str:
        sitemap_url = self._settings.absolute_url("/sitemap.xml")
        sitemap_line = f"Sitemap: {sitemap_url}\n" if sitemap_url else ""
        return f"User-agent: *\nAllow: /\n{sitemap_line}"

    def _feed_bytes(self, content: SiteContent) -> bytes:
        site_url = self._settings.site_url or ""
        entries = sorted([*content.commentary, *content.rulings], key=lambda entry: entry.sort_key, reverse=True)[:FEED_ENTRY_COUNT]
        items = "".join(
            "<item>"
            f"<title>{xml_escape(entry.title)}</title>"
            f"<link>{xml_escape(site_url + entry.href)}</link>"
            f"<guid>{xml_escape(site_url + entry.href)}</guid>"
            f"<description>{xml_escape(entry.dek or getattr(entry, 'one_line_summary', ''))}</description>"
            + (f"<pubDate>{entry.date:%a, %d %b %Y} 00:00:00 +0000</pubDate>" if entry.date else "")
            + "</item>"
            for entry in entries
        )
        publication = self._settings.publication
        return (
            '<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel>'
            f"<title>{xml_escape(publication['name'])} — {xml_escape(publication['tagline'])}</title>"
            f"<link>{xml_escape(site_url + '/')}</link>"
            f"<description>{xml_escape(publication['description'])}</description>"
            f"{items}</channel></rss>\n"
        ).encode("utf-8")

    def _sitemap_bytes(self, content: SiteContent) -> bytes:
        site_url = self._settings.site_url
        paths = ["/", "/rulings/", "/wire/", "/commentary/", "/guides/", "/subscribe/"]
        paths += [entry.href for entry in [*content.commentary, *content.rulings, *content.guides, *content.standing_pages]]
        urls = "".join(f"<url><loc>{xml_escape((site_url or '') + path)}</loc></url>" for path in paths) if site_url else ""
        return (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n'
        ).encode("utf-8")


def create_projector() -> DistinctiveProjector:
    return DistinctiveProjector(read_site_configuration(), read_committed_static_files())
