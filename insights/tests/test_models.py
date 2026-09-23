from django.test import TestCase
from django.utils import timezone

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

    def test_publishing_sets_publication_date_for_admin_posts(self):
        insight = Insight.objects.create(
            title="Admin-authored insight",
            description="desc",
            topic=Insight.TOPIC_GENERAL,
        )

        insight.status = Insight.STATUS_PUBLISHED
        insight.save()

        self.assertIsNotNone(insight.published_at)
        self.assertLessEqual(insight.published_at, timezone.now())

    def test_existing_publication_date_is_preserved(self):
        published_at = timezone.datetime(2026, 1, 15, tzinfo=timezone.get_current_timezone())
        insight = Insight.objects.create(
            title="Imported insight",
            description="desc",
            topic=Insight.TOPIC_GENERAL,
            status=Insight.STATUS_PUBLISHED,
            published_at=published_at,
        )

        insight.save()

        self.assertEqual(insight.published_at, published_at)
