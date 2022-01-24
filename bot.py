import telebot
import bsg_python_master.bsg_restapi as api
from logger import logger
from users_db import Users
from config import ADMIN_ID, TOKEN, API_KEY, DB_PATH
from converter import message_to_subscribers_list
from hlr_engine import hlr_check, hlr_recheck
from bot_ui_lang_EN import *

bot = telebot.TeleBot(TOKEN)
users = Users(DB_PATH)

admin_commands = [BUT_ERROR_LOG, BUT_RESPONSE_LOG, BUT_USER_LIST]


def user_keyboard():
    """Define user keyboard (Telebot markup)"""
    user_markup = telebot.types.ReplyKeyboardMarkup(True, True)  # user keyboard-menu
    user_markup.row(BUT_REQ)
    user_markup.row(BUT_BAL, BUT_GET_ID)
    user_markup.row(BUT_HELP, BUT_HLR_COMMON_INFO)
    return user_markup


def admin_keyboard():
    """Define admin keyboard (Telebot markup)"""
    admin_markup = telebot.types.ReplyKeyboardMarkup(True, True)  # admin keyboard-menu
    admin_markup.row(BUT_REQ)
    admin_markup.row(BUT_BAL, BUT_GET_ID)
    admin_markup.row(BUT_HELP, BUT_HLR_COMMON_INFO)
    admin_markup.row(BUT_USER_LIST)
    admin_markup.row(BUT_ERROR_LOG, BUT_RESPONSE_LOG)
    return admin_markup


@bot.message_handler(func=lambda message: (message.from_user.id == ADMIN_ID) and (message.text == BUT_ERROR_LOG))
def send_error_log(message):
    """ONLY ADMIN: Sends error log file by admin request"""
    try:
        with open("hlr_errors.log", 'rb') as doc:
            bot.send_document(message.chat.id, doc)
        logger.info(f'Admin got error log', action='admin_do')
    except Exception as er_desc:
        logger.error(f'Cant send error log file. Error description: {er_desc}')


@bot.message_handler(func=lambda message: (message.from_user.id == ADMIN_ID) and (message.text == BUT_RESPONSE_LOG))
def send_response_log(message):
    """ONLY ADMIN: Sends HLR results history (log file) by admin request"""
    try:
        with open("hlr_responses.log", 'rb') as doc:
            bot.send_document(message.chat.id, doc)
        logger.info(f'Admin got responses log', action='admin_do')
    except Exception as er_desc:
        logger.error(f'Cant send responses log file. Error description: {er_desc}')


@bot.message_handler(func=lambda message: message.from_user.id == ADMIN_ID and message.text == BUT_USER_LIST)
def send_user_list(message):
    """ONLY ADMIN: Sends users list with activity status (active/blocked) by admin request"""
    try:
        t_user_list = users.get_users()
        bot.send_message(message.chat.id, t_adm_user_list_head + t_user_list + t_adm_user_list_tail)
        logger.info(f'Admin got users list', action='admin_do')
    except Exception as er_desc:
        logger.error(f'Cant send users list: {er_desc}')


@bot.message_handler(func=lambda message: (message.from_user.id == ADMIN_ID) and (message.text.startswith('add_user')))
def add_user(message):
    """ONLY ADMIN: Add new user or unblock exist"""
    if len(message.text.split(' ')) == 3:
        new_id = message.text.split(' ')[1]
        new_alias = message.text.split(' ')[2]
        if new_id.isdigit():
            try:
                users.add_user(new_id, new_alias)
                logger.info(f'Admin set access TRUE for user: {new_alias} ({new_id})', action='admin_do')
                bot.send_message(message.chat.id, t_adm_user_added + f'{new_alias} ({new_id})')
            except Exception as er_desc:
                logger.error(f'Cant add user {new_alias} ({new_id}), error description {er_desc}')
        else:
            bot.send_message(message.chat.id, t_adm_unexp_id + t_adm_user_list_tail)
            logger.warning(f'Add user {new_alias} ({new_id}) - wrong ID format')
    else:
        bot.send_message(message.chat.id, t_adm_unexp_command + t_adm_user_list_tail)
        logger.warning(f'Add user command "{message.text}" - wrong command format')


