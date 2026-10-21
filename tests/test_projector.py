"""The Distinctive projector renders the sample content into the pages the design calls for.

Run: python3 -m unittest discover -s tests   (needs requirements-publication.txt)
"""

import dataclasses
import sys
import unittest
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPOSITORY / "bin"))
sys.path.insert(0, str(REPOSITORY / "web"))

import build_local_site  # noqa: E402
from papyrus_content.projection.model import SiteIndex  # noqa: E402
from papyrus_content.projection.standard.projector import StandardMarkusProjector  # noqa: E402

SAMPLE_CONTENT = REPOSITORY / "tests" / "fixtures" / "sample-content"


def create_projector():
    return StandardMarkusProjector.from_static_directory(
        REPOSITORY / "web", environ={"PAPYRUS_SITE_PUBLIC_URL": build_local_site.PREVIEW_ORIGIN}
    )


def sample_site():
    return build_local_site.site_index_from_directory(SAMPLE_CONTENT)


def site_with_changed_front_matter(site, item_id, **changed_fields):
    changed = []
    for summary in site.items:
        if summary.item_id == item_id:
            summary = dataclasses.replace(summary, front_matter={**summary.front_matter, **changed_fields})
        changed.append(summary)
    return SiteIndex(items=tuple(changed), load_item=site.load_item)


class RenderedSampleSiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files = build_local_site.render_site(SAMPLE_CONTENT)

    def page(self, key):
        return self.files[key].decode("utf-8")

    def test_every_page_of_the_design_is_rendered(self):
        for key in (
            "index.html",
            "rulings/index.html",
            "rulings/in-re-applicant-e/index.html",
            "commentary/index.html",
            "commentary/letters-of-protest/index.html",
            "wire/index.html",
            "subscribe/index.html",
            "about/index.html",
            "404.html",
            "feed.xml",
            "sitemap.xml",
            "robots.txt",
            "css/site-theme.css",
            "assets/distinctive.js",
        ):
            self.assertIn(key, self.files)

    def test_wire_items_link_out_and_have_no_page(self):
        self.assertFalse(any(key.startswith("wire/") and key not in ("wire/index.html", "wire/index.md") for key in self.files))
        self.assertIn("https://www.wipo.int/madrid/en/", self.page("wire/index.html"))

    def test_front_page_leads_with_the_flagged_ruling(self):
        home = self.page("index.html")
        lead_start = home.index('class="ds-lead-story"')
        self.assertIn("A crowded field, or just a few neighbors?", home[lead_start : lead_start + 1500])
        self.assertIn("From the Board", home)
        self.assertIn("The Docket, <span>weekly.</span>", home)

    def test_tracker_hero_is_the_most_notable_ruling(self):
        tracker = self.page("rulings/index.html")
        hero_start = tracker.index('class="ds-notable-hero"')
        self.assertIn("Notability 5 of 5", tracker[hero_start : hero_start + 600])
        self.assertIn("12 decisions", tracker)
        self.assertEqual(tracker.count('data-ds-row="sponsor"'), 2)

    def test_story_page_has_glance_marks_inline_signup_and_sponsor_units(self):
        story = self.page("rulings/in-re-applicant-e/index.html")
        self.assertIn("Decision at a glance", story)
        self.assertIn("[APPLIED‑FOR MARK]", story)
        signup_position = story.index("ds-inline-signup")
        self.assertLess(story.index('id="what-the-board-decided"'), signup_position)
        self.assertLess(signup_position, story.index('id="why-the-registrations-didnt-carry-the-day"'))
        self.assertIn("ds-sponsor-sidebar", story)
        self.assertIn("ds-sponsor-banner", story)
        self.assertIn("More on §2(d)", story)

    def test_markus_title_heading_is_not_repeated_in_the_body(self):
        story = self.page("commentary/letters-of-protest/index.html")
        self.assertEqual(story.count("<h1"), 1)
        self.assertNotIn("markus-header", story)

    def test_footer_lists_only_standing_pages_that_exist(self):
        home = self.page("index.html")
        self.assertIn('href="/about/"', home)
        self.assertNotIn('href="/contributors/"', home)


