"""Safe JSON response parsing diagnostics without exposing response bodies."""
import json


def decode_json_response(raw, status, content_type, stage):
    """Decode HTTP JSON; report only non-sensitive response metadata on failure."""
    try:
        return json.loads(raw)
    except (ValueError, UnicodeDecodeError) as exc:
        media_type = content_type.split(';', 1)[0].strip()
        raise ValueError(
            f"AUREX_INVALID_JSON stage={stage} status={status} "
            f"content_type={media_type} bytes={len(raw)}"
        ) from exc