@bot.message_handler(func=lambda message: (message.from_user.id == ADMIN_ID) and
                                          (message.text.startswith('block_user')))
def block_user(message):
    """ONLY ADMIN: Block exist user by ID"""
    if len(message.text.split(' ')) == 2:
        block_id = message.text.split(' ')[1]
        if block_id.isdigit():
            try:
                users.block_user(block_id)
                logger.info(f'Admin set access FALSE for: {users.get_alias(block_id)} ({block_id})', action='admin_do')
                if users.check_id(block_id) is False:
                    bot.send_message(message.chat.id, t_adm_user_blocked + f'{users.get_alias(block_id)} ({block_id})')
            except Exception as er_desc:
                logger.error(f'Cant block user {users.get_alias(block_id)} ({block_id}), error description {er_desc}')
        else:
            bot.send_message(message.chat.id, t_adm_unexp_id + t_adm_user_list_tail)
            logger.warning(f'Block user {users.get_alias(block_id)} ({block_id}) - wrong ID format')
    else:
        bot.send_message(message.chat.id, t_adm_unexp_command + t_adm_user_list_tail)
        logger.warning(f'Block user command "{message.text}" - wrong command format')


@bot.message_handler(commands=['start'])
def start_command(message):
    """Start command handler. Sends different keyboards types (admin/user), logging untrusted activity"""
    current_user_id = message.from_user.id
    current_user_name = users.get_alias(current_user_id)

    if str(current_user_id) == str(ADMIN_ID):
        bot.send_message(message.chat.id, t_msg_trust + "\nGOD MODE ON", reply_markup=admin_keyboard())
        logger.info(f'Admin {current_user_name} ({current_user_id}) restarted the bot', action='admin_do')
    elif users.check_id(current_user_id):
        bot.send_message(message.chat.id, t_msg_trust, reply_markup=user_keyboard())
        logger.info(f'User {current_user_id} ({current_user_name}) restarted the bot', action='user_do')
    else:
        bot.send_message(message.chat.id, t_msg_untrust + str(current_user_id), reply_markup=user_keyboard())
        logger.warning(f'Unknown user {current_user_id} started the bot')


