from typing import Any

from conf import ChatId, PENDING, WORKING

from ormmanager.models import TicketModel
# UsersModel
from torrentschecker.models import PendingModel


# def add_ticket_to_user(user_id: int, ticket: int) -> None:
#     user, _ = UsersModel.objects.get_or_create(user_id=user_id)
#     user.last_ticket = ticket
#     user.save()

#
# def get_ticket_owner(ticket: int) -> int:
#     user = UsersModel.objects.filter(last_ticket=ticket).get()
#     return user.user_id


# def get_user_last_ticket(user_id: int) -> int:
#     model = UsersModel.objects.filter(user_id=user_id).get()
#     return model.last_ticket


def update_status(ticket: TicketModel, status: str):
    ticket.status = status
    ticket.save()


def get_ticket(ticket_id) -> TicketModel:
    ticket, created = TicketModel.objects.get_or_create(ticket_id=ticket_id)
    return ticket


def create_ticket(ticket_id: int, user_id: int = None):
    ticket, created = TicketModel.objects.get_or_create(ticket_id=ticket_id,
                                                        user_id=user_id,
                                                        working_directory='',
                                                        folders_json={})
    return ticket


def save_to_db(ticket: int | str, data: Any, key: str):
    ticket = get_ticket(ticket)
    if key == 'json':
        ticket.folders_json = data
        ticket.working_directory = data['last_opt']
    elif key == 'speed':
        ticket.speed = data
    elif key == 'subtitle':
        ticket.subtitles = data
    elif key == 'items':
        items = ticket.items
        items['items'].extend(data)
        ticket.items = items
    ticket.save()


def folder_from_response(ticket: int | str, response: str) -> str:
    ticket = get_ticket(ticket)
    folder = ticket.folders_json.get(response).get('path')
    return folder


def get_option_from_json(ticket: int, response: str) -> str:
    ticket = get_ticket(ticket)
    option = ticket.folders_json.get(response)
    return option


def pending_ticket():
    all_tickets = TicketModel.objects.filter(status=PENDING)
    working = TicketModel.objects.filter(status=WORKING)
    if working:
        return
    if all_tickets:
        return all_tickets[0]


def get_recently_downloaded():
    all_downloads = PendingModel.objects.filter(status__iexact="DOWNLOADED") \
        .filter(has_content=True)
    if not all_downloads:
        return
    return all_downloads[0]


def make_ticket_from_download(download_model: PendingModel):
    new_ticket = TicketModel.objects.create(ticket_id=download_model.ident,
                                            working_directory=download_model.folder_path,
                                            user_id=ChatId.admin)
    return new_ticket
