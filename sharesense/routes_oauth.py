"""
Google OAuth 2.0 routes.

Flow:
  GET  /api/auth/google           → redirect to Google consent screen
  GET  /api/auth/google/callback  → exchange code, upsert user, issue JWT,
                                    redirect to frontend with token in fragment
"""

import uuid

import requests
from authlib.integrations.requests_client import OAuth2Session
from flask import Blueprint, redirect, request

import config
from auth import create_token
from database import get_db

bp = Blueprint("oauth", __name__, url_prefix="/api/auth")

_GOOGLE_AUTH_URL  = "https://accounts.google.com/o/oauth2/v2/auth"
_GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
_GOOGLE_USERINFO  = "https://www.googleapis.com/oauth2/v3/userinfo"

# Frontend URL to redirect to after OAuth completes.
# In production this is the same origin; locally it may differ.
_FRONTEND_URL = "/"


def _oauth_client():
    return OAuth2Session(
        client_id=config.GOOGLE_CLIENT_ID,
        client_secret=config.GOOGLE_CLIENT_SECRET,
        redirect_uri=config.GOOGLE_REDIRECT_URI,
        scope="openid email profile",
    )


@bp.route("/google")
def google_login():
    """Redirect the user to Google's OAuth consent screen."""
    if not config.GOOGLE_CLIENT_ID:
        return "Google OAuth is not configured.", 501

    client = _oauth_client()
    uri, _state = client.create_authorization_url(
        _GOOGLE_AUTH_URL,
        access_type="online",
    )
    return redirect(uri)


@bp.route("/google/callback")
def google_callback():
    """
    Google redirects here after the user consents.
    Exchange the code for tokens, fetch user info, upsert the user,
    issue our own JWT, and redirect to the frontend.
    """
    error = request.args.get("error")
    if error:
        return redirect(f"/#login?error={error}")

    code = request.args.get("code")
    if not code:
        return redirect("/#login?error=missing_code")

    # Exchange authorisation code for access token
    try:
        client = _oauth_client()
        token = client.fetch_token(
            _GOOGLE_TOKEN_URL,
            code=code,
            grant_type="authorization_code",
        )
    except Exception:
        return redirect("/#login?error=token_exchange_failed")

    # Fetch user profile from Google
    try:
        resp = requests.get(
            _GOOGLE_USERINFO,
            headers={"Authorization": f"Bearer {token['access_token']}"},
            timeout=10,
        )
        resp.raise_for_status()
        profile = resp.json()
    except Exception:
        return redirect("/#login?error=userinfo_failed")

    google_id = profile.get("sub")
    email     = profile.get("email", "").lower().strip()
    name      = profile.get("name") or profile.get("given_name") or email.split("@")[0]

    if not google_id or not email:
        return redirect("/#login?error=invalid_profile")

    db = get_db()
    try:
        # 1. Try to find an existing user by google_id
        row = db.execute(
            "SELECT id, email, name FROM users WHERE google_id = ?",
            (google_id,),
        ).fetchone()

        if row:
            user_id = row["id"]
        else:
            # 2. Try to find an existing email/password user and link the account
            row = db.execute(
                "SELECT id, email, name FROM users WHERE email = ?",
                (email,),
            ).fetchone()

            if row:
                # Link Google account to existing user
                user_id = row["id"]
                db.execute(
                    "UPDATE users SET google_id = ?, auth_provider = 'google', updated_at = NOW() WHERE id = ?",
                    (google_id, user_id),
                )
                db.commit()
            else:
                # 3. Brand-new user — create account (no password)
                user_id = str(uuid.uuid4())
                db.execute(
                    """INSERT INTO users (id, email, name, google_id, auth_provider)
                       VALUES (?, ?, ?, ?, 'google')""",
                    (user_id, email, name, google_id),
                )
                db.commit()
    finally:
        db.close()

    jwt_token = create_token(user_id, email)

    # Redirect to frontend — token is passed in the URL fragment so it never
    # hits the server logs. The frontend JS picks it up and stores it.
    return redirect(f"/#oauth?token={jwt_token}")
