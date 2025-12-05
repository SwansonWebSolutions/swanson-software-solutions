import csv
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify

from website.models import ServiceMarket


class Command(BaseCommand):
    help = (
        "Import US city/state markets from a CSV (simplemaps uszips.csv). "
        "Creates ServiceMarket rows for web development and iOS app development."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--csv",
            dest="csv_path",
            default="uszips.csv",
            help="Path to the uszips.csv file (default: ./uszips.csv)",
        )
        parser.add_argument(
            "--service-types",
            nargs="+",
            choices=[
                ServiceMarket.ServiceType.WEB_DEVELOPMENT,
                ServiceMarket.ServiceType.IOS_APP,
            ],
            default=[
                ServiceMarket.ServiceType.WEB_DEVELOPMENT,
                ServiceMarket.ServiceType.IOS_APP,
            ],
            help="Which service types to generate for each market (default: both).",
        )

    def handle(self, *args, **options):
        csv_path = Path(options["csv_path"])
        if not csv_path.exists():
            raise CommandError(f"CSV file not found: {csv_path}")

        service_types = options["service_types"]
        self.stdout.write(f"Loading markets from {csv_path} for {', '.join(service_types)}")

        with csv_path.open(newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            required_cols = {"city", "state_id", "state_name", "lat", "lng", "zip"}
            missing = required_cols - set(reader.fieldnames or [])
            if missing:
                raise CommandError(f"CSV is missing required columns: {', '.join(sorted(missing))}")

            # Deduplicate by city/state slug; keep first lat/lng seen.
            unique_markets = {}
            for row in reader:
                city = (row.get("city") or "").strip()
                state_id = (row.get("state_id") or "").strip()
                state_name = (row.get("state_name") or "").strip()
                if not city or not state_id or not state_name:
                    continue

                slug_city = slugify(city)
                slug_state = slugify(state_name) or slugify(state_id)
                key = (slug_state, slug_city)
                if key in unique_markets:
                    continue
                try:
                    lat = float(row.get("lat")) if row.get("lat") else None
                    lng = float(row.get("lng")) if row.get("lng") else None
                except (TypeError, ValueError):
                    lat = lng = None

                unique_markets[key] = {
                    "city": city,
                    "state_id": state_id,
                    "state_name": state_name,
                    "slug_state": slug_state,
                    "slug_city": slug_city,
                    "latitude": lat,
                    "longitude": lng,
                    "zip_code": (row.get("zip") or "").strip(),
                }

        existing_keys = set(
            ServiceMarket.objects.values_list("slug_state", "slug_city", "service_type")
        )

        to_create = []
        for (slug_state, slug_city), payload in unique_markets.items():
            for service_type in service_types:
                key = (slug_state, slug_city, service_type)
                if key in existing_keys:
                    continue
                to_create.append(ServiceMarket(service_type=service_type, **payload))

        if not to_create:
            self.stdout.write(self.style.WARNING("No new markets to import."))
            return

        ServiceMarket.objects.bulk_create(to_create, batch_size=1000, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS(f"Imported {len(to_create)} service markets."))
