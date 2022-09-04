from django.core.management import BaseCommand
from conf import bot_instance, ChatId, PENDING, CLOSED, RMTREE
from shutil import rmtree
from utils.orm import create_ticket, get_option_from_json, get_ticket, \
    update_status, save_to_db
from utils import encode_response, gen_keyboard, decode_response, gen_options_kb

bot = bot_instance


class Command(BaseCommand):
    help = "Комманда запускает бота для отслеживания и запуска задач на ускорение видеоматериалов."

    def handle(self, *args, **options):
        @bot.message_handler(content_types=['text'])
        def send_kb(message):
            ticket_id = hash(message.id)
            user_id = message.chat.id
            create_ticket(ticket_id, user_id)
            response = {
                'ticket_id': ticket_id,
                'option_type': 'workdir',
                'option_value': None,
            }
            response = encode_response(response)
            if user_id == ChatId.admin:
                bot.send_message(chat_id=user_id,
                                 text="Choose",
                                 reply_markup=gen_keyboard(response=response))
            elif user_id == ChatId.friend:
                bot.send_message(chat_id=user_id,
                                 text="Choose",
                                 reply_markup=gen_keyboard(response=response,
                                                           restrict_dir=True))

        @bot.callback_query_handler(func=lambda call: True)
        def callback(call):
            user_id = call.message.chat.id
            response = decode_response(call.data)
            response_type = response.get('option_type')
            response_value = response.get('option_value')
            ticket = response.get('ticket_id')
            message_id = call.message.message_id
            if 'render' in response_type:
                workdir = get_option_from_json(ticket, 'last_opt')
                bot.edit_message_reply_markup(chat_id=user_id,
                                              message_id=message_id,
                                              reply_markup=None)
                bot.edit_message_text(chat_id=user_id,
                                      message_id=message_id,
                                      text=f"Choosen folder: {workdir}")
                response['option_type'] = 'speed'
                response = encode_response(response)
                bot.send_message(chat_id=user_id,
                                 text="Выберите скорость!",
                                 reply_markup=gen_options_kb(response))
            elif 'close' in response_type:
                bot.delete_message(chat_id=user_id, message_id=message_id)
                bot.send_message(chat_id=user_id, text="See you Again!")
                update_status(get_ticket(ticket), CLOSED)
            elif "speed" in response_type:
                choose = response_value
                save_to_db(ticket, choose, 'speed')
                bot.edit_message_text(chat_id=user_id,
                                      message_id=message_id,
                                      text="Нужны субтитры?")
                response['option_type'] = 'subs'
                response = encode_response(response)
                bot.edit_message_reply_markup(chat_id=user_id,
                                              message_id=message_id,
                                              reply_markup=gen_options_kb(response))
            elif 'subs' in response_type:
                choose = response_value
                save_to_db(ticket, choose, 'subtitle')
                bot.edit_message_reply_markup(chat_id=user_id, message_id=message_id)
                bot.edit_message_text(chat_id=user_id,
                                      message_id=message_id,
                                      text="Добавлено в очередь на рендер!")
                update_status(get_ticket(ticket), PENDING)
            elif 'remove' in response_type:
                tick = get_ticket(ticket)
                folder = tick.working_directory
                bot.edit_message_reply_markup(chat_id=user_id, message_id=message_id)
                rmtree(folder, ignore_errors=True)
                bot.edit_message_text(chat_id=user_id,
                                      message_id=message_id,
                                      text=f"Успешно удалена: {folder}")
                update_status(tick, RMTREE)
            else:
                if user_id == ChatId.admin:
                    restrict_dir = False
                else:
                    restrict_dir = True
                bot.edit_message_reply_markup(chat_id=user_id,
                                              message_id=message_id,
                                              reply_markup=gen_keyboard(response=call.data,
                                                                        restrict_dir=restrict_dir))

        bot.infinity_polling()
