import random
from fastapi import FastAPI, BackgroundTasks, APIRouter

from ..helpers.email import send_smtp_email

from ..models.models import MagicLinkRequest
from ..auth import auth

login_attempts = {}
otp_store = {}

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/magic-link")
def trigger_otp(request: MagicLinkRequest, background_tasks: BackgroundTasks):
    otp = f"{random.randint(100000, 999999)}"

    # Store it (In a real app, use Redis or a DB with expiry)
    otp_store[request.email] = otp
    login_attempts[request.email] = {"status": "pending", "token": None}

    background_tasks.add_task(send_smtp_email, request.email, otp)
    return {"message": "OTP Sent"}


@router.get("/poll")
def poll_status(email: str):
    attempt = login_attempts.get(email)
    print(attempt)
    if not attempt:
        return {"status": "not_found"}
    return attempt


@router.post("/verify-otp")
def verify_otp(request: dict):
    email = request.get("email")
    otp = request.get("otp")

    if otp_store.get(email) == otp:
        # Generate your actual API token here
        token = "some-generated-session-token"
        login_attempts[email] = {"status": "completed", "token": token}
        return {"message": "Verified"}

    return {"message": "Invalid OTP"}, 401
