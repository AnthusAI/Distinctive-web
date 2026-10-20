"""The Distinctive content model, read from the projection's item summaries.

Editors write each item in the Papyrus newsroom. The item's section decides what it is:

* ``commentary``: an article with a page of its own.
* ``rulings``: one TTAB decision. Every ruling has a page; notable ones carry full analysis.
* ``wire``: outside news. It links to the source and has no page here.
* no section, type ``page``: a standing page such as About or Editorial policy.

Card fields come from the item's front matter (``docs/content-model.md``), so every
listing can be rendered from summaries alone, without loading item bodies.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field

COMMENTARY_SECTION = "commentary"
RULINGS_SECTION = "rulings"
WIRE_SECTION = "wire"
NOTABLE_RULING_MINIMUM_NOTABILITY = 4
MAXIMUM_NOTABILITY = 5


def read_text(front_matter: dict, *names: str) -> str:
    for name in names:
        value = front_matter.get(name)
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return ""


def read_text_list(front_matter: dict, name: str) -> tuple[str, ...]:
    value = front_matter.get(name)
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, list):
        return ()
    return tuple(str(entry).strip() for entry in value if str(entry).strip())


def read_positive_integer(front_matter: dict, name: str) -> int | None:
    value = front_matter.get(name)
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None
    return number if number > 0 else None


def read_boolean(front_matter: dict, name: str) -> bool:
    value = front_matter.get(name)
    if isinstance(value, str):
        return value.strip().lower() in ("true", "yes", "1")
    return bool(value)


def parse_calendar_date(value) -> dt.date | None:
    if isinstance(value, dt.datetime):
        return value.date()
    if isinstance(value, dt.date):
        return value
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip()
    try:
        return dt.datetime.fromisoformat(text.replace("Z", "+00:00")).date()
    except ValueError:
        pass
    try:
        return dt.date.fromisoformat(text[:10])
    except ValueError:
        return None


def item_calendar_date(summary) -> dt.date | None:
    return parse_calendar_date(summary.front_matter.get("date")) or parse_calendar_date(summary.published_at)


def format_long_date(date: dt.date | None) -> str:
    return f"{date:%B} {date.day}, {date.year}" if date else ""


def format_short_date(date: dt.date | None) -> str:
    return f"{date:%b} {date.day}" if date else ""


def format_short_date_with_year(date: dt.date | None) -> str:
    return f"{date:%b} {date.day}, {date.year}" if date else ""


@dataclass(frozen=True)
class MarkAtIssue:
    label: str
    mark: str
    number: str
    goods: str


@dataclass(frozen=True)
class PublishedEntry:
    item_id: str
    slug: str
    title: str
    dek: str
    date: dt.date | None
    author: str
    read_minutes: int | None
    tags: tuple[str, ...]
    is_lead: bool

    @property
    def sort_key(self) -> tuple:
        return (self.date or dt.date.min, self.slug)


@dataclass(frozen=True)
class Commentary(PublishedEntry):
    kicker: str = ""

    @property
    def page_key(self) -> str:
        return f"{COMMENTARY_SECTION}/{self.slug}/index.html"

    @property
    def href(self) -> str:
        return f"/{COMMENTARY_SECTION}/{self.slug}/"


@dataclass(frozen=True)
class Ruling(PublishedEntry):
    caption: str = ""
    proceeding: str = ""
    proceeding_number: str = ""
    issue: str = ""
    issue_label: str = ""
    outcome: str = ""
    is_precedential: bool = False
    notability: int = 1
    panel: str = ""
    opinion_url: str = ""
    one_line_summary: str = ""
    reasons_notable: tuple[str, ...] = ()
    marks_at_issue: tuple[MarkAtIssue, ...] = ()

    @property
    def page_key(self) -> str:
        return f"{RULINGS_SECTION}/{self.slug}/index.html"

    @property
    def href(self) -> str:
        return f"/{RULINGS_SECTION}/{self.slug}/"

    @property
    def is_notable(self) -> bool:
        return self.notability >= NOTABLE_RULING_MINIMUM_NOTABILITY

    @property
    def status_label(self) -> str:
        return "Precedential" if self.is_precedential else "Not precedential"

    @property
    def headline(self) -> str:
        return self.title or self.caption


@dataclass(frozen=True)
class WireItem:
    item_id: str
    slug: str
    headline: str
    source: str
    source_url: str
    outlet: str
    take: str
    date: dt.date | None

    @property
    def sort_key(self) -> tuple:
        return (self.date or dt.date.min, self.slug)


@dataclass(frozen=True)
class StandingPage:
    item_id: str
    slug: str
    title: str

    @property
    def page_key(self) -> str:
        return f"{self.slug}/index.html"

    @property
    def href(self) -> str:
        return f"/{self.slug}/"


def read_marks_at_issue(front_matter: dict) -> tuple[MarkAtIssue, ...]:
    marks = front_matter.get("marks")
    if not isinstance(marks, dict):
        return ()
    labelled_roles = (("applicant", "Applicant"), ("cited", "Cited registration"))
    found = []
    for role, default_label in labelled_roles:
        entry = marks.get(role)
        if not isinstance(entry, dict):
            continue
        found.append(
            MarkAtIssue(
                label=read_text(entry, "label") or default_label,
                mark=read_text(entry, "mark"),
                number=read_text(entry, "number"),
                goods=read_text(entry, "goods"),
            )
        )
    return tuple(found)


def shared_entry_fields(summary) -> dict:
    front_matter = summary.front_matter
    return {
        "item_id": summary.item_id,
        "slug": summary.slug,
        "title": read_text(front_matter, "title") or summary.page_title or summary.title or summary.slug,
        "dek": read_text(front_matter, "dek", "description"),
        "date": item_calendar_date(summary),
        "author": read_text(front_matter, "author"),
        "read_minutes": read_positive_integer(front_matter, "readMinutes"),
        "tags": read_text_list(front_matter, "tags"),
        "is_lead": read_boolean(front_matter, "lead"),
    }


def commentary_from_summary(summary) -> Commentary:
    return Commentary(**shared_entry_fields(summary), kicker=read_text(summary.front_matter, "kicker"))


def ruling_from_summary(summary) -> Ruling:
    front_matter = summary.front_matter
    notability = read_positive_integer(front_matter, "notability") or 1
    return Ruling(
        **shared_entry_fields(summary),
        caption=read_text(front_matter, "caption"),
        proceeding=read_text(front_matter, "proceeding"),
        proceeding_number=read_text(front_matter, "proceedingNumber"),
        issue=read_text(front_matter, "issue"),
        issue_label=read_text(front_matter, "issueLabel", "issue"),
        outcome=read_text(front_matter, "outcome"),
        is_precedential=read_boolean(front_matter, "precedential"),
        notability=min(notability, MAXIMUM_NOTABILITY),
        panel=read_text(front_matter, "panel"),
        opinion_url=read_text(front_matter, "opinionUrl"),
        one_line_summary=read_text(front_matter, "summary"),
        reasons_notable=read_text_list(front_matter, "whyNotable"),
        marks_at_issue=read_marks_at_issue(front_matter),
    )


def wire_item_from_summary(summary) -> WireItem:
    front_matter = summary.front_matter
    return WireItem(
        item_id=summary.item_id,
        slug=summary.slug,
        headline=read_text(front_matter, "title") or summary.page_title or summary.title or summary.slug,
        source=read_text(front_matter, "source"),
        source_url=read_text(front_matter, "sourceUrl"),
        outlet=read_text(front_matter, "outlet"),
        take=read_text(front_matter, "take"),
        date=item_calendar_date(summary),
    )


def is_standing_page(summary) -> bool:
    return summary.section is None and summary.type == "page" and summary.slug not in ("index", "")


@dataclass
class SiteContent:
    """Every published item of the site, sorted newest first within its kind."""

    commentary: list[Commentary] = field(default_factory=list)
    rulings: list[Ruling] = field(default_factory=list)
    wire_items: list[WireItem] = field(default_factory=list)
    standing_pages: list[StandingPage] = field(default_factory=list)

    @classmethod
    def from_summaries(cls, summaries) -> "SiteContent":
        content = cls()
        for summary in summaries:
            if summary.section == COMMENTARY_SECTION:
                content.commentary.append(commentary_from_summary(summary))
            elif summary.section == RULINGS_SECTION:
                content.rulings.append(ruling_from_summary(summary))
            elif summary.section == WIRE_SECTION:
                content.wire_items.append(wire_item_from_summary(summary))
            elif is_standing_page(summary):
                content.standing_pages.append(
                    StandingPage(
                        item_id=summary.item_id,
                        slug=summary.slug,
                        title=read_text(summary.front_matter, "title") or summary.page_title or summary.title or summary.slug,
                    )
                )
        content.commentary.sort(key=lambda entry: entry.sort_key, reverse=True)
        content.rulings.sort(key=lambda entry: entry.sort_key, reverse=True)
        content.wire_items.sort(key=lambda entry: entry.sort_key, reverse=True)
        content.standing_pages.sort(key=lambda page: page.slug)
        return content

    @property
    def notable_rulings(self) -> list[Ruling]:
        return [ruling for ruling in self.rulings if ruling.is_notable]

    @property
    def standing_page_slugs(self) -> set[str]:
        return {page.slug for page in self.standing_pages}

    def lead_story(self) -> Commentary | Ruling | None:
        flagged = [entry for entry in [*self.rulings, *self.commentary] if entry.is_lead]
        if flagged:
            return max(flagged, key=lambda entry: entry.sort_key)
        if self.notable_rulings:
            return max(self.notable_rulings, key=lambda ruling: (ruling.notability, ruling.sort_key))
        if self.commentary:
            return self.commentary[0]
        return self.rulings[0] if self.rulings else None

    def entry_for_item(self, item_id: str) -> Commentary | Ruling | StandingPage | None:
        for entry in [*self.commentary, *self.rulings, *self.standing_pages]:
            if entry.item_id == item_id:
                return entry
        return None

    def related_entries(self, entry: Commentary | Ruling, maximum_count: int = 3) -> list[Commentary | Ruling]:
        topic_words = set(entry.tags)
        if isinstance(entry, Ruling) and entry.issue:
            topic_words.add(entry.issue)
        candidates = [other for other in [*self.rulings, *self.commentary] if other.item_id != entry.item_id]

        def shares_topic(other) -> bool:
            other_topics = set(other.tags) | ({other.issue} if isinstance(other, Ruling) and other.issue else set())
            return bool(topic_words & other_topics)

        related = sorted((other for other in candidates if shares_topic(other)), key=lambda other: other.sort_key, reverse=True)
        return related[:maximum_count]
