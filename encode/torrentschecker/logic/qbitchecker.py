import hashlib
import os
from datetime import datetime as dt

import qbittorrentapi

from conf import logger, ChatId, QBITCREDS
from utils import check_type, check_filetype, notify_me
from ..models import PendingModel

try:
    client = qbittorrentapi.Client(**QBITCREDS
    )
    client.auth_log_in(timeout=10)
except Exception as e:
    logger.warning(f"failed login {e}")


def check_time_past(item):
    if (completion_time := item.completion_on) < 0:
        return False
    diff_time = dt.now() - dt.fromtimestamp(completion_time)
    if diff_time.days < 1 and diff_time.seconds < 3600 * 24:
        return True
    else:
        return False


def make_hash(fullpath: str) -> str:
    return hashlib.md5(fullpath.encode("utf-8")).hexdigest()


def is_pending(fullpath: str) -> bool:
    hashed = make_hash(fullpath)
    pending_item = PendingModel.objects.filter(ident=hashed)
    if pending_item:
        return True
    return False


def recently_downloaded(client_obj=None, /) -> list:
    pended = [
        item
        for item in client_obj.torrents_info()
        if check_time_past(item) and not is_pending(item.content_path)
    ]
    return pended

def check_torrents() -> str:
    to_render = recently_downloaded(client)
    is_file = False
    if to_render:
        for folder in to_render:
            content_path = folder.content_path
            if os.path.isdir(content_path):
                has_content = check_filetype(content_path)
            else:
                has_content = check_type(content_path)
                is_file = True
            notify_me(
                chat_id=ChatId.admin,
                message=f"{folder.content_path} downloaded "
                        f"and added to waiting model",
            )
            PendingModel(
                folder_path=content_path,
                ident=make_hash(folder.content_path),
                has_content=bool(has_content),
                is_file=is_file,
            ).save()
        return "Есть скачанные торренты"
    return "Пока без новых торрентов"


