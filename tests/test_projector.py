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
import projector as distinctive_projector  # noqa: E402
from papyrus_content.projection.model import SiteIndex  # noqa: E402

SAMPLE_CONTENT = REPOSITORY / "sample-content"


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
        self.assertFalse(any(key.startswith("wire/") and key != "wire/index.html" for key in self.files))
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
        self.projector = distinctive_projector.create_projector()
        self.site, _items = sample_site()

    def test_editing_a_wire_item_rerenders_wire_and_front_page_only(self):
        before = self.projector.listing_inputs(self.site)
        changed_site = site_with_changed_front_matter(self.site, "wire/madrid-system-update", take="A different take.")
        after = self.projector.listing_inputs(changed_site)
        changed_keys = {key for key in before if before[key] != after[key]}
        self.assertEqual(changed_keys, {"index.html", "wire/index.html"})

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


class EscapingTests(unittest.TestCase):
    def test_front_matter_text_is_escaped_in_listings(self):
        projector = distinctive_projector.create_projector()
        site, _items = sample_site()
        hostile_site = site_with_changed_front_matter(site, "wire/madrid-system-update", title='<script>alert("x")</script>')
        wire_page = projector.listing_pages(hostile_site, keys={"wire/index.html"})["wire/index.html"].decode("utf-8")
        self.assertNotIn('<script>alert("x")</script>', wire_page)
        self.assertIn("&lt;script&gt;", wire_page)


if __name__ == "__main__":
    unittest.main()
