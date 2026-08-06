import hashlib
import hmac
import json
import logging

from django.conf import settings
from django.http import HttpRequest, JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import Insight

logger = logging.getLogger(__name__)

EVENT_POST_PUBLISHED = "post.published"


def _is_valid_signature(request: HttpRequest) -> bool:
    secret = getattr(settings, "VIBESEO_WEBHOOK_SECRET", "")
    if not secret:
        logger.warning("VIBESEO_WEBHOOK_SECRET is not configured; rejecting webhook request.")
        return False

    signature_header = request.headers.get("X-VibeSEO-Signature", "")
    if not signature_header.startswith("sha256="):
        return False

    provided_digest = signature_header[len("sha256="):]
    expected_digest = hmac.new(
        secret.encode("utf-8"),
        request.body,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(provided_digest, expected_digest)


@csrf_exempt
@require_POST
def vibeseo_webhook(request: HttpRequest) -> JsonResponse:
    if not _is_valid_signature(request):
        logger.warning("Rejected VibeSEO webhook request: invalid or missing signature.")
        return JsonResponse({"status": "error", "detail": "invalid signature"}, status=401)

    try:
        payload = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        logger.warning("Rejected VibeSEO webhook request: malformed JSON body.")
        return JsonResponse({"status": "error", "detail": "malformed JSON"}, status=400)

    event = payload.get("event")
    if event != EVENT_POST_PUBLISHED:
        logger.info("Ignoring VibeSEO webhook event: %s", event)
        return JsonResponse({"status": "ignored"}, status=200)

    post_data = payload.get("post") or {}
    vibeseo_post_id = post_data.get("id")
    meta_description = post_data.get("metaDescription", "")

    insight, created = Insight.objects.update_or_create(
        vibeseo_post_id=vibeseo_post_id,
        defaults={
            "title": post_data.get("title", ""),
            "slug": post_data.get("slug") or "",
            "description": meta_description,
            "topic": Insight.TOPIC_GENERAL,
            "body_markdown": post_data.get("body", ""),
            "seo_title": post_data.get("metaTitle", ""),
            "seo_description": meta_description,
            "focus_keyword": post_data.get("focusKeyword", ""),
            "seo_score": post_data.get("seoScore"),
            "faq": post_data.get("faq") or [],
            "internal_links": post_data.get("internalLinks") or [],
            "status": Insight.STATUS_PUBLISHED,
            "published_at": post_data.get("publishedAt") or timezone.now(),
            "vibeseo_published_at": post_data.get("publishedAt") or timezone.now(),
        },
    )

    action = "created" if created else "updated"
    logger.info("VibeSEO webhook %s post id=%s slug=%s", action, insight.vibeseo_post_id, insight.slug)

    return JsonResponse(
        {"status": "ok", "action": action, "postId": insight.vibeseo_post_id, "slug": insight.slug},
        status=201 if created else 200,
    )
