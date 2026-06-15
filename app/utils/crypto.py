import hashlib
import hmac
import json


def verify_nowpayments_signature(raw_body: bytes, signature: str, secret: str) -> bool:
    """
    Verify the x-nowpayments-sig HMAC-SHA512 signature.
    NOWPayments sorts the JSON payload keys before signing.
    """
    try:
        data = json.loads(raw_body.decode("utf-8"))
    except Exception:
        return False
    sorted_data = json.dumps(data, separators=(",", ":"), sort_keys=True)
    digest = hmac.new(
        secret.encode(), sorted_data.encode(), hashlib.sha512
    ).hexdigest()
    return hmac.compare_digest(digest, signature)


def constant_time_equal(left: str, right: str) -> bool:
    """Timing-safe string comparison for secrets."""
    return hmac.compare_digest(left.encode(), right.encode())
