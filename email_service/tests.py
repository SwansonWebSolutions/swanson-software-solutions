from datetime import timedelta

from django.core import mail
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.utils import timezone

from website.models import (
    BrokerContactLog,
    Consumer,
    ConsumerBrokerStatus,
    DataBrokers2025,
)


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="support@example.com",
)
class SendConsumerWeeklyStatusCommandTests(TestCase):
    def test_sends_weekly_status_and_updates_timestamp(self):
        consumer = Consumer.objects.create(
            first_name="Pat",
            last_name="Smith",
            primary_email="daswanson22@gmail.com",
            weekly_status_opt_in=True,
        )
        broker1 = DataBrokers2025.objects.create(name="Acme Data")
        broker2 = DataBrokers2025.objects.create(name="Beta Data")
        broker3 = DataBrokers2025.objects.create(name="Gamma Data")

        ConsumerBrokerStatus.objects.create(
            consumer=consumer,
            broker=broker1,
            status=ConsumerBrokerStatus.Status.QUEUED,
        )
        ConsumerBrokerStatus.objects.create(
            consumer=consumer,
            broker=broker2,
            status=ConsumerBrokerStatus.Status.PROCESSING,
        )
        ConsumerBrokerStatus.objects.create(
            consumer=consumer,
            broker=broker3,
            status=ConsumerBrokerStatus.Status.COMPLETED,
            completed_at=timezone.now() - timedelta(days=1),
        )

        before_run = timezone.now()
        call_command("send_consumer_weekly_status", days=7)

        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertIn("Weekly Status Update", message.subject)
        self.assertIn("Total brokers tracked: 3", message.body)
        self.assertIn("New confirmations this week: 1", message.body)

        consumer.refresh_from_db()
        self.assertIsNotNone(consumer.last_status_email_at)
        self.assertGreater(consumer.last_status_email_at, before_run)


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="support@example.com",
    TEST_BROKER_RECIPIENTS=["daswanson22@gmail.com"],
    PUBLIC_BASE_URL="https://example.com",
)
class SendConsumerBrokerDripCommandTests(TestCase):
    def test_sends_outreach_email_and_marks_status_contacted(self):
        consumer = Consumer.objects.create(
            first_name="Casey",
            last_name="Lee",
            primary_email="casey@example.com",
        )
        broker = DataBrokers2025.objects.create(
            name="DataCo",
            contact_email="to-ignore@example.com",
        )
        status = ConsumerBrokerStatus.objects.create(
            consumer=consumer,
            broker=broker,
            status=ConsumerBrokerStatus.Status.QUEUED,
            request_type=ConsumerBrokerStatus.RequestType.DELETE,
        )

        call_command(
            "send_consumer_broker_drip",
            consumer_id=consumer.id,
            test=True,
            subject="Request for {consumer} / {broker}",
        )

        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertIn(broker.name, message.subject)
        self.assertIn("stop my spam", message.body.lower())

        status.refresh_from_db()
        self.assertEqual(status.status, ConsumerBrokerStatus.Status.CONTACTED)
        self.assertIsNotNone(status.contacted_at)
        self.assertEqual(status.batch_number, 1)

        log = BrokerContactLog.objects.filter(status=status).first()
        self.assertIsNotNone(log)
        self.assertTrue(log.success)

        drip_state = consumer.drip_state
        self.assertEqual(drip_state.last_batch_size, 1)
