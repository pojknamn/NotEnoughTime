import os
from conf import logger, SPLITTER, ENCODED_FOLDER
from pydantic import BaseModel

from utils import check_audio, create_subfolders, has_subtitles, probe
from utils.orm import get_ticket, save_to_db


class TicketModel(BaseModel):
    ticket_id: int
    user_id: int
    working_directory: str
    serial: bool
    recursive: bool
    status: str
    speed: float
    subtitles: bool
    external_audio: str
    folder_json: dict
    items: dict


class ItemsProcedure:

    def __init__(self, ticket: TicketModel):
        self.ticket = ticket
        self._splitter = SPLITTER
        self._extract_from_rl()
        self.items_to_render = self.ticket.items['items']
        self._errors = []

    def _extract_from_rl(self) -> None:
        """Extract all media-files from working directory."""
        if os.path.isdir(self.ticket.working_directory):
            create_subfolders(
                start_dir=self.ticket.working_directory,
                recursive=self.ticket.recursive,
                ticket_id=self.ticket.ticket_id
            )
        else:
            save_to_db(self.ticket.ticket_id, key='items', data=[self.ticket.working_directory])
        self._update_ticket()

    @property
    def commands(self) -> list[dict]:
        """Returns list of commands."""
        return self._generate_commands()

    def _generate_commands(self) -> list[dict]:
        """Generate commands to render with ffmpeg."""
        commands = []
        for item in self.items_to_render:
            try:
                commands.append(self._make_command(item))
            except Exception as process_error:
                logger.error(f"This file contains error: {item}, error message {process_error}")
                self._errors.append((item, process_error))
        return commands

    def _split_item(self, fullpath: str) -> tuple[str, str, str]:
        """Split fullpath with system delimiter."""
        return fullpath.rpartition(self._splitter)

    def _get_filename(self, fullpath: str) -> str:
        """Extract filename from fullpath."""
        return self._split_item(fullpath)[-1].rpartition(".")[0]

    def _output_name(self, fullpath: str) -> str:
        """Generate output name with edited folder."""
        base, _, filename = self._split_item(fullpath=fullpath)
        edited_folder = f"{self._splitter}{ENCODED_FOLDER}{self._splitter}"
        return base + edited_folder + filename.replace("avi", "mp4")

    def _get_video_filter(self, fullpath: str) -> str:
        """
        Return videofilter for videos.
        Downscale 4k to FullHD if needed
        """
        if probe(fullpath).get("streams")[0].get("height") == 2160:
            videofilter = "[0:v]scale=1920:1080[m];[m]"
        else:
            videofilter = "[0:v]"
        return videofilter

    def _get_subtitle(self, fullpath: str) -> str:
        """Return subtitle pass if user ask add subtitles"""
        if self.ticket.subtitles and has_subtitles(fullpath):
            return f'-i "{fullpath.rpartition(".")[0]}_subs.srt"'
        else:
            return ''

    def get_external_audio(self, filename: str) -> str:
        """Match external audio path to current item"""
        if self.ticket.external_audio:
            for item in os.listdir(self.ticket.external_audio):
                if filename in item:
                    return f'-i "{self.ticket.external_audio}{self._splitter}{item}"'
        else:
            return ""

    def _make_command(self, fullpath: str):
        filename = self._get_filename(fullpath)
        audio_path = self.get_external_audio(filename)
        subtitle = self._get_subtitle(fullpath) if self.ticket.subtitles else ''
        audio = check_audio(fullpath)
        videofilter = self._get_video_filter(fullpath)
        speed = self.ticket.speed
        output = self._output_name(fullpath)
        command = f'ffmpeg -n -loglevel warning -stats -threads 6 '\
                  f'-i "{fullpath}" {audio_path} {subtitle} '\
                  f'-filter_complex "{videofilter}setpts=(1/{speed})*PTS[v];'\
                  f'[{1 if audio_path else 0}:a:{audio}]atempo={speed}[a]" '\
                  f'-map "[v]" -map "[a]" ' \
                  f'{f"-map {2 if audio_path else 1}:s" if subtitle else ""} '\
                  f'-crf 18 -preset superfast "{output}"'
        logger.debug(command)
        return {'command': command, 'filename': filename}

    def _update_ticket(self):
        """Updating the Ticket to catch newly added items."""
        self.ticket = get_ticket(self.ticket.ticket_id)

    def errors(self):
        return self._errors


if __name__ == '__main__':
    a = ItemsProcedure(get_ticket('156215315201581659'))
    c = a.commands
    b = 1