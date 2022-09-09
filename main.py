from os import environ as env
from dotenv import load_dotenv
import datetime
from email.message import EmailMessage
import asyncio
from client import SJTUElecBillClient

async def main():
    load_dotenv()
    async with SJTUElecBillClient() as client:
        time_delta = abs(
            (
                datetime.datetime.now() - datetime.datetime.combine(
                    datetime.date.today(), datetime.time(int(env["REPORT_TIME"]), 0)
                )
            ) / datetime.timedelta(minutes=1)
        )
        await client.init()
        await client.login(env["JACCOUNT_NAME"], env["JACCOUNT_PASS"])
        balance = await client.get_balance()
        history = await client.get_history(int(env["HISTORY_RANGE"]))
        email_msg = EmailMessage()
        email_msg['Subject'] = "宿舍电费情况通知"
        email_msg['From'] = env["SENDER_ADDR"]
        email_msg['To'] = env["RECEIVER_ADDR"]
        email_msg.set_charset("utf-8")
        client.SMTP_login(env["SMTP_HOST"], int(env["SMTP_PORT"]), env["SENDER_ADDR"], env["SENDER_PASS"])
        if float(balance) < 5:
            email_msg.set_content("当前电费剩余{}度，已不足5度，请立即充值！".format(str(balance)))
        elif float(balance) < 10:
            email_msg.set_content("当前电费剩余{}度，已不足10度，请尽快充值！".format(str(balance)))
        elif time_delta < 30:
            email_msg.set_content("每日电费：当前电费剩余{}度，根据过去{}天用量，预计还可以使用{}天。".format(str(balance), env["HISTORY_RANGE"], str(round(balance / sum(history) * len(history), 1))))
        client.SMTP_send_msg(email_msg)
        client.SMTP_quit()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
