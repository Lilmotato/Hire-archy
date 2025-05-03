import os
import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import firebase_admin
from firebase_admin import credentials, auth

# --- Logger ---
logger = logging.getLogger(__name__)

# --- Firebase Initialization ---
SERVICE_ACCOUNT_KEY_PATH = "app/config/serviceAccountKey.json"

try:
    if not os.path.exists(SERVICE_ACCOUNT_KEY_PATH):
        raise FileNotFoundError(
            f"Firebase service account key not found at: {os.path.abspath(SERVICE_ACCOUNT_KEY_PATH)}\n"
            "Please check your path and service account file."
        )
    cred = credentials.Certificate(SERVICE_ACCOUNT_KEY_PATH)
    firebase_admin.initialize_app(cred)
    logger.info("✅ Firebase Admin SDK initialized successfully.")
except Exception as e:
    logger.critical(f"🔥 FATAL: Firebase initialization failed: {e}")
    raise SystemExit("Firebase Admin SDK initialization failed.")

# --- Authentication ---
token_auth_scheme = HTTPBearer()

async def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(token_auth_scheme),
) -> dict:
    """
    Dependency to verify Firebase Bearer token.
    Returns decoded claims.
    Raises HTTPException for invalid tokens.
    """
    try:
        decoded_token = auth.verify_id_token(token.credentials, check_revoked=True)
        logger.debug(f"Token verified successfully for UID: {decoded_token.get('uid')}")
        return decoded_token

    except auth.ExpiredIdTokenError:
        logger.warning("Token expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except auth.RevokedIdTokenError:
        logger.warning("Token revoked")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked (user logged out)",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except auth.InvalidIdTokenError:
        logger.warning("Invalid token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal authentication error",
        )
