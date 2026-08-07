from unittest import mock

import httpx
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings

from insights.models import Insight, InsightSection


def _post(post_id=1208, **overrides):
    data = {
        "id": post_id,
        "slug": "how-to-build-a-social-network-website",
        "title": "Building a Social Network Website",
        "metaTitle": None,
        "metaDescription": "Learn how to build a social network website.",
        "bodyHtml": "<h2>Intro</h2><p>Hello world.</p>",
        "heroImageUrl": "https://cdn.vibeseo.site/posts/hero.jpg",
        "publishedAt": "2026-08-07T00:02:09.870605Z",
        "languageCode": "en",
    }
    data.update(overrides)
    return data


def _mock_response(posts):
    response = mock.Mock()
    response.raise_for_status = mock.Mock()
    response.json.return_value = posts
    return response


@override_settings(VIBESEO_API_KEY="test-key")
class SyncVibeSEOPostsTests(TestCase):
    @mock.patch("insights.management.commands.sync_vibeseo_posts.httpx.get")
    def test_fresh_pull_creates_insight_and_section(self, mock_get):
        mock_get.return_value = _mock_response([_post()])

        call_command("sync_vibeseo_posts")

        insight = Insight.objects.get(vibeseo_post_id=1208)
        self.assertEqual(insight.status, Insight.STATUS_PUBLISHED)
        self.assertEqual(insight.topic, Insight.TOPIC_GENERAL)
        self.assertEqual(insight.seo_title, "")  # metaTitle was null, falls back via get_effective_seo_title()
        self.assertEqual(insight.get_effective_seo_title(), insight.title)
        self.assertEqual(insight.featured_image_url, "https://cdn.vibeseo.site/posts/hero.jpg")

        section = insight.sections.get(order=0)
        self.assertEqual(section.content, "<h2>Intro</h2><p>Hello world.</p>")

    @mock.patch("insights.management.commands.sync_vibeseo_posts.httpx.get")
    def test_rerun_upserts_not_duplicates(self, mock_get):
        mock_get.return_value = _mock_response([_post()])

        call_command("sync_vibeseo_posts")
        call_command("sync_vibeseo_posts")

        self.assertEqual(Insight.objects.filter(vibeseo_post_id=1208).count(), 1)
        self.assertEqual(InsightSection.objects.filter(insight__vibeseo_post_id=1208).count(), 1)

    @mock.patch("insights.management.commands.sync_vibeseo_posts.httpx.get")
    def test_post_missing_from_pull_is_retired(self, mock_get):
        mock_get.return_value = _mock_response([
            _post(post_id=1, slug="post-one", title="Post One"),
            _post(post_id=2, slug="post-two", title="Post Two"),
        ])
        call_command("sync_vibeseo_posts")

        mock_get.return_value = _mock_response([_post(post_id=1)])
        call_command("sync_vibeseo_posts")

        retired = Insight.objects.get(vibeseo_post_id=2)
        self.assertEqual(retired.status, Insight.STATUS_DRAFT)
        still_published = Insight.objects.get(vibeseo_post_id=1)
        self.assertEqual(still_published.status, Insight.STATUS_PUBLISHED)

    @mock.patch("insights.management.commands.sync_vibeseo_posts.httpx.get")
    def test_manual_insight_untouched_by_retirement(self, mock_get):
        manual = Insight.objects.create(
            title="Manually Written", description="desc", topic=Insight.TOPIC_MARKETING,
            status=Insight.STATUS_PUBLISHED,
        )
        mock_get.return_value = _mock_response([])

        call_command("sync_vibeseo_posts")

        manual.refresh_from_db()
        self.assertEqual(manual.status, Insight.STATUS_PUBLISHED)

    @override_settings(VIBESEO_API_KEY="")
    def test_missing_api_key_raises_command_error(self):
        with self.assertRaises(CommandError):
            call_command("sync_vibeseo_posts")

    @mock.patch("insights.management.commands.sync_vibeseo_posts.httpx.get")
    def test_http_error_raises_command_error(self, mock_get):
        mock_get.side_effect = httpx.ConnectError("boom")

        with self.assertRaises(CommandError):
            call_command("sync_vibeseo_posts")

    @mock.patch("insights.management.commands.sync_vibeseo_posts.httpx.get")
    def test_dry_run_makes_no_writes(self, mock_get):
        mock_get.return_value = _mock_response([_post()])

        call_command("sync_vibeseo_posts", "--dry-run")

        self.assertEqual(Insight.objects.count(), 0)
