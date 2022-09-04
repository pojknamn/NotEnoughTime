from utils import bot, encode_response, gen_options_kb
from utils.orm import (get_recently_downloaded, make_ticket_from_download,
                       update_status)


def suggest_one():
    recent_one = get_recently_downloaded()
    if recent_one:
        save_to_ticket = make_ticket_from_download(recent_one)
        update_status(recent_one, 'SUGGESTED')
        message = {
            'option_type': 'speed',
            'ticket_id': save_to_ticket.ticket_id,
            'option_value': '',
        }
        response = encode_response(message)
        bot.send_message(chat_id=save_to_ticket.user_id,
                         text=f"{save_to_ticket.working_directory}: \n"
                              f"Насколько ускорить?",
                         reply_markup=gen_options_kb(response))
        return "Успешно предложено"
    return "Нечего предлагать"
