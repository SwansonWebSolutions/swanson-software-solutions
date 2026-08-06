import hashlib
import hmac
import json

from django.test import Client, TestCase, override_settings
from django.urls import reverse

from insights.models import Insight

WEBHOOK_SECRET = "test-secret"


def _sign(body: bytes) -> str:
    digest = hmac.new(WEBHOOK_SECRET.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


def _payload(event: str = "post.published") -> dict:
    return {
        "event": event,
        "post": {
            "id": 123,
            "title": "How to Build a SaaS in 2026",
            "slug": "how-to-build-a-saas-2026",
            "body": "## Introduction\n\nBuilding a SaaS product...",
            "metaTitle": "How to Build a SaaS in 2026 | SwanTech",
            "metaDescription": "Step-by-step guide to launching your SaaS product fast.",
            "focusKeyword": "build a saas",
            "seoScore": 87,
            "faq": [{"question": "How long does it take?", "answer": "Typically 3-6 months."}],
            "internalLinks": [{"text": "our pricing", "url": "/pricing"}],
            "publishedAt": "2026-08-07T09:00:00Z",
        },
    }


@override_settings(VIBESEO_WEBHOOK_SECRET=WEBHOOK_SECRET)
class VibeSEOWebhookTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("insights:vibeseo_webhook")

    def _post(self, payload: dict, signature: str | None = None):
        body = json.dumps(payload).encode("utf-8")
        headers = {}
        if signature is not None:
            headers["HTTP_X_VIBESEO_SIGNATURE"] = signature
        return self.client.post(self.url, data=body, content_type="application/json", **headers)

    def test_valid_signed_payload_creates_insight(self):
        payload = _payload()
        body = json.dumps(payload).encode("utf-8")
        response = self._post(payload, _sign(body))

        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["action"], "created")

        insight = Insight.objects.get(vibeseo_post_id=123)
        self.assertEqual(insight.topic, Insight.TOPIC_GENERAL)
        self.assertEqual(insight.status, Insight.STATUS_PUBLISHED)
        self.assertEqual(insight.focus_keyword, "build a saas")
        self.assertEqual(insight.seo_score, 87)
        self.assertEqual(insight.faq, payload["post"]["faq"])
        self.assertEqual(insight.internal_links, payload["post"]["internalLinks"])
        self.assertTrue(insight.sections.filter(order=0).exists())

    def test_repeated_payload_updates_not_duplicates(self):
        payload = _payload()
        body = json.dumps(payload).encode("utf-8")
        self._post(payload, _sign(body))

        response = self._post(payload, _sign(body))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["action"], "updated")
        self.assertEqual(Insight.objects.filter(vibeseo_post_id=123).count(), 1)

    def test_invalid_signature_returns_401(self):
        payload = _payload()
        response = self._post(payload, "sha256=deadbeef")
        self.assertEqual(response.status_code, 401)

    def test_missing_signature_returns_401(self):
        payload = _payload()
        response = self._post(payload, signature=None)
        self.assertEqual(response.status_code, 401)

    def test_unknown_event_type_ignored(self):
        payload = _payload(event="post.deleted")
        body = json.dumps(payload).encode("utf-8")
        response = self._post(payload, _sign(body))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ignored")
        self.assertFalse(Insight.objects.filter(vibeseo_post_id=123).exists())

    def test_malformed_json_returns_400(self):
        body = b"{not valid json"
        response = self.client.post(
            self.url,
            data=body,
            content_type="application/json",
            HTTP_X_VIBESEO_SIGNATURE=_sign(body),
        )
        self.assertEqual(response.status_code, 400)

    def test_get_request_returns_405(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)
