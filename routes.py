from fastapi import APIRouter, HTTPException
import asyncio

from models import (
    StartAutomationRequest,
    SubmitOtpRequest,
    SubmitCaptchaRequest
)

from sessions import browser_agent

router = APIRouter(
    prefix="/automation",
    tags=["Automation"]
)


# -----------------------------
# Start Automation
# -----------------------------
@router.post("/start")
async def start_automation(request: StartAutomationRequest):
    
    print("Automation endpoint called")
    print(request)
    try:

        session_id = await browser_agent.create_session(
            session_id=request.sessionId,
            url=request.url,
            service_name=request.serviceName,
            prompt=request.prompt,
        )

        asyncio.create_task(
            browser_agent.start(session_id)
        )

        return {
            "success": True,
            "sessionId": session_id,
            "message": "Automation Started"
        }
    
        

    except Exception as ex:

        raise HTTPException(
            status_code=500,
            detail=str(ex)
        )


# -----------------------------
# Get Status
# -----------------------------
@router.get("/status/{session_id}")
async def get_status(session_id: str):

    return browser_agent.get_status(session_id)


# -----------------------------
# Submit OTP
# (Implementation will be added later)
# -----------------------------
@router.post("/otp")
async def submit_otp(request: SubmitOtpRequest):

    return await agent.submit_otp(
        request.sessionId,
        request.otp
    )


# -----------------------------
# Close Browser
# -----------------------------
@router.post("/close/{session_id}")
async def close_browser(session_id: str):

    await browser_agent.close(session_id)

    return {
        "success": True,
        "message": "Browser Closed"
    }

@router.post("/captcha")
async def captcha(request:SubmitCaptchaRequest):

    return await agent.submit_captcha(
        request.sessionId,
        request.captcha
    )