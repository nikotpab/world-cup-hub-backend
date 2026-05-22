"""
AWS Lambda handler — Daily Pack Distribution
Triggered by EventBridge rule: cron(0 5 * * ? *)  →  05:00 UTC = 00:00 UTC-5

Environment variables required (injected from Secrets Manager via App Runner / Lambda):
  DATABASE_URL, SECRET_KEY, JWT_SECRET_KEY, FLASK_ENV=production
"""
import json
import logging
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

DAILY_FREE_PACKS = 3


def handler(event, context):
    os.environ.setdefault('FLASK_ENV', 'production')

    from app import create_app
    app = create_app()

    with app.app_context():
        from datetime import datetime, timezone, timedelta
        from app.infrastructure.database import db
        from app.domain.models.user import User
        from app.domain.models.album import Album
        from app.infrastructure.external.notification_service import notification_service

        UTC_MINUS_5 = timezone(timedelta(hours=-5))
        today = datetime.now(UTC_MINUS_5).date()
        distributed = 0

        users = User.query.filter_by(verified=True, accountStatus='activo').all()
        for user in users:
            try:
                album = Album.query.filter_by(idUser=user.idUser).first()
                if not album:
                    album = Album(idUser=user.idUser, packBalance=0, coins=0)
                    db.session.add(album)
                if album.lastRewardDate != today:
                    album.lastRewardDate = today
                    album.packBalance = (album.packBalance or 0) + DAILY_FREE_PACKS
                    distributed += 1
                    try:
                        notification_service.notify_user_from_id(
                            user_id=user.idUser,
                            title="¡Nuevos sobres disponibles!",
                            body=f"Tienes {DAILY_FREE_PACKS} sobres listos para abrir. ¡Entra a la app!",
                            notif_type="packs",
                        )
                    except Exception:
                        pass
            except Exception:
                pass

        db.session.commit()
        logger.info({"event": "daily_packs_distributed", "users": distributed,
                     "packs": DAILY_FREE_PACKS, "date": str(today)})

    return {
        "statusCode": 200,
        "body": json.dumps({"distributed": distributed, "date": str(today)})
    }
