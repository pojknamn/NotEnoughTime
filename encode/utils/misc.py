import os
import pathlib

import ffmpeg._run
import srt
from conf import (BASE_FOLDER_LEN, CLOSE_N_CHOOSE, DEFAULT_DRIVE_AYRISH,
                  DEFAULT_DRIVES, DEFAULT_OPTIONS, ENCODE_KEYS, SPLITTER, SUB_N_SPEED,
                  ENCODED_FOLDER)
from conf import bot_instance as bot
from conf import logger
from ffmpeg import probe
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from utils.orm import folder_from_response, save_to_db


def has_subtitles(item_path: str) -> bool:
    try:
        subtitles = get_russian_streams(probe(item_path)["streams"], "subtitle")
    except ffmpeg._run.Error:
        return False
    return True if subtitles else False


def get_russian_streams(stream_list: list, codec_type: str) -> list:
    streams_list = [
        stream for stream in stream_list if stream.get("codec_type") == codec_type
    ]
    russian_streams = []
    for n, item in enumerate(streams_list):
        if item.get("tags", {}).get("language") == "rus":
            russian_streams.append([n, item])
            logger.debug(f'{n}, {item["tags"]}')
    if not russian_streams and streams_list:
        russian_streams.append([0, streams_list[0]])
    return russian_streams


def choose_workdir(basedir: str, folders: list) -> str:
    choose = int(input("Choose num folder (0 for current folder): \n")) - 1
    if choose == -1:
        working_directory = basedir
        return working_directory
    else:
        working_directory = os.path.join(basedir, folders[choose])
        folders = list_folder(working_directory)
        return choose_workdir(working_directory, folders)


def list_folder(folder: str) -> list:
    folders = [i for i in os.listdir(folder) if os.path.isdir(os.path.join(folder, i))]
    for folder_n, folder in enumerate(folders):
        logger.info(f"{folder_n + 1}, {folder}")
    return folders


def show_subs(item_path: str) -> int:
    logger.debug(item_path.split("/")[-1])
    cnt = get_russian_streams(probe(item_path)["streams"], "subtitle")
    if len(cnt) > 1:
        winner = [0, 0]
        for item in cnt:
            if (cur := int(item[1].get("tags", {}).get("NUMBER_OF_BYTES", 0))) > winner[1]:
                winner = [item[0], cur]
        logger.info(f"Я выбрал эти сабы {cnt[winner[0]][1].get('tags')['title']}")
        return winner[0]
    else:
        return cnt[0][0]


def check_audio(item_path: str) -> int:
    logger.debug(item_path.split("/")[-1])
    russian_audio = get_russian_streams(probe(item_path)["streams"], "audio")
    return russian_audio[0][0]


def spedup_subs(subtitle_path: str, speeded_path: str, speed: float) -> None:
    with open(subtitle_path, "r", encoding="utf-8") as sb:
        subs = srt.parse(srt=sb)
        new_subs = []
        for sub in subs:
            sub.start = sub.start / speed
            sub.end = sub.end / speed
            new_subs.append(sub)
    logger.info(f"Sub done: {subtitle_path}")
    os.remove(subtitle_path)
    with open(speeded_path, "w", encoding="utf-8") as new:
        new.writelines(srt.compose(new_subs))


def check_filetype(workdir: str) -> str:
    origin, folders, items = os.walk(os.path.abspath(workdir)).__next__()
    logger.debug(f"{origin = }\n{folders = }\n{items= }")
    for item in items:
        if filetype := check_type(path=item, ret_ext=True):
            return filetype[0]
    else:
        for folder in folders:
            if filetype := check_filetype(os.path.join(workdir, folder)):
                return filetype


def create_subfolders(start_dir: str = '', recursive: bool = False,
                      ticket_id: int = 0) -> None:  # TODO: rename + split
    temp_data = []
    for origin, folders, items in os.walk(start_dir):

        if ENCODED_FOLDER in origin:
            continue

        if items := [os.path.join(origin, item) for item in items if check_type(item)]:
            if ENCODED_FOLDER not in folders:
                new_folder = os.path.join(origin, ENCODED_FOLDER)
                os.mkdir(new_folder)
                logger.debug(f'Path created {new_folder}')
            temp_data += items

        if not recursive:
            break

    save_to_db(ticket_id, key="items", data=temp_data)


def extract_sub(file: str, subs: int) -> str:
    sub_name = f"{file.rpartition('.')[0]}_subs.srt"
    command = (
        f"ffmpeg -y -loglevel "
        f'warning -stats -threads 6 -i "{file}" -map 0:s:{subs} "{sub_name}"'
    )
    os.system(command)
    return sub_name


