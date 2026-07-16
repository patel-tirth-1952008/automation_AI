from pydantic import BaseModel


class StartAutomationRequest(BaseModel):

    sessionId:str

    serviceName:str

    url:str

    prompt:str


class SubmitOtpRequest(BaseModel):

    sessionId:str

    otp:str


class SubmitCaptchaRequest(BaseModel):

    sessionId:str

    captcha:str