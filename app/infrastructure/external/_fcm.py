"""
Firebase Cloud Messaging push helper.
Uses firebase-admin SDK when GOOGLE_APPLICATION_CREDENTIALS or
FIREBASE_SERVICE_ACCOUNT_JSON env-var is set; silently no-ops otherwise
so local dev never requires FCM credentials.
"""
import os
import json

_app = None


def _get_app():
    global _app
    if _app is not None:
        return _app
    try:
        import firebase_admin
        from firebase_admin import credentials

        sa_json = os.environ.get("FIREBASE_SERVICE_ACCOUNT_JSON")
        cred_file = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

        if sa_json:
            sa_dict = json.loads(sa_json)
            cred = credentials.Certificate(sa_dict)
        elif cred_file and os.path.exists(cred_file):
            cred = credentials.Certificate(cred_file)
        else:
            return None  # no credentials — FCM unavailable

        _app = firebase_admin.initialize_app(cred)
    except Exception:
        _app = None
    return _app


def send_push(token: str, title: str, body: str, data: dict = None) -> None:
    """Send a push notification via FCM. Raises on failure."""
    app = _get_app()
    if app is None:
        raise RuntimeError("FCM not configured (no FIREBASE_SERVICE_ACCOUNT_JSON or GOOGLE_APPLICATION_CREDENTIALS)")

    from firebase_admin import messaging
    str_data = {k: str(v) for k, v in (data or {}).items()}
    message = messaging.Message(
        notification=messaging.Notification(title=title, body=body),
        data=str_data,
        token=token,
    )
    messaging.send(message, app=app)
