import sys
import time
from datetime import timedelta

from conf import ChatId, drives, logger, FAILED, DONE
from encode.wsgi import *
from utils import (choose_opt, choose_workdir, extract_sub, has_subtitles,
                   list_folder, notify_me, show_subs, spedup_subs)
from utils.orm import create_ticket, get_ticket, update_status
from utils.process_ticket import ItemsProcedure

audio_path = subtitle = ''
audio = 0
sublist = []
args = sys.argv
if len(args) > 1:
    ticket = get_ticket(args[1])
    WORKDIR = ticket.working_directory
    serial = ticket.serial
    subtitles = ticket.subtitles
    recursive = ticket.recursive
    external_audio = ticket.external_audio
    speed = ticket.speed
else:
    drive = drives[choose_opt("drive")]
    AYRISH_DIR = os.path.abspath(drive)
    folders = list_folder(AYRISH_DIR)
    WORKDIR = choose_workdir(AYRISH_DIR, folders)
    recursive = choose_opt('recursive')
    serial = choose_opt('serial') if not recursive else 0
    subtitles = choose_opt('subtitle') if not recursive else 0
    speed = choose_opt('speed')
    external_audio = choose_workdir(WORKDIR, list_folder(WORKDIR)) if choose_opt("external") else ''
    ticket = create_ticket(hash(time.time()), ChatId.admin)
    ticket.speed = speed
    ticket.working_directory = WORKDIR
    ticket.recursive = recursive
    ticket.serial = serial
    ticket.external_audio = external_audio
    ticket.subtitles = subtitles
    ticket.save()
CHAT_ID = ticket.user_id
message_id = notify_me(
    chat_id=CHAT_ID,
    message=f'Тикет номер {ticket.ticket_id} в процессе.',
)
processed_ticket = ItemsProcedure(ticket)
film_list = processed_ticket.items_to_render
count = len(film_list)
if subtitles:
    notify_me(
        chat_id=CHAT_ID,
        message='Сейчас я мееедленно буду вытаскивать все субтитры',
        message_id=message_id,
    )
    for item_num, item in enumerate(film_list, 1):
        if has_sub := has_subtitles(item):
            sub = show_subs(item)
            sublist.append(extract_sub(item, sub))
        notify_me(chat_id=CHAT_ID,
                  message=f'{item_num}/{count}'
                          f'{item} {"extracted." if has_sub else "has no subtitles."}',
                  message_id=message_id)
    for index, item_path in enumerate(sublist):
        notify_me(chat_id=CHAT_ID,
                  message=f'{index}/{len(sublist)}'
                          f'{item_path} speeding up',
                  message_id=message_id)
        working_on = os.path.join(WORKDIR, "curr.srt")
        os.rename(item_path, working_on)
        spedup_subs(working_on, item_path, speed)

commands = processed_ticket.commands
try:
    notify_me(
        chat_id=CHAT_ID,
        message=f'В процессе:\n{commands[0]["filename"]}',
        message_id=message_id,
    )
except IndexError:
    notify_me(chat_id=CHAT_ID, message='В этой папке нет видео')
    update_status(ticket, FAILED)
else:
    start_time = time.time()
    for i, command in enumerate(commands, 1):
        logger.info(command['command'])
        os.system(command=command['command'])
        elapsed = time.time() - start_time
        notify_me(chat_id=CHAT_ID,
                  message=f"{i}/{count}: \n{command['filename']}\n"
                          f"Elapsed Time: {timedelta(seconds=elapsed)}\n"
                          f"Average {timedelta(seconds=(elapsed / i))}",
                  message_id=message_id)
    if processed_ticket.errors():
        update_status(ticket, FAILED)
        notify_me(chat_id=CHAT_ID, message=f"{ticket.ticket_id}: Во время работы возникли ошибки.")
    notify_me(chat_id=CHAT_ID, message="Все готово!", no_sound=False)
    update_status(ticket, DONE)
