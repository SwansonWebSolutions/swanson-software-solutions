from django.test import TestCase

from insights.models import Insight


class InsightModelTests(TestCase):
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
