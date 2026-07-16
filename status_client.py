import httpx


class StatusClient:

    BASE_URL = "https://assistapp-lx9a.onrender.com/api/automation/update"

    async def update(

        self,

        session_id,

        status,

        step,

        progress,

        waiting_otp=False,

        waiting_captcha=False,

        completed=False,

        result=""
    ):

        body = {

            "sessionId": session_id,

            "status": status,

            "currentStep": step,

            "progress": progress,

            "waitingForOtp": waiting_otp,

            "waitingForCaptcha": waiting_captcha,

            "completed": completed,

            "result": result

        }

        async with httpx.AsyncClient() as client:

            await client.post(

                self.BASE_URL,

                json=body

            )