import os

from utils.orm import pending_ticket, update_status
from conf import WORKING


def renderer():
    ticket = pending_ticket()
    if ticket:
        update_status(ticket, WORKING)
        os.system(f'python render.py {ticket.ticket_id}')
        return f"Взяли тикет в работу: {ticket.ticket_id}"
    return "Нет доступных тикетов к работе или очередь занята"
