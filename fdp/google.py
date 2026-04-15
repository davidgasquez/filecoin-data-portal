import base64
import json
import os

from google.oauth2 import service_account

CREDENTIALS_ENV_VAR = "ENCODED_GOOGLE_APPLICATION_CREDENTIALS"


def credentials_from_env(
    *,
    scopes: list[str] | None = None,
) -> service_account.Credentials:
    encoded = os.environ.get(CREDENTIALS_ENV_VAR)
    if not encoded:
        raise ValueError(f"Missing {CREDENTIALS_ENV_VAR} in environment")

    try:
        decoded = base64.b64decode(encoded).decode("utf-8")
        payload = json.loads(decoded)
    except Exception as exc:
        raise ValueError(f"Invalid {CREDENTIALS_ENV_VAR} payload") from exc

    if not isinstance(payload, dict):
        raise ValueError(f"Invalid {CREDENTIALS_ENV_VAR} payload")

    return service_account.Credentials.from_service_account_info(payload, scopes=scopes)
