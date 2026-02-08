import random
from fastapi import BackgroundTasks, APIRouter

from ..helpers.email import send_smtp_email

from ..models.models import MagicLinkRequest, VerifyOtpRequest
from ..auth import auth

login_attempts = {}
otp_store = {}

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/magic-link")
def trigger_otp(request: MagicLinkRequest, background_tasks: BackgroundTasks):
    otp = f"{random.randint(100000, 999999)}"

    otp_store[request.email] = otp
    login_attempts[request.email] = {"status": "pending", "token": None}

    background_tasks.add_task(send_smtp_email, request.email, otp)
    return {"message": "OTP Sent"}


@router.get("/poll")
def poll_status(email: str):
    attempt = login_attempts.get(email)
    print("getting the access token after successful otp", attempt)
    if not attempt:
        return {"status": "not_found"}
    return attempt


@router.post("/verify-otp")
def verify_otp(request: VerifyOtpRequest):
    email = request.email
    otp = request.otp

    if otp_store.get(email) == otp:
        cli_user = auth.fetch_user_metadata_by_email(
            email=request.email,
            include_orgs=True,
        )

        if cli_user is None:
            return {"message": "User not found in PropelAuth"}, 404

        token = auth.create_access_token(cli_user.user_id, 999).access_token
        login_attempts[email] = {
            "status": "completed",
            "token": token,
            "id": cli_user.user_id,
        }
        return {"message": "Verified"}

    return {"message": "Invalid OTP"}, 401