class DependencyRuleTests(unittest.TestCase):
    def setUp(self):
        self.projector = create_projector()
        self.site, _items = sample_site()

    def test_editing_a_wire_item_rerenders_wire_and_front_page_only(self):
        before = self.projector.listing_inputs(self.site)
        changed_site = site_with_changed_front_matter(self.site, "wire/madrid-system-update", take="A different take.")
        after = self.projector.listing_inputs(changed_site)
        changed_keys = {key for key in before if before[key] != after[key]}
        self.assertEqual(changed_keys, {"index.html", "wire/index.html", "index.md", "wire/index.md"})

    def test_editing_a_ruling_card_field_moves_item_page_shared_inputs(self):
        changed_site = site_with_changed_front_matter(self.site, "rulings/in-re-applicant-a", outcome="Refusal reversed")
        self.assertNotEqual(self.projector.shared_inputs(self.site), self.projector.shared_inputs(changed_site))

    def test_listing_pages_render_only_the_requested_keys(self):
        pages = self.projector.listing_pages(self.site, keys={"wire/index.html"})
        self.assertEqual(set(pages), {"wire/index.html"})

    def test_projector_owns_html_and_feeds_but_not_static_assets(self):
        self.assertTrue(self.projector.owns_page_key("rulings/in-re-applicant-a/index.html"))
        self.assertTrue(self.projector.owns_page_key("feed.xml"))
        self.assertFalse(self.projector.owns_page_key("css/site-theme.css"))

    def test_aliases_redirect_to_the_item_page(self):
        aliased_site = SiteIndex(
            items=tuple(
                dataclasses.replace(summary, aliases=("/old-ruling-address/",)) if summary.item_id == "rulings/in-re-applicant-a" else summary
                for summary in self.site.items
            ),
            load_item=self.site.load_item,
        )
        self.assertEqual(self.projector.redirects(aliased_site), {"/old-ruling-address/": "/rulings/in-re-applicant-a/"})


class GuideTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files = build_local_site.render_site(SAMPLE_CONTENT)

    def page(self, key):
        return self.files[key].decode("utf-8")

    def test_guides_index_groups_guides_by_series_in_rank_order(self):
        index = self.page("guides/index.html")
        self.assertLess(index.index("Choosing a mark"), index.index("After you file"))
        self.assertLess(index.index("Choosing a strong mark"), index.index("Searching before you file"))

    def test_guide_page_shows_review_date_and_more_guides_in_its_series(self):
        guide = self.page("guides/searching-before-you-file/index.html")
        self.assertIn("Last reviewed October 1, 2026", guide)
        self.assertIn('href="/guides/choosing-a-strong-mark/"', guide)
        self.assertIn('href="/rulings/in-re-applicant-e/"', guide)

    def test_story_with_owner_takeaway_links_its_guide(self):
        ruling = self.page("rulings/in-re-applicant-e/index.html")
        self.assertIn("ds-owner-takeaway", ruling)
        self.assertIn("Read the guide: Searching before you file", ruling)

    def test_navigation_home_and_sitemap_reach_the_guides(self):
        self.assertIn('href="/guides/"', self.page("rulings/index.html"))
        self.assertIn("ds-guides-band", self.page("index.html"))
        self.assertIn("/guides/searching-before-you-file/", self.page("sitemap.xml"))

    def test_practitioner_referral_note_appears_on_rulings(self):
        self.assertIn("ds-sponsor-referral", self.page("rulings/in-re-applicant-e/index.html"))


class RulingTierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files = build_local_site.render_site(SAMPLE_CONTENT)
        cls.tracker = cls.files["rulings/index.html"].decode("utf-8")

    def test_every_ruling_gets_a_tier_from_precedential_status_and_notability(self):
        for tier in ("precedential", "brief", "line"):
            self.assertIn(f'data-ds-tier="{tier}"', self.tracker)

    def test_rulings_are_grouped_by_week_with_precedential_first(self):
        self.assertIn("Week of October 12, 2026", self.tracker)
        week = self.tracker.split('data-ds-week="2026-10-12"', 1)[1].split("</section>", 1)[0]
        self.assertLess(week.index('data-ds-tier="precedential"'), week.index('data-ds-tier="line"'))

    def test_monthly_archive_pages_exist_and_are_in_the_sitemap(self):
        self.assertIn("rulings/archive/2026-09/index.html", self.files)
        self.assertIn('href="/rulings/archive/2026-09/"', self.tracker)
        self.assertIn("/rulings/archive/2026-09/", self.files["sitemap.xml"].decode("utf-8"))

    def test_stats_strip_counts_tracked_decisions(self):
        self.assertIn("decisions tracked in 2026", self.tracker)

    def test_line_rows_show_the_short_outcome(self):
        from distinctive_content import Ruling
        sample = Ruling(item_id="x", slug="x", title="x", dek="", date=None, author="", read_minutes=None, tags=(), is_lead=False,
                        owner_takeaway="", guide_slug="", outcome="Refusal affirmed (classes 35 and 41); other grounds not reached")
        self.assertEqual(sample.short_outcome, "Refusal affirmed")


class ContactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files = build_local_site.render_site(SAMPLE_CONTENT)

    def test_contact_page_says_it_is_not_open_while_no_endpoint_is_configured(self):
        contact = self.files["contact/index.html"].decode("utf-8")
        self.assertIn("data-ds-contact-closed", contact)
        self.assertIn("Messages cannot be sent yet", contact)
        self.assertIn('name="website"', contact)

    def test_footer_and_stories_link_to_the_contact_page(self):
        story = self.files["rulings/in-re-applicant-e/index.html"].decode("utf-8")
        self.assertIn('href="/contact/"', story)
        self.assertIn("/contact/?topic=correction&amp;page=/rulings/in-re-applicant-e/", story)


class DeployedSiteTests(unittest.TestCase):
    def test_placeholder_sponsor_and_consultation_calls_to_action_show_on_the_deployed_site(self):
        files = build_local_site.render_site(SAMPLE_CONTENT)
        for key in ("index.html", "rulings/index.html", "rulings/in-re-applicant-e/index.html", "wire/index.html", "guides/index.html", "guides/searching-before-you-file/index.html"):
            page = files[key].decode("utf-8")
            self.assertIn("ds-sponsor", page, key)
            self.assertIn("Request a consultation", page, key)
            self.assertIn('href="/contact/?topic=consultation"', page, key)
            self.assertNotIn('href="/sponsorship/">Request a consultation', page, key)

    def test_masthead_names_the_publication_in_two_words_with_the_trademark_sign(self):
        home = build_local_site.render_site(SAMPLE_CONTENT)["index.html"].decode("utf-8")
        self.assertIn('<span class="ds-wordmark__distinctive">Distinctive</span>', home)
        self.assertIn('<span class="ds-wordmark__mark">Mark<span class="ds-trademark-sign">™</span></span>', home)
        self.assertIn("<title>Distinctive Mark™", home)


class StandardFrontEndTests(unittest.TestCase):
    """What Papyrus core now provides around the page bodies."""

    @classmethod
    def setUpClass(cls):
        cls.files = build_local_site.render_site(SAMPLE_CONTENT)

    def page(self, key):
        return self.files[key].decode("utf-8")

    def test_story_head_has_canonical_social_cards_and_json_ld_with_modified_date(self):
        story = self.page("rulings/in-re-applicant-e/index.html")
        self.assertIn('<link rel="canonical" href="https://distinctive-mark.com/rulings/in-re-applicant-e/">', story)
        self.assertIn('<meta property="og:type" content="article">', story)
        self.assertIn('<meta name="twitter:card"', story)
        self.assertIn('"@type":"NewsArticle"', story)
        self.assertIn('"dateModified"', story)

    def test_both_feeds_are_advertised_and_published(self):
        home = self.page("index.html")
        self.assertIn('type="application/rss+xml"', home)
        self.assertIn('type="application/atom+xml"', home)
        self.assertIn("<feed ", self.page("atom.xml"))
        self.assertIn('<rss version="2.0"', self.page("feed.xml"))

    def test_the_feeds_carry_commentary_and_rulings_but_not_the_wire_or_guides(self):
        feed = self.page("feed.xml")
        self.assertIn("/rulings/in-re-applicant-e/", feed)
        self.assertIn("/commentary/letters-of-protest/", feed)
        self.assertNotIn("/guides/", feed)
        self.assertNotIn("/wire/", feed)

    def test_the_sitemap_has_lastmod_and_covers_guides_and_standing_pages(self):
        sitemap = self.page("sitemap.xml")
        self.assertIn("<lastmod>", sitemap)
        self.assertIn("/guides/searching-before-you-file/", sitemap)
        self.assertIn("/about/", sitemap)
        self.assertNotIn("/wire/madrid-system-update", sitemap)

    def test_pages_have_a_skip_link_that_reaches_main(self):
        home = self.page("index.html")
        self.assertIn('<a class="markus-skip-link" href="#main">', home)
        self.assertIn('<main id="main"', home)

    def test_a_staging_origin_is_not_indexable(self):
        projector = StandardMarkusProjector.from_static_directory(
            REPOSITORY / "web", environ={"PAPYRUS_SITE_PUBLIC_URL": "https://staging.example.test"}
        )
        self.assertEqual(projector.static_files()["robots.txt"], b"User-agent: *\nDisallow: /\n")
        site, _items = sample_site()
        home = projector.listing_pages(site, keys={"index.html"})["index.html"].decode("utf-8")
        self.assertIn('<meta name="robots" content="noindex, nofollow">', home)


class EscapingTests(unittest.TestCase):
    def test_front_matter_text_is_escaped_in_listings(self):
        projector = create_projector()
        site, _items = sample_site()
        hostile_site = site_with_changed_front_matter(site, "wire/madrid-system-update", title='<script>alert("x")</script>')
        wire_page = projector.listing_pages(hostile_site, keys={"wire/index.html"})["wire/index.html"].decode("utf-8")
        self.assertNotIn('<script>alert("x")</script>', wire_page)
        self.assertIn("&lt;script&gt;", wire_page)


if __name__ == "__main__":
    unittest.main()
