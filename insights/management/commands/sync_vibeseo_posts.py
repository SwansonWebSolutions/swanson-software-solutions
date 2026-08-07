import httpx
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from email_service.logger import get_script_logger
from insights.models import Insight, InsightSection

VIBESEO_POSTS_URL = "https://api.vibeseo.dev/api/v1/integrations/blog/posts"
SITE_LANGUAGE_CODE = "en"


class Command(BaseCommand):
    help = "Pull published posts from VibeSEO's read API and sync them into Insight."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Log what would change without writing to the database.",
        )

    def handle(self, *args, **options):
        logger = get_script_logger("sync_vibeseo_posts")
        dry_run = options["dry_run"]

        api_key = getattr(settings, "VIBESEO_API_KEY", "")
        if not api_key:
            logger.error("VIBESEO_API_KEY is not configured; aborting sync.")
            raise CommandError("VIBESEO_API_KEY is not configured.")

        try:
            response = httpx.get(
                VIBESEO_POSTS_URL,
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=15,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.error("Failed to fetch VibeSEO posts: %s", exc)
            raise CommandError(f"Failed to fetch VibeSEO posts: {exc}")

        posts = response.json()
        current_ids = {post["id"] for post in posts}

        created = updated = skipped = 0

        for post in posts:
            if post.get("languageCode") != SITE_LANGUAGE_CODE:
                logger.info("Skipping post id=%s: languageCode=%s", post.get("id"), post.get("languageCode"))
                skipped += 1
                continue

            if dry_run:
                exists = Insight.objects.filter(vibeseo_post_id=post["id"]).exists()
                logger.info("[dry-run] would %s post id=%s", "update" if exists else "create", post["id"])
                updated += exists
                created += not exists
                continue

            insight, was_created = Insight.objects.update_or_create(
                vibeseo_post_id=post["id"],
                defaults={
                    "title": post.get("title", ""),
                    "slug": post.get("slug") or "",
                    "description": post.get("metaDescription") or "",
                    "seo_title": post.get("metaTitle") or "",
                    "featured_image_url": post.get("heroImageUrl") or "",
                    "topic": Insight.TOPIC_GENERAL,
                    "status": Insight.STATUS_PUBLISHED,
                    "published_at": post.get("publishedAt"),
                    "vibeseo_published_at": post.get("publishedAt"),
                },
            )
            InsightSection.objects.update_or_create(
                insight=insight, order=0,
                defaults={"heading": "", "content": post.get("bodyHtml") or ""},
            )
            created += was_created
            updated += not was_created

        if dry_run:
            retired = Insight.objects.filter(
                vibeseo_post_id__isnull=False
            ).exclude(vibeseo_post_id__in=current_ids).count()
        else:
            retired = Insight.objects.filter(
                vibeseo_post_id__isnull=False
            ).exclude(vibeseo_post_id__in=current_ids).update(status=Insight.STATUS_DRAFT)

        logger.info(
            "%sVibeSEO sync complete: created=%s updated=%s retired=%s skipped=%s",
            "[dry-run] " if dry_run else "",
            created, updated, retired, skipped,
        )
