from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.core import mail
from django.core.management import call_command

from website.models import (
    Consumer,
    ConsumerBrokerStatus,
    DataBrokers2025,
    BrokerCompliance,
    NewsletterSubscriber,
)
from insights.models import Insight


class BrokerComplianceViewTests(TestCase):
    def setUp(self):
        self.broker = DataBrokers2025.objects.create(name="Acme Data", state="CA")
        self.consumer = Consumer.objects.create(
            first_name="Jane",
            last_name="Doe",
            primary_email="jane@example.com",
        )
        # Consumer post-save initializes statuses; reuse or create if missing
        existing = self.consumer.broker_statuses.filter(broker=self.broker).first()
        if existing:
            self.status = existing
            self.status.status = ConsumerBrokerStatus.Status.QUEUED
            self.status.request_type = ConsumerBrokerStatus.RequestType.DELETE
            self.status.save(update_fields=["status", "request_type", "updated_at"])
        else:
            self.status = ConsumerBrokerStatus.objects.create(
                consumer=self.consumer,
                broker=self.broker,
                status=ConsumerBrokerStatus.Status.QUEUED,
                request_type=ConsumerBrokerStatus.RequestType.DELETE,
            )
        self.compliance = BrokerCompliance.objects.create(
            broker=self.broker,
            token=BrokerCompliance.generate_token(),
        )

    def test_uuid_token_get_renders_form(self):
        url = reverse("website:broker-compliance-token", args=[self.status.tracking_token])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, self.consumer.full_name)
        self.assertContains(resp, self.broker.name)

    def test_uuid_token_post_valid_updates_status(self):
        url = reverse("website:broker-compliance-token", args=[self.status.tracking_token])
        resp = self.client.post(
            url,
            {
                "response_status": ConsumerBrokerStatus.Status.COMPLETED,
                "contact_name": "Agent",
                "contact_email": "agent@example.com",
                "notes": "Done",
                "t": str(self.status.tracking_token),
            },
        )
        self.assertEqual(resp.status_code, 200)
        self.status.refresh_from_db()
        self.assertEqual(self.status.status, ConsumerBrokerStatus.Status.COMPLETED)
        self.assertIsNotNone(self.status.completed_at)

    def test_uuid_token_post_invalid_shows_error(self):
        url = reverse("website:broker-compliance-token", args=[self.status.tracking_token])
        resp = self.client.post(url, {"response_status": "not-valid", "t": str(self.status.tracking_token)})
        self.assertEqual(resp.status_code, 200)
        self.status.refresh_from_db()
        self.assertEqual(self.status.status, ConsumerBrokerStatus.Status.QUEUED)

    def test_compliance_token_get_renders_form(self):
        url = reverse("website:broker-compliance") + f"?t={self.compliance.token}"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, self.broker.name)

    def test_compliance_token_post_marks_submitted(self):
        url = reverse("website:broker-compliance")
        resp = self.client.post(
            url,
            {
                "response_status": ConsumerBrokerStatus.Status.COMPLETED,
                "contact_name": "Agent",
                "contact_email": "agent@example.com",
                "notes": "Done",
                "t": self.compliance.token,
            },
        )
        self.assertEqual(resp.status_code, 200)
        self.compliance.refresh_from_db()
        self.assertTrue(self.compliance.submitted)
        self.assertIsNotNone(self.compliance.submitted_at)
        self.assertEqual(self.compliance.contact_name, "Agent")
        self.assertEqual(self.compliance.contact_email, "agent@example.com")

    def test_missing_token_returns_400(self):
        url = reverse("website:broker-compliance")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 400)

    def test_invalid_token_returns_404(self):
        url = reverse("website:broker-compliance") + "?t=not-found"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_tracking_token_submission_returns_success_page(self):
        url = reverse("website:broker-compliance-token", args=[self.status.tracking_token])
        resp = self.client.post(
            url,
            {
                "response_status": ConsumerBrokerStatus.Status.PROCESSING,
                "contact_name": "Agent",
                "contact_email": "agent@example.com",
                "notes": "Working on it",
                "t": str(self.status.tracking_token),
            },
        )
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Thank you")
        self.assertContains(resp, "has been recorded")
        self.status.refresh_from_db()
        self.assertEqual(self.status.status, ConsumerBrokerStatus.Status.PROCESSING)


class NewsletterSubscribeTests(TestCase):
    def setUp(self):
        mail.outbox.clear()

    def test_subscribe_creates_record_and_redirects(self):
        resp = self.client.post(
            reverse("website:newsletter-subscribe"),
            {"email": "Test@Example.com", "next": "/"},
            follow=True,
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(NewsletterSubscriber.objects.filter(email="test@example.com").exists())
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Welcome to the SwanTech newsletter", mail.outbox[0].subject)

    def test_invalid_email_shows_error(self):
        resp = self.client.post(
            reverse("website:newsletter-subscribe"),
            {"email": "not-an-email", "next": "/"},
            follow=True,
        )
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(NewsletterSubscriber.objects.exists())

    def test_duplicate_subscribe_does_not_duplicate(self):
        NewsletterSubscriber.objects.create(email="hello@example.com")
        resp = self.client.post(
            reverse("website:newsletter-subscribe"),
            {"email": "hello@example.com", "next": "/"},
            follow=True,
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(NewsletterSubscriber.objects.filter(email="hello@example.com").count(), 1)
        self.assertEqual(len(mail.outbox), 0)


class NewsletterCommandTests(TestCase):
    def setUp(self):
        mail.outbox.clear()
        # Create subscribers
        NewsletterSubscriber.objects.create(email="alice@example.com")
        NewsletterSubscriber.objects.create(email="bob@example.com")
        # Four insights; only newest 3 (by created_at) should be included
        Insight.objects.create(title="Old Insight", description="Old desc", topic=Insight.TOPIC_DATA_PRIVACY)
        Insight.objects.create(title="Insight 1", description="Desc 1", topic=Insight.TOPIC_WEB_DEV)
        Insight.objects.create(title="Insight 2", description="Desc 2", topic=Insight.TOPIC_IOS)
        Insight.objects.create(title="Insight 3", description="Desc 3", topic=Insight.TOPIC_MARKETING)

    def test_command_sends_to_all_subscribers_with_latest_three_insights(self):
        call_command("send_newsletter")
        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertIn("weekly insights", message.subject.lower())
        self.assertCountEqual(message.bcc, ["alice@example.com", "bob@example.com"])
        body = message.body
        self.assertIn("Insight 1", body)
        self.assertIn("Insight 2", body)
        self.assertIn("Insight 3", body)
        self.assertNotIn("Old Insight", body)
