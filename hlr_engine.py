from time import sleep
import bsg_python_master.bsg_restapi as api
from config import API_KEY, AWAIT_RESPONSE_TIME
from logger import logger


hlr_instance = api.HLRAPI(config={'api_key': API_KEY})


def hlr_check(phone_number) -> dict:
    """
    API connector. Result description (keys):

    - phone_number: subscriber phone_number
    - number_id: request id (able to recheck)
    - main_status: phone status (active, absent, barred, etc.)
    - imsi: recieved SIM IMSI (may be half-hidden or changed)
    - ported: another network porting sign
    - roaming: use roaming sign
    - country_name: current operator country belong
    - network: operator network ID
    - brand: operator network name
    - brand_name: operator full name

    :param phone_number: (str) subscriber number (international format - 380951112233)
    :return: dict
    """

    try:
        lookup_object = api.HLRL(phone_number)
        result = hlr_instance.send(lookup_object)
        logger.debug(f'Sent HLR request - {phone_number}')
        number_id = result['result'][0]['id']
        number_ref = result['result'][0]['reference']
        sleep(AWAIT_RESPONSE_TIME)

        status_by_id = hlr_instance.get_status(number_id)
        status_by_ref = hlr_instance.get_status(number_ref)
        logger.debug('Received from API HLR: ' + str(status_by_id))

        if 'details' in status_by_id.keys() and isinstance(status_by_id['details'], dict):
            imsi = status_by_id['details'].get('imsi')
            ported = status_by_id['details'].get('ported')
            roaming = status_by_id['details'].get('roaming')

        else:
            imsi, ported, roaming = None, None, None

        phone_hlr_result = {"phone_number": status_by_ref.get('msisdn'),
                            "number_id": number_id,
                            "main_status": status_by_ref.get('status'),
                            "imsi": imsi,
                            "ported": ported,
                            "roaming": roaming,
                            "country_name": status_by_id.get('country_name'),
                            "network": status_by_id.get('network'),
                            "brand": status_by_id.get('brand'),
                            "brand_name": status_by_id.get('brand_name')}
        logger.debug('HLR engine result:' + str(phone_hlr_result))
        return phone_hlr_result

    except api.APIError as exc:
        logger.error(f'API error - {exc}')
        if str(exc) == "Error occurred during request processing. Error code: '8', error reason: 'Not enough money'":
            phone_hlr_result = {"phone_number": phone_number,
                                "main_status": "no money"}
            logger.error("HLR API crashed: NO MONEY ERROR (code:8)")
        else:
            phone_hlr_result = {"phone_number": phone_number,
                                "main_status": "error"}
            logger.error(f"HLR API crashed: {exc}")
        return phone_hlr_result
    except Exception as exc:
        logger.error(f'HLR engine error - {exc}')
        phone_hlr_result = {"phone_number": phone_number,
                            "main_status": "error"}
        return phone_hlr_result


def hlr_recheck(phone_hlr_result: dict) -> str:
    sleep(AWAIT_RESPONSE_TIME*2)
    status = 'error'
    try:
        logger.warning(f'Recheck HLR result - {phone_hlr_result.get("phone_number")}')
        number_id = phone_hlr_result.get("number_id")
        status_id = hlr_instance.get_status(number_id)
        number = status_id.get('msisdn')
        status = status_id.get('status')
        if number and status:
            logger.info(f'New HLR status for {number} - {status}')
        else:
            logger.error(f'No response HLR status for {phone_hlr_result.get("phone_number")}')
    except Exception as common_error:
        logger.error(f'Error due recheck HLR status - {phone_hlr_result.get("phone_number")}: {common_error}')
    return status
