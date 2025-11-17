from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from website.models import (
    Consumer,
    ConsumerBrokerStatus,
    DataBrokers2025,
    BrokerCompliance,
)


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
