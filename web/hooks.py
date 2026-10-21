"""Distinctive's page compositions, as the one named hook of the standard Papyrus front end.

Core renders everything around the page body: head tags, canonical and social cards, JSON-LD, robots, sitemap,
feeds, 404, redirects, listing structure. What stays here is the part that is the publication: the typed content
model (``distinctive_content``) and the compositions of ``distinctive_markup``. Settings live in ``projection.json``;
``site-config.json`` keeps the editorial fields the compositions read (filters, newsletter, sponsor, legal notice).

``DEPENDS_ON`` says what each page is composed from, so that an edit re-renders only the pages that show it: every page
also shows the footer's standing-page links ("@root"), and stories and the front page show cards from the whole site.
The publication's name, tagline and description have one source of truth, ``projection.json``.

Only ``page_body`` is a hook (see "Hooks" in the Papyrus guide "Building a Papyrus static site"). Helpers start with
an underscore so they are not mistaken for hooks.
"""

from __future__ import annotations

import functools
import json
from pathlib import Path

import distinctive_markup as markup
from distinctive_content import (
    COMMENTARY_SECTION,
    GUIDES_SECTION,
    RULINGS_SECTION,
    WIRE_SECTION,
    Commentary,
    Guide,
    Ruling,
    SiteContent,
    StandingPage,
)
from papyrus_content.projection.standard.fragments import article_body

import re

DEPENDS_ON = {
    "home": ["*"],
    "item": ["*"],
    "listing:rulings": ["rulings", "@root"],
    "archive:rulings": ["rulings", "@root"],
    "custom:contact": ["@root"],
    "listing:wire": ["wire", "@root"],
    "listing:commentary": ["commentary", "@root"],
    "listing:guides": ["guides", "@root"],
    "custom:subscribe": ["rulings", "@root"],
    "not_found": ["@root"],
    "*": ["*"],
}

_CONFIGURATION_PATH = Path(__file__).resolve().parent / "site-config.json"
_content_cache: list = [None, None]

_RULINGS_NOTICE = "Summaries are drawn from the public record on TTABVUE and are not legal advice. Read the opinion before relying on it."
_ARCHIVE_NOTICE = "Summaries are drawn from the public record and are not legal advice. Read the opinion before relying on it."
_WIRE_NOTICE = "Links on the Wire go to third‑party sites we don’t control. Our notes are commentary, not legal advice."
_GUIDES_NOTICE = "Guides are general information, not legal advice, and reading them does not create an attorney–client relationship."
_GUIDE_PAGE_NOTICE = (
    "Guides are general information, not legal advice, and reading them does not create an attorney–client relationship. "
    "Fees, forms and deadlines change; check the cited source before relying on them."
)
_RULING_PAGE_NOTICE = (
    "Commentary on this site is general information, not legal advice, and reading it does not create an attorney–client "
    "relationship. Read the opinion before relying on it."
)


@functools.lru_cache(maxsize=1)
def _configuration_text() -> str:
    return _CONFIGURATION_PATH.read_text(encoding="utf-8")


def _settings(page) -> markup.SiteSettings:
    configuration = json.loads(_configuration_text())
    identity = page.settings.identity
    configuration["publication"].update(name=identity.name, tagline=identity.tagline, description=identity.description)
    return markup.SiteSettings(configuration=configuration, site_url=page.environment.origin)


def _content(page) -> SiteContent:
    if _content_cache[0] is not page.summaries:
        _content_cache[:] = [page.summaries, SiteContent.from_summaries(page.summaries)]
    return _content_cache[1]


def _first_heading_level_one_removed(article_html: str) -> str:
    return re.sub(r"^\s*<h1[^>]*>.*?</h1>", "", article_html, count=1, flags=re.S)


def _inner_page(settings, content, section, main_html: str, notice: str | None = None, shows_sponsor_bar: bool = False) -> str:
    return (
        markup.compact_site_header(settings, section, shows_sponsor_bar=shows_sponsor_bar)
        + main_html
        + markup.site_footer(settings, content, notice=notice, show_links=True)
        + markup.confirmation_toast()
    )


def _listing_body(settings, content, section: str) -> str:
    if section == RULINGS_SECTION:
        return _inner_page(settings, content, RULINGS_SECTION, markup.rulings_page_body(settings, content), notice=_RULINGS_NOTICE)
    if section == WIRE_SECTION:
        return _inner_page(settings, content, "wire", markup.wire_page_body(settings, content), notice=_WIRE_NOTICE)
    if section == COMMENTARY_SECTION:
        return _inner_page(settings, content, COMMENTARY_SECTION, markup.commentary_index_body(settings, content))
    if section == GUIDES_SECTION:
        return _inner_page(settings, content, GUIDES_SECTION, markup.guides_index_body(settings, content), notice=_GUIDES_NOTICE)
    raise ValueError(f"No composition for the {section!r} listing")


def _item_body(settings, content, page) -> str | None:
    entry = content.entry_for_item(page.entry.item_id)
    if entry is None:
        return None
    article_html = _first_heading_level_one_removed(article_body(page.fragment))
    if isinstance(entry, StandingPage):
        return _inner_page(settings, content, None, markup.standing_page_body(entry.title, article_html), shows_sponsor_bar=True)
    if isinstance(entry, Guide):
        return _inner_page(
            settings, content, GUIDES_SECTION, markup.guide_page_body(settings, content, entry, article_html, page.page_actions), notice=_GUIDE_PAGE_NOTICE
        )
    section = RULINGS_SECTION if isinstance(entry, Ruling) else COMMENTARY_SECTION
    notice = _RULING_PAGE_NOTICE if isinstance(entry, Ruling) else None
    body = _inner_page(settings, content, section, markup.story_page_body(settings, content, entry, article_html, page.page_actions), notice=notice)
    return body + markup.sticky_signup_bar_and_slide_in(settings)


def _with_main_target(body_html: str) -> str:
    """Give the first <main> the id that the skip link points at."""
    return re.sub(r"<main(?=[\s>])", '<main id="main"', body_html, count=1)


def page_body(page):
    settings = _settings(page)
    content = _content(page)
    if page.kind == "home":
        body = (
            markup.home_site_header(settings, content)
            + markup.home_page_body(settings, content)
            + markup.site_footer(settings, content, show_links=True)
            + markup.confirmation_toast()
        )
    elif page.kind == "listing":
        body = _listing_body(settings, content, page.listing.section)
    elif page.kind == "archive":
        body = _inner_page(
            settings, content, RULINGS_SECTION, markup.ruling_archive_page_body(settings, content, page.listing.group), notice=_ARCHIVE_NOTICE
        )
    elif page.kind == "custom" and page.custom_id == "contact":
        body = _inner_page(settings, content, None, markup.contact_page_body(settings))
    elif page.kind == "custom" and page.custom_id == "subscribe":
        body = _inner_page(settings, content, None, markup.subscribe_page_body(settings, content))
    elif page.kind == "not_found":
        body = _inner_page(settings, content, None, markup.not_found_body())
    elif page.kind == "item":
        body = _item_body(settings, content, page)
        if body is None:
            return None
    else:
        return None
    return page.skip_link + _with_main_target(body)
