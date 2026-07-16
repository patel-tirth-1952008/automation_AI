import asyncio
import uuid
from typing import Dict, Any
from playwright.async_api import Page
import re
from Status_client import StatusClient

from browser_use import (
    Agent,
    Browser,
    BrowserProfile,
    ChatOllama,
)


class BrowserAgent:

    def __init__(self):

        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.waiting_sessions = {}
        
        self.llm = ChatOllama(
            model="qwen2.5:3b",
            host="http://localhost:11434"
        )
        self.status_client = StatusClient()

        self.browser_profile = BrowserProfile(

            headless=False,

            keep_alive=True,

            wait_between_actions=0.5,

            minimum_wait_page_load_time=1,

            wait_for_network_idle_page_load_time=2,

            highlight_elements=True,

            viewport={
                "width": 1400,
                "height": 900
            }
        )
    async def create_browser(self):

            browser = Browser(

                browser_profile=self.browser_profile

        )

            return browser
        
    async def create_session(

            self,
            session_id,

            url: str,

            service_name: str,
            prompt
        ):

            session_id = str(uuid.uuid4())
            

            browser = await self.create_browser()

            self.sessions[session_id] = {

                "status": "Starting",
                "browser" : browser,
                "agent" : None,
                "prompt" : prompt,

"url": url,

"service": service_name,

"otp_required": False,
"captcha_required" : False,
"completed": False,

"current_step": 0,

"last_action": "",

"progress": 0,

"result": "",

"error": ""

            }

            return session_id
        
    def build_prompt(

        self,

        url: str,

        service_name: str

    ) -> str:

            return f"""
You are filling an Indian Government service.

Service:
{service_name}

Website:
{url}

Instructions:

Open the website.

Navigate intelligently.

Fill every possible field.

Do NOT submit final application.

If OTP appears,

STOP.

If CAPTCHA appears,

STOP.

Wait for further instruction.

Never close browser.

Keep browser alive.
"""
    
    async def update_progress(

        self,

        session_id: str,

        step: int,

        action: str

    ):

        session = self.sessions[session_id]

        session["current_step"] = step

        session["last_action"] = action

        progress = min(step * 5, 95)

        session["progress"] = progress

        session["status"] = action

        await self.status_client.update(

        session_id=session_id,

        status="Running",

        step=action,

        progress=progress,

        waiting_otp=False,

        waiting_captcha=False,

        completed=False,

        result=""

        )

    async def finish_session(
        self,
        session_id: str,
        result: str,
    ):

        session = self.sessions[session_id]

        session["completed"] = True

        session["progress"] = 100

        session["status"] = "Completed"

        session["result"] = result
        await self.status_client.update(
    session_id=session_id,
    status="Completed",
    step="Automation Finished",
    progress=100,
    waiting_otp=False,
    waiting_captcha=False,
    completed=True,
    result=result
)

        session["last_action"] = "Automation Finished"    
    async def fail_session(
        self,
        session_id: str,
        error: str,
    ):

        session = self.sessions[session_id]

        session["completed"] = True

        session["status"] = "Failed"

        session["error"] = error

        session["last_action"] = error
        await self.status_client.update(
    session_id=session_id,
    status="Failed",
    step="Error",
    progress=session["progress"],
    waiting_otp=False,
    waiting_captcha=False,
    completed=True,
    result=error
)

    async def detect_otp_page(
        self,
        session_id: str,
    ):

        browser = self.sessions[session_id]["browser"]

        page = await browser.get_current_page()

        html = await page.content()

        html = html.lower()

        keywords = [

            "otp",
            "one time password",
            "verification code",
            "enter otp",
            "mobile otp",
            "verify otp"

        ]

        for keyword in keywords:

            if keyword in html:

                return True

        return False
    
        
    async def detect_captcha_page(
        self,
        session_id: str,
    ):

        browser = self.sessions[session_id]["browser"]

        page = await browser.get_current_page()

        html = await page.content()

        html = html.lower()

        keywords = [

            "captcha",
            "i'm not a robot",
            "recaptcha"

        ]

        for keyword in keywords:

            if keyword in html:

                return True

        return False
    
    
    async def wait_for_user(
        self,
        session_id: str,
        reason: str,
    ):

        session = self.sessions[session_id]

        session["status"] = reason

        if reason == "WaitingForOTP":

            session["otp_required"] = True

        elif reason == "WaitingForCaptcha":

            session["captcha_required"] = True

        self.waiting_sessions[session_id] = True

        while self.waiting_sessions.get(session_id):

            await asyncio.sleep(1)

    async def submit_otp(
        self,
        session_id: str,
        otp: str,
    ):

        if session_id not in self.sessions:

            return {

                "success": False,

                "message": "Invalid Session"

            }

        browser = self.sessions[session_id]["browser"]

        page = await browser.get_current_page()

        otp_selectors = [

            "input[type='tel']",

            "input[type='number']",

            "input[name*='otp']",

            "input[id*='otp']",

            "input[placeholder*='OTP']",

            "input[placeholder*='otp']",

            "input[maxlength='6']",

            "input[maxlength='4']"

        ]

        textbox = None

        for selector in otp_selectors:

            try:

                textbox = page.locator(selector).first

                if await textbox.count() > 0:

                    break

            except:

                pass

        if textbox is None:

            return {

                "success": False,

                "message": "OTP textbox not found"

            }

        await textbox.fill(otp)      
        buttons = [

            "button",

            "input[type='submit']",

            "input[type='button']",

            "[role='button']"

        ]

        clicked = False

        for selector in buttons:

            try:

                elements = page.locator(selector)

                count = await elements.count()

                for i in range(count):

                    btn = elements.nth(i)

                    text = (

                        await btn.inner_text()

                    ).lower()

                    if (

                        "verify" in text or

                        "submit" in text or

                        "continue" in text or

                        "next" in text

                    ):

                        await btn.click()

                        clicked = True

                        break

                if clicked:

                    break

            except:

                pass  

        self.waiting_sessions[session_id] = False

        self.sessions[session_id]["otp_required"] = False

        self.sessions[session_id]["status"] = "Resuming"

        try:

            await self.sessions[
                session_id
            ]["agent"].resume()

        except:

            pass

        return {

            "success": True,

            "message": "OTP Submitted"

        }
    async def submit_captcha(

        self,

        session_id: str

    ):

        if session_id not in self.sessions:

            return

        self.waiting_sessions[session_id] = False

        self.sessions[session_id][
            "otp_required"
        ] = False

        self.sessions[session_id][
            "status"
        ] = "Resuming"

        try:

            await self.sessions[
                session_id
            ]["agent"].resume()

        except:

            pass

        return {

            "success": True

        }
    async def start(

        self,

        session_id: str

        ):
        

            session = self.sessions[session_id]

            prompt = session["prompt"]
            
            

            session["status"] = "Opening Browser"

            agent = Agent(

                    task=prompt,

                    llm=self.llm,

                    browser=session["browser"],

                    use_vision=True,

                    max_actions_per_step=3,

                    max_failures=5,

                    enable_planning=True,

                    use_thinking=True,

                    generate_gif=False

                )

            session["agent"] = agent

            session["status"] = "Running"

            

            step = 0

            try : 
                while True:

                    step += 1

                    await self.update_progress(

                        session_id,

                        step,

                        f"Executing Step {step}"

                    )

                    result = await agent.step()
                    if result is not None:

                        try:

                            if hasattr(result, "is_done"):

                                if result.is_done:

                                    break

                        except:

                            pass
                       
                    otp = await self.detect_otp_page(session_id)

                    if otp:

                        await agent.pause()
                        await self.status_client.update(
                            session_id=session_id,
                            status="WaitingForOTP",
                            step="Waiting for OTP",
                            progress=session["progress"],
                            waiting_otp=True,
                            waiting_captcha=False,
                            completed=False,
                            result=""
                        )

                        await self.wait_for_user(
            session_id,
            "WaitingForOTP"
        )

                        await agent.resume()

                        continue
                    if step > 300:

                        raise Exception(
                            "Maximum automation steps reached."
                    )
                    captcha = await self.detect_captcha_page(session_id)

                    if captcha:

                        await agent.pause()
                        await self.status_client.update(
                            session_id=session_id,
                            status="WaitingForCaptcha",
                            step="Waiting for Captcha",
                            progress=session["progress"],
                            waiting_otp=False,
                            waiting_captcha=True,
                            completed=False,
                            result=""
                        )

                        await self.wait_for_user(
            session_id,
            "WaitingForCaptcha"
        )

                        await agent.resume()

                        continue
                    
                await self.finish_session(
    session_id,
    "Automation completed successfully."
)

            
                session["completed"] = True

                session["progress"] = 100

                session["status"] = "Completed"

                session["result"] = "Automation Finished"

            except Exception as ex:

                await self.fail_session(
                session_id,
                str(ex)
    )

                raise
    async def save_browser_state(
        self,
        session_id: str,
    ):

        browser = self.sessions[session_id]["browser"]

        try:

            await browser.export_storage_state(
                f"sessions/{session_id}.json"
            )

        except:

            pass
    async def close_session(
        self,
        session_id: str,
    ):

        if session_id not in self.sessions:

            return

        browser = self.sessions[
            session_id
        ]["browser"]

        try:

            await browser.close()

        except:

            pass

    def get_status(

        self,

        session_id: str

    ):

        if session_id not in self.sessions:

            return {

                "success": False,

                "message": "Invalid Session"

            }

        s = self.sessions[session_id]

        return {

            "success": True,

            "status": s["status"],

            "completed": s["completed"],

            "progress": s["progress"],

            "currentStep": s["current_step"],

            "lastAction": s["last_action"],

            "otpRequired": s["otp_required"],

            "url": s["url"],

            "service": s["service"],

            "result": s["result"],

            "error": s["error"]

        }
    def get_browser(

        self,

        session_id: str

    ):

        if session_id not in self.sessions:

            return None

      
        return self.sessions[session_id]["browser"] 
    def get_agent(

        self,

        session_id: str

    ):

        if session_id not in self.sessions:

            return None

        return self.sessions[session_id]["agent"]
    
    async def close(

        self,

        session_id: str

    ):

        if session_id not in self.sessions:

            return

        browser = self.sessions[session_id]["browser"]

        try:

            await browser.close()

        except:

            pass

        del self.sessions[session_id]

      
    
