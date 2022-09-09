# This file is a modification of https://github.com/tc-imba/python-jaccount-cli/blob/master/jaccount_cli/asyncio.py
from datetime import date, datetime, timedelta
from io import BytesIO
from types import TracebackType
from typing import Optional, Type, Dict, Any
from http.cookies import SimpleCookie
import json
import smtplib
from email.message import EmailMessage

from aiohttp import ClientSession
from bs4 import BeautifulSoup
import ddddocr
try:
    import Image as Image
except ImportError:
    import PIL
    from PIL import Image as Image

# make the jaccount server believe it is a browser
JACCOUNT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/91.0.4472.77 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9",
}
CAPTCHA_URL = "https://jaccount.sjtu.edu.cn/jaccount/captcha"
LOGIN_URL = "https://jaccount.sjtu.edu.cn/jaccount/ulogin"
FRONT_PAGE_URL = "https://elec.sjtu.edu.cn"
BILL_URL = "https://elec.sjtu.edu.cn/api/ws/sydl"
HISTORY_URL = "https://elec.sjtu.edu.cn/api/rechage/ydlmx"

class SJTUElecBillClient:
    def __init__(self):
        self.session: ClientSession = ClientSession(headers=JACCOUNT_HEADERS)
        self._session_autoclose = True
        self.cookies: Optional[SimpleCookie[str]] = None
        self.captcha_image: Optional[BytesIO] = None
        self.params: Dict[str, Any] = {}

    async def __aenter__(self) -> "SJTUElecBillClient":
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        if self._session_autoclose:
            await self.session.close()
        
    async def init(self):
        async with self.session.get(FRONT_PAGE_URL) as response:
            body = await response.text()
            self.cookies = response.cookies
        soup = BeautifulSoup(body, "html.parser")
        hidden_inputs = soup.select("input[type=hidden]")
        self.params = dict({(x["name"], x["value"]) for x in hidden_inputs})
        url = "%s?uuid=%s&t=%d" % (
            CAPTCHA_URL,
            self.params["uuid"],
            int(datetime.now().timestamp()),
        )
        async with self.session.get(url, cookies=self.cookies) as response:
            fp = BytesIO()
            fp.write(await response.read())
            self.captcha_image = fp

    async def login(self, username, password):
        ocr = ddddocr.DdddOcr()
        self.params["v"] = ""
        self.params["user"] = username
        self.params["pass"] = password
        self.params["captcha"] = ocr.classification(Image.open(self.captcha_image))
        async with self.session.post(
            LOGIN_URL, cookies=self.cookies, data=self.params
        ) as response:
            pass
    
    async def get_balance(self):
        async with self.session.get(BILL_URL, headers={"Accept": "application/json"}) as response:
            return json.loads(await response.text())["entities"][0]["SYL"]

    async def get_history(self, length: int):
        url = "%s?begin=%s&end=%s" % (
            HISTORY_URL,
            (date.today() - timedelta(days=length)).strftime("%Y-%m-%d"),
            (date.today() - timedelta(days=1)).strftime("%Y-%m-%d"),
        )
        async with self.session.get(url, headers={"Accept": "application/json"}) as response:
            return [data["used"] for data in json.loads(await response.text())["entities"]]

    def SMTP_login(self, host: str, port: int, addr: str, password: str):
        self.smtp_client = smtplib.SMTP(host, port)
        self.smtp_client.login(addr, password)

    def SMTP_quit(self):
        self.smtp_client.quit()

    def SMTP_send_msg(self, msg: EmailMessage):
        self.smtp_client.send_message(msg)

