import csv
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from website.models import DataBrokers2025


class Command(BaseCommand):
    help = "Import the California Data Broker Registry 2025 CSV into DataBrokers2025."

    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            help="Path to the CSV file. Defaults to '<BASE_DIR>/California Data Broker Registry 2025.csv'",
        )
        parser.add_argument(
            "--truncate",
            action="store_true",
            help="Delete existing rows before importing.",
        )

    def handle(self, *args, **opts):
        default_path = Path(settings.BASE_DIR) / "California Data Broker Registry 2025.csv"
        path = Path(opts.get("path") or default_path)
        if not path.exists():
            raise CommandError(f"CSV not found at: {path}")

        if opts.get("truncate"):
            self.stdout.write("Truncating DataBrokers2025 table…")
            DataBrokers2025.objects.all().delete()

        self.stdout.write(f"Reading: {path}")

        # Read file and derive headers (skip first non-header row)
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.reader(f)
            try:
                next(reader)  # discard preface row
                headers = next(reader)
            except StopIteration:
                raise CommandError("CSV file appears empty or malformed.")

            dict_reader = csv.DictReader(f, fieldnames=headers)

            def find_header(*keywords: str):
                for h in headers:
                    lh = (h or "").lower()
                    if all(k in lh for k in keywords):
                        return h
                return None

            # Resolve header keys robustly (handles odd characters from export)
            name_key = find_header("data broker", "name")
            dba_key = find_header("doing business as")
            web_key = find_header("primary website")
            email_key = find_header("primary contact", "email")
            phone_key = find_header("primary phone")
            street_key = find_header("primary street address")
            city_key = find_header("city")
            state_key = find_header("state")
            zip_key = find_header("zip")
            country_key = find_header("country")
            privacy_key = find_header("privacy", "policy") or find_header("contains details", "privacy")

            created = 0
            batch: list[DataBrokers2025] = []

            for row in dict_reader:
                if not any((row or {}).values()):
                    continue
                name = (row.get(name_key) or "").strip()
                if not name:
                    # skip blank rows
                    continue

                obj = DataBrokers2025(
                    name=name,
                    dba=(row.get(dba_key) or "").strip() if dba_key else "",
                    website=(row.get(web_key) or "").strip() if web_key else "",
                    contact_email=(row.get(email_key) or "").strip() if email_key else "",
                    phone=(row.get(phone_key) or "").strip() if phone_key else "",
                    street=(row.get(street_key) or "").strip() if street_key else "",
                    city=(row.get(city_key) or "").strip() if city_key else "",
                    state=(row.get(state_key) or "").strip() if state_key else "",
                    postal_code=(row.get(zip_key) or "").strip() if zip_key else "",
                    country=(row.get(country_key) or "").strip() if country_key else "",
                    privacy_url=(row.get(privacy_key) or "").strip() if privacy_key else "",
                    raw={k: (v if v is not None else "") for k, v in (row or {}).items()},
                )
                batch.append(obj)
                if len(batch) >= 500:
                    DataBrokers2025.objects.bulk_create(batch)
                    created += len(batch)
                    batch.clear()

            if batch:
                DataBrokers2025.objects.bulk_create(batch)
                created += len(batch)

        self.stdout.write(self.style.SUCCESS(f"Imported {created} brokers into DataBrokers2025."))

