from config import ADMIN_CONTACT, LIST_LIMIT

t_bot_desc = "Bot verifies a mobile phone number activity status by HLR-lookup. The request is processed by the " \
             "communication operator without reaching the phone of the checked subscriber (it is not reflected in " \
             "the call details and is not shown to the subscriber). Subscriber information obtained from the HLR " \
             "register may indicate: " \
             "\nš” termination of service" \
             "\nš” fixed on-line during the last day" \
             "\nš” home country" \
             "\nš” communication operator" \
             "\nš” service network ID" \
             "\n\nIn some cases and countries:" \
             "\n   ā” roaming status " \
             "\n   ā” IMSI number" \
             "\n   ā” porting status to another network. " \
             "\n\nš Access to HLR data does not conflict with personal data protection standards and policies (GDPR)."

t_bot_help = f'To correctly identify the requested subscribers - print the number without spaces. Printing with ' \
             f'technical symbols is allowed "-" "+" ")(". The bot supports checking up to {LIST_LIMIT} numbers with ' \
             f'delimiters: comma, semicolon, tab, space or each number on a new line. ' \
             f'\n\nā Correct:\n0958656688, (093)345-34-34, 6625533-44 +38(067)222-33-44; 380504456688' \
             f'\n\nā Wrong:\n095 776-22-13, +38 (095) 3345544, 38050 466 77 88'

t_hlr_desc = "HLR (Home Location Register). Temporary information about the last base station in which subscribers " \
             "were fixed. Information is updated when you turn on the phone, move from one BS to another. Based on " \
             "the HLR, the operator chooses which BS use to establish a connection with the subscriber. If the " \
             "subscriber has not updated his location for a long time (6 ... 24 hours - depending on the chosen " \
             "operator's policy), the subscriber is considered absent in the home network. Certain entries of the HLR " \
             "register are publicly available and used in the field of advertising. " \
             "\nSubscriber information obtained from the HLR may indicate: " \
             "\nš” termination of service" \
             "\nš” fixed on-line during the last day" \
             "\nš” home country" \
             "\nš” communication operator" \
             "\nš” service network ID" \
             "\n\nIn some cases and countries:" \
             "\n   ā” roaming status " \
             "\n   ā” IMSI number" \
             "\n   ā” porting status to another network. " \
             "\n\nš Access to HLR data does not conflict with personal data protection standards and policies (GDPR)."

t_msg_trust = 'Bot started. You are trusted user. š '
t_msg_untrust = f'š Access denied. Call to {ADMIN_CONTACT} ' \
                f'for permission. Your ID - '
t_msg_balance = 'š° Money - '
t_msg_balance_error = 'Account balance not available now'
t_typing_invite = f'Input one or few subscriber\'s numbers (max {LIST_LIMIT}):'
t_typing_error = 'No number. Check typing.'

t_sent_req = 'Sent request:'
t_unexp_status = 'šµ Unknown response format'
t_porting = '\nš There are signs of porting to another operator'
t_roaming = '\nā reported roaming!'
t_more_time = 'Additional response time...'
t_more_time_no_resp = 'No answer. Try again later.'
t_res_title = 'š Result for '

t_adm_user_list_head = 'USERS LIST:\n'
t_adm_user_list_tail = "\nAdmin commands:\n" \
                       "š add_user <telegramID> <Alias>\n" \
                       "š block_user <telegramID>\n\n" \
                       "Arguments:\n" \
                       "ā” telegramID - only digits\n" \
                       "ā” Alias - Ńhosen name for DB.\n"

t_adm_user_added = 'Allowed access to user - '
t_adm_user_blocked = "User blocked - "
t_adm_user_not_found = "No user by this ID "
t_adm_unexp_command = 'Unknown command, not enough arguments '
t_adm_unexp_id = 'only digits in Telegram ID '


BUT_REQ = 'š¤ Send HLR-request'
BUT_BAL = 'š Check balance'
BUT_HELP = 'š Typing hints'
BUT_HLR_COMMON_INFO = 'āAbout HLR'
BUT_GET_ID = 'š Get my ID'
BUT_ERROR_LOG = 'š ERRORS'
BUT_RESPONSE_LOG = 'š HISTORY'
BUT_USER_LIST = 'USER LIST'

SYMBOL_OFF = 'āš“'
SYMBOL_ON = 'āš²'
SYMBOL_BARRED = 'š«š'
SYMBOL_UNKNOWN = 'āš'

status_dict = {'active': '\nā on-line (active)',
               'absent': '\nā off_line (absent)',
               'failed': '\nšµ failed',
               'None': '\nšµ empty result (maybe typing was incorrect)',
               'barred': '\nšµ š§ request was barred (š maybe user was ported to another operator)',
               'unknown': '\nšµ can\'t get status (the subscriber is unknown in the operator\'s network '
                          '(may no longer be serviced or never existed))',
               'sent': '\nšµ š¤ timed out waiting for a response. Retry...',
               'money': '\nšµ no money'}