@bot.message_handler(content_types=['text'], func=lambda message: message not in admin_commands)
def receive_user_message(message):
    """Main message handler: info dialogs (buttons use), HLR check"""
    user_id = message.from_user.id  # Telegram id
    user_name = users.get_alias(user_id)  # user's alias in DB
    user_access = users.check_id(user_id)  # check user's permission
    if message.text == BUT_HELP:  # typing hints
        logger.info(f"{user_name} ({user_id}) clicked 'TYPING HELP' button", action='user_do')
        bot.send_message(message.chat.id, t_bot_help)
    elif message.text == BUT_HLR_COMMON_INFO:  # about HLR-lookup
        logger.info(f"{user_name} ({user_id}) clicked 'ABOUT-HLR' button", action='user_do')
        bot.send_message(message.chat.id, t_hlr_desc)
    elif message.text == BUT_GET_ID:  # returns user's Telegram ID
        logger.info(f"{user_name} ({user_id}) clicked 'MY-ID' button", action='user_do')
        bot.send_message(message.chat.id, str(user_id))
    elif not user_access:
        logger.info(f"{user_name} ({user_id}) got 'ACCESS DENIED' message", action='user_do')
        bot.send_message(message.chat.id, t_msg_untrust + str(user_id), reply_markup=user_keyboard())
    elif message.text == BUT_BAL and user_access:  # check account balance
        logger.info(f"{user_name} ({user_id}) clicked 'BALANCE CHECK' button", action='user_do')
        try:
            client = api.BalanceAPI(config={'api_key': API_KEY})
            balance = client.get()
            if balance and 'amount' in balance.keys():
                balance_string = str(int(float(balance.get('amount')))) + " " + \
                                 str(balance.get('currency'))
                bot.send_message(message.chat.id, t_msg_balance + balance_string)
                logger.info(f"{user_name} ({user_id}) got balance info - {balance_string}", action='user_do')
            else:
                logger.warning(f'{user_name} ({user_id}) balance info None response ({balance})')
                bot.send_message(message.chat.id, t_msg_balance_error)
        except api.APIError as exc:
            bot.send_message(message.chat.id, t_msg_balance_error)
            logger.error(f'{user_name} ({user_id}) API req error ({exc})')
    elif message.text == BUT_REQ:  # request invite and hide menu
        bot.send_message(message.chat.id, t_typing_invite)
        logger.info(f"{user_name} ({user_id}) clicked 'REQUEST' button", action='user_do')
    else:
        # Prepare user input:
        received_message = str(message.text).replace('\t', ',').replace('\n', ',')
        list_to_work = message_to_subscribers_list(received_message)  # typing check, split
        logger.info(f'{user_id}\t'
                    f'{user_name}\t'
                    f'{len(list_to_work)}\t'
                    f'{message.text}\t',
                    action='request')

        # No phone numbers recognized:
        if not list_to_work:
            bot.send_message(message.chat.id, t_typing_error)

        # Send HLR:
        elif len(list_to_work) > 0:

            # Request delivery confirmation (for user):
            confirm_request = t_sent_req
            for phone in list_to_work:
                confirm_request += '\n' + '⏳ ' + str(phone)
            bot.send_message(message.chat.id, confirm_request)  # echo with recognized phone list

            # HLR check number-by-number:
            for phone in list_to_work:
                res = hlr_check(phone)  # MAIN HLR EXCHANGE FUNC
                if not res.get("main_status"):  # None response type
                    activity_status = 'None'
                    logger.warning(f'None response for {str(res.get("phone_number"))}, initiator: {user_name}')
                elif res.get("main_status") in status_dict.keys():  # expected (known) response status
                    activity_status = status_dict.get(res.get("main_status"))
                else:
                    activity_status = t_unexp_status   # unexpected status
                    logger.error(f'Unexpected response "{str(res.get("main_status"))}" for '
                                 f'{str(res.get("phone_number"))}, '
                                 f'initiator: {user_name}')

                # Concating answer for user:
                human_answer = t_res_title + str(res.get("phone_number")) + ': ' + activity_status
                if res.get('brand_name'):
                    human_answer += f"\n📶 {res.get('brand_name')} ({res.get('brand')})"
                if res.get('brand_name'):
                    human_answer += f"\n🌐 {res.get('country_name')}"
                if str(res.get('ported')) == '1':
                    human_answer += t_porting
                if str(res.get('roaming')) == '1':
                    human_answer += t_roaming

                # Send message to user (HLR result)
                bot.send_message(message.chat.id, human_answer)

                # Recheck if timeout:
                if res.get('main_status') == 'sent':
                    bot.send_message(message.chat.id, t_more_time)
                    new_status = hlr_recheck(res)
                    if new_status == 'sent':
                        bot.send_message(message.chat.id, t_more_time_no_resp)
                        logger.error(f'HLR timeout {res.get("phone_number")}, initiator: {user_name}')
                    elif new_status in status_dict.keys():
                        res.update({'main_status': new_status})
                        new_ans = str(res.get('phone_number')) + ': ' + str(status_dict.get(new_status))
                        bot.send_message(message.chat.id, new_ans)
                    else:
                        print(f'\t{t_unexp_status} - ' + new_status)
                        new_ans = str(res.get('phone_number')) + ': ' + str(new_status)
                        bot.send_message(message.chat.id, new_ans)
                        logger.error(f'HLR unexpected status "{new_status}" '
                                     f'for {res.get("phone_number")}, '
                                     f'initiator: {user_name}')

                # Log response:
                logger.success(f'{user_id}\t{user_name}\t'
                               f'{res.get("phone_number")}\t'
                               f'{res.get("main_status")}\t'
                               f'{[[a, b] for a, b in res.items()]}',
                               action='response_full')
                logger.success(f'{user_id}\t'
                               f'{user_name}\t'
                               f'{res.get("phone_number")}\t'
                               f'{res.get("main_status")}',
                               action='response_short')
