from speedtest import Speedtest
import asyncio

from ..helper.ext_utils.bot_utils import new_task
from .. import LOGGER
from ..helper.ext_utils.status_utils import get_readable_file_size
from ..helper.telegram_helper.message_utils import send_message, delete_message, send_photo


def speedtestcli():
    test = Speedtest(secure=True)
    test.get_best_server()
    test.download()
    test.upload()
    test.results.share()
    return test.results.dict()


@new_task
async def speedtest_cmd(_, message):
    """Give speedtest of the server where bot is running."""

    speed = await send_message(message, text="Running speedtest....")
    LOGGER.info("Running speedtest....")
    result = await asyncio.to_thread(speedtestcli)

    speed_string = f"""
Upload: {get_readable_file_size(result["upload"] / 8)}/s
Download: {get_readable_file_size(result["download"] / 8)}/s
Ping: {result["ping"]} ms
ISP: {result["client"]["isp"]} {result["client"]["isprating"]} 
IP: {result["client"]["ip"]} {result["client"]["country"]}
Rating: {result["client"]["rating"]}

Server: {result["server"]["host"]}
Name: {result["server"]["sponsor"]}
Country: {result["server"]["name"]} {result["server"]["country"]}
"""
    await delete_message(speed)
    return await send_photo(message, photo=result["share"], caption=speed_string)
