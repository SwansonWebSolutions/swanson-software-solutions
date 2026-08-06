from django.test import TestCase

from insights.models import Insight


class InsightVibeSEOModelTests(TestCase):
    def test_body_markdown_rendered_into_first_section_on_save(self):
        insight = Insight.objects.create(
            title="Hello World",
            description="desc",
            topic=Insight.TOPIC_GENERAL,
            body_markdown="## Heading\n\nSome **bold** text.",
        )
        section = insight.sections.get(order=0)
        self.assertIn("<h2", section.content)
        self.assertIn("<strong>bold</strong>", section.content)

    def test_slug_auto_generated_from_title(self):
        insight = Insight.objects.create(
            title="How to Build a SaaS in 2026",
            description="desc",
            topic=Insight.TOPIC_GENERAL,
        )
        self.assertEqual(insight.slug, "how-to-build-a-saas-in-2026")

    def test_provided_slug_not_overwritten(self):
        insight = Insight.objects.create(
            title="Some Title",
            slug="custom-slug",
            description="desc",
            topic=Insight.TOPIC_GENERAL,
        )
        self.assertEqual(insight.slug, "custom-slug")

    def test_insights_without_body_markdown_get_no_auto_section(self):
        insight = Insight.objects.create(
            title="Manually Written",
            description="desc",
            topic=Insight.TOPIC_MARKETING,
        )
        self.assertEqual(insight.sections.count(), 0)
