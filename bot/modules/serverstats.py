import os
import time
import shutil
import psutil, cpuinfo, platform
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

from pyrogram.types import InputMediaPhoto

from ..helper.ext_utils.bot_utils import new_task
from ..helper.ext_utils.status_utils import get_readable_bytes, get_readable_time
from .. import bot_start_time


@new_task
async def server_stats(_, message):

    image = Image.open("TelegramBot/helpers/assets/statsbg.png").convert("RGB")
    IronFont = ImageFont.truetype("TelegramBot/helpers/assets/IronFont.otf", 42)
    draw = ImageDraw.Draw(image)

    # 120, coordinate, progress, coordinate - 25
    def draw_progressbar(coordinate, progress):
        progress = 110 + (progress * 10.8)
        draw.ellipse((105, coordinate - 25, 127, coordinate), fill="#DDFD35")
        progress = 121 if progress < 121 else progress
        draw.rectangle([(120, coordinate -25), (progress, coordinate)], fill="#DDFD35")
        draw.ellipse((progress - 7, coordinate - 25, progress + 15, coordinate), fill="#DDFD35")

    total, used, free = shutil.disk_usage(".")
    process = psutil.Process(os.getpid())

    botuptime = get_readable_time(time.time() - bot_start_time)
    osuptime = get_readable_time(time.time() - psutil.boot_time())
    botusage = f"{round(process.memory_info()[0]/1024 ** 2)} MiB"

    upload = get_readable_bytes(psutil.net_io_counters().bytes_sent)
    download = get_readable_bytes(psutil.net_io_counters().bytes_recv)

    ram_percentage = psutil.virtual_memory().percent
    ram_total = get_readable_bytes(psutil.virtual_memory().total)
    ram_used = get_readable_bytes(psutil.virtual_memory().used)

    swap = psutil.swap_memory()
    swap_used = get_readable_bytes(swap.used)
    swap_total = get_readable_bytes(swap.total)
    swap_percent = swap.percent

    disk_percenatge = psutil.disk_usage("/").percent
    disk_total = get_readable_bytes(total)
    disk_used = get_readable_bytes(used)
    disk_free = get_readable_bytes(free)
    dio = psutil.disk_io_counters()

    cpu = cpuinfo.get_cpu_info().get("brand_raw", platform.processor())
    cpu_percentage = psutil.cpu_percent()
    cpu_freq = psutil.cpu_freq().current
    cpu_freq_str = f"{round(cpu_freq / 1000, 2)}GHz" if cpu_freq >= 1000 else f"{round(cpu_freq, 2)}MHz"
    cpu_load = psutil.cpu_percent(interval=1)
    cpu_count = psutil.cpu_count()

    arch = platform.machine()
    os_name = platform.system()
    os_version = platform.version()

    load_avg = 'Unknown'
    if hasattr(os, "getloadavg"):
        load1, load5, load15 = os.getloadavg()
        load_avg = f"{load1:.2f}, {load5:.2f}, {load15:.2f}"

    temps = psutil.sensors_temperatures()
    avg_temp = 'Unknown'
    if temps and "coretemp" in temps:
        core_temps = temps["coretemp"]
        avg_temp = sum(t.current for t in core_temps) / len(core_temps)
        avg_temp = f"{avg_temp:.1f}°C"

    caption = f"""
**Hostname:** {platform.node()}
**Kernel:** {platform.release()}

**CPU:** {cpu}
**CPU SPEC:** {cpu_count} cores @ {cpu_freq_str}, {cpu_load}%
**Bot Usage:** {botusage}
**Load Avg:** {load_avg}
**CPU Temp:** {avg_temp}

**Swap:** {swap_used} / {swap_total} ({swap_percent}%)

**Arch:** {arch}
**OS:** {os_name} {os_version}
**OS Uptime:** {osuptime}

**Total Space:** {disk_total}
**Free Space:** {disk_free}
**Disk I/O:** R {get_readable_bytes(dio.read_bytes)} | W {get_readable_bytes(dio.write_bytes)}

**Download:** {download}
**Upload:** {upload}
"""

    for iface, stats in psutil.net_if_stats().items():
        if stats.isup:
            caption += f"\n**Net:** {iface} is UP - {stats.speed} Mbps"

    start = datetime.now()
    msg = await message.reply_photo(
        photo="https://te.legra.ph/file/30a82c22854971d0232c7.jpg",
        caption=caption,
        quote=True)
    end = datetime.now()

    draw_progressbar(243, int(cpu_percentage))
    draw.text(
        (225, 153),
        f"( {cpu_count} core, {cpu_percentage}% )",
        (255, 255, 255),
        font=IronFont,
    )

    draw_progressbar(395, int(disk_percenatge))
    draw.text(
        (335, 302),
        f"( {disk_used} / {disk_total}, {disk_percenatge}% )",
        (255, 255, 255),
        font=IronFont,
    )

    draw_progressbar(533, int(ram_percentage))
    draw.text(
        (225, 445),
        f"( {ram_used} / {ram_total} , {ram_percentage}% )",
        (255, 255, 255),
        font=IronFont,
    )

    draw.text((290, 590), botuptime, (255, 255, 255), font=IronFont)
    draw.text(
        (910, 590),
        f"{(end-start).microseconds/1000} ms",
        (255, 255, 255),
        font=IronFont,
    )

    image.save("stats.png")
    await msg.edit_media(media=InputMediaPhoto("stats.png", caption=caption))
    os.remove("stats.png")