def notify_me(
        chat_id: int, message: str, no_sound: bool = True, message_id: int = None
) -> int:
    try:
        if message_id:
            bot.edit_message_text(
                chat_id=chat_id, text=f"{message}", message_id=message_id
            )
        else:
            message = bot.send_message(
                chat_id=chat_id, text=f"{message}", disable_notification=no_sound
            )
            message_id = message.id
        return message_id
    except Exception:  # noqa
        logger.log("DEBUG", "I can`t do this for now.")


def check_type(path: str, ret_ext=False) -> bool | list:
    """
    Chek if file is kind of media type. Returns True or False if ret_ext not specified.
    Else returns list: [extension, resulting extension]
    """
    media_list = {
        ".mp4": "mkv",
        ".mkv": "mp4",
        ".avi": ".mkv",
        ".m4v": "m4v",
        ".flv": "mkv",
        ".mov": "mkv",
        '.ts': 'mkv',
    }
    extention = pathlib.Path(path).suffix
    if extention in media_list.keys():
        if ret_ext:
            return [extention, media_list[extention]]
        return True
    return False


def choose_opt(opt_name: str) -> int | float:
    options = DEFAULT_OPTIONS
    answer = input(options[opt_name].get("text"))
    default_value = options[opt_name].get("default")
    match answer:
        case "":
            answer = default_value
        case str() if '.' in answer:
            answer = float(answer)
        case str() if answer.isdigit():
            answer = int(answer)
        case _:
            logger.warning("Вы указали неверный параметр, попробуйте ещё раз!")
            return choose_opt(opt_name)
    return answer


def add_buttons(kb: InlineKeyboardMarkup, defaults: dict, ticket_id: int | str) -> None:
    for key, val in defaults.items():
        option_type = 'workdir'
        if isinstance(val, dict):
            display_name = val.get("display_name")
            option_type = val.get('option_type')
        else:
            display_name = val
        if key == "last_opt":
            continue
        key = encode_response(
            {
                'option_type': option_type,
                'option_value': key,
                'ticket_id': ticket_id
            }
        )
        kb.add(InlineKeyboardButton(text=display_name, callback_data=key))


def gen_folders_json(current_folder: str | dict, restrict_dir: bool = False) -> dict:
    if isinstance(current_folder, dict):
        current_folder = current_folder.get("path")
    folders_json = {"last_opt": current_folder}
    for ind, item in enumerate(list_folder(current_folder), 1):
        path = os.path.join(current_folder, item)
        key = f"p{ind}"
        folders_json[key] = {"path": path, "display_name": item}
    if len(splited := current_folder.split(SPLITTER)) >= BASE_FOLDER_LEN:
        if not restrict_dir:
            back = DEFAULT_DRIVE_AYRISH.get("base_g").get("path")
        else:
            back = SPLITTER.join(splited[:-1])
        folders_json["back"] = {"path": back, "display_name": "Назад"}
    return folders_json


def gen_keyboard(response=None, restrict_dir: bool = False) -> InlineKeyboardMarkup:
    response = decode_response(response)
    ticket = response['ticket_id']
    option = response['option_value']
    kb = InlineKeyboardMarkup()
    add_buttons(kb, CLOSE_N_CHOOSE, ticket_id=ticket)
    drives = DEFAULT_DRIVE_AYRISH if restrict_dir else DEFAULT_DRIVES
    if option == 'None':
        add_buttons(kb, drives, ticket_id=ticket)
        return kb
    if "base" in option:
        cur_dir = drives.get(option).get("path")
    else:
        cur_dir = folder_from_response(ticket, option)
    folders_json = gen_folders_json(cur_dir, restrict_dir)
    save_to_db(ticket, folders_json, "json")
    add_buttons(kb, folders_json, ticket_id=ticket)
    return kb


def gen_options_kb(response: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    response = decode_response(response)
    response_query = response.get('option_type')
    ticket_id = response.get('ticket_id')
    options = SUB_N_SPEED
    for option in options[response_query]:
        message = {
            'option_type': response_query,
            'option_value': option,
            'ticket_id': ticket_id,
        }
        button = InlineKeyboardButton(
            text=f"{option}",
            callback_data=encode_response(message)
        )
        kb.add(button)
    return kb


def encode_response(message: dict):
    response = "{ticket_id}🐣{option_type}🐣{option_value}".format(**message)
    return response


def decode_response(encoded_message: str):
    response = encoded_message.split('🐣')
    return dict(zip(ENCODE_KEYS, response))

