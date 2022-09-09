# SJTU-elec-bill-mailer
Get the electricity bill of the dormitory bound to your Jaccount from the new API and send an email to you via SMTP accordingly.

从新API获取绑定在Jaccount的宿舍的电费信息，并通过SMTP服务器发送邮件通知。

## Requirements
You may need to install packages like aiohttp, bs4, Image, ddddocr, and so on. Here's an example:
```shell
$ pip3 install aiohttp, bs4, Image, ddddocr
```

## Usage
### Create Environment File
To run the script, you need to provide a `.env` file inside this directory. It should contain the following entries:

```Python
JACCOUNT_NAME=
JACCOUNT_PASS=
SMTP_HOST=
SMTP_PORT=
SENDER_ADDR=
SENDER_PASS=
RECEIVER_ADDR=
REPORT_TIME=
HISTORY_RANGE=
```

* `JACCOUNT_NAME` and `JACCOUNT_PASS` should be the username and password of your Jaccount.
* `SMTP_HOST` and `SMTP_PORT` (an integer) are the host address and port of your SMTP server, by which you will send an email to notify yourself.
* `SENDER_ADDR` and `SENDER_PASS` are the email address and password needed to log in to your SMTP server. The email will be sent from `SENDER_ADDR`.
* `RECEIVER_ADDR` is the email address you wish to receive the notification email.
* `REPORT_TIME` (an integer) is a 24-hour clock value. If your balance (in kW $\cdot$ H) is greater than 10, the script will not send you an email, unless it is executed half an hour near `REPORT_TIME`.
* `HISTORY_RANGE` (an integer) is the history range the script will access. The script will predict the time (in days) before your balance is used up. It will calculate your average daily usage based on the last `HISTORY_RANGE` days' data.

Then, you can directly run `python3 main.py` to have a try.

### Set the Script as An CRON Job
You can make the script a cron job and execute it regularly. For example, if you want to run it every two hours, you can use
```shell
$ crontab -e
```
and insert an entry
```shell
0 */2 * * * python3 <absolute path to the script>
```
to the crontab.

For further usage of cron, try Google.

## Disclaimer
The part of script logging in Jaccount is based on [tc-imba/python-jaccount-cli](https://github.com/tc-imba/python-jaccount-cli). Basically, `client.py` is a modification of [tc-imba/python-jaccount-cli/jaccount_cli/asyncio.py](https://github.com/tc-imba/python-jaccount-cli/blob/master/jaccount_cli/asyncio.py)

**I am not responsible for any consequences of using this script.**

**本人不对使用此脚本产生的任何后果负责。**
