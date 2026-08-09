import json
from functools import partial
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.conf import settings
from django.db import transaction as db_transaction
from django.utils import timezone

from .models import EBankingCredential, SMSDelivery, SystemSetting, Transaction


class AakashSMSError(Exception):
    def __init__(self, message, response_data=None):
        super().__init__(message)
        self.response_data = response_data or {}


def normalize_nepal_mobile(phone_number):
    digits = "".join(character for character in str(phone_number or "") if character.isdigit())
    if digits.startswith("977") and len(digits) == 13:
        digits = digits[3:]
    if len(digits) != 10 or not digits.startswith("9"):
        raise ValueError("Recipient must be a valid 10-digit Nepal mobile number.")
    return digits


def send_aakash_sms(recipient, message):
    token = settings.AAKASHSMS_AUTH_TOKEN
    if not token:
        raise AakashSMSError("AAKASHSMS_AUTH_TOKEN is not configured.")

    request_data = urlencode(
        {
            "auth_token": token,
            "to": recipient,
            "text": message,
        }
    ).encode("utf-8")
    request = Request(
        settings.AAKASHSMS_API_URL,
        data=request_data,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=max(1, settings.AAKASHSMS_TIMEOUT_SECONDS)) as response:
            response_body = response.read().decode("utf-8")
    except HTTPError as exc:
        raise AakashSMSError(f"AakashSMS returned HTTP {exc.code}.") from exc
    except URLError as exc:
        raise AakashSMSError(f"Could not connect to AakashSMS: {exc.reason}") from exc

    try:
        response_data = json.loads(response_body)
    except json.JSONDecodeError as exc:
        raise AakashSMSError("AakashSMS returned an invalid JSON response.") from exc

    if response_data.get("error"):
        raise AakashSMSError(
            response_data.get("message") or "AakashSMS rejected the message.",
            response_data=response_data,
        )

    valid_messages = (response_data.get("data") or {}).get("valid") or []
    if not valid_messages:
        invalid_messages = (response_data.get("data") or {}).get("invalid") or []
        reason = invalid_messages[0].get("status") if invalid_messages else "not queued"
        raise AakashSMSError(
            f"AakashSMS did not queue the message: {reason}.",
            response_data=response_data,
        )

    provider_reference = str(valid_messages[0].get("id") or "")
    return provider_reference, response_data


def sanitize_provider_response(value):
    if isinstance(value, dict):
        return {
            key: sanitize_provider_response(item)
            for key, item in value.items()
            if key.lower() not in {"auth_token", "text"}
        }
    if isinstance(value, list):
        return [sanitize_provider_response(item) for item in value]
    return value


def build_collection_receipt_message(transaction_obj):
    system_setting = SystemSetting.get_solo()
    local_transaction_time = timezone.localtime(transaction_obj.transacted_at)
    values = {
        "company_name": system_setting.company_name,
        "customer_name": transaction_obj.customer.full_name,
        "customer_id": transaction_obj.customer.customer_id,
        "currency": system_setting.currency_label or "Rs",
        "amount": f"{transaction_obj.amount:.2f}",
        "receipt": transaction_obj.transaction_id,
        "balance": f"{transaction_obj.balance_after:.2f}",
        "date": local_transaction_time.strftime("%d %b %Y, %H:%M"),
        "payment_method": transaction_obj.payment_method,
    }
    template = system_setting.sms_receipt_template.strip()
    if template:
        try:
            return template.format(**values).strip()
        except (KeyError, ValueError):
            pass

    sender_name = system_setting.sms_sender_name.strip() or system_setting.company_name
    return (
        f"{sender_name}: {values['currency']} {values['amount']} received for "
        f"{values['customer_id']}. Receipt {values['receipt']}. Balance "
        f"{values['currency']} {values['balance']}. Date {values['date']}."
    )


def build_ebanking_login_message(credential):
    system_setting = SystemSetting.get_solo()
    sender_name = system_setting.sms_sender_name.strip() or system_setting.company_name
    return (
        f"{sender_name} E-Banking login. Username: {credential.username}. "
        "Password was provided separately by admin and is not stored."
    )


def build_temporary_password_message(credential, temporary_password):
    system_setting = SystemSetting.get_solo()
    sender_name = system_setting.sms_sender_name.strip() or system_setting.company_name
    return (
        f"{sender_name} E-Banking. Username: {credential.username}. "
        f"Temporary password: {temporary_password}. Please change your password after login."
    )


def build_redacted_temporary_password_message(credential):
    system_setting = SystemSetting.get_solo()
    sender_name = system_setting.sms_sender_name.strip() or system_setting.company_name
    return (
        f"{sender_name} E-Banking. Username: {credential.username}. "
        "Temporary password: [REDACTED]. Please change your password after login."
    )


def attempt_sms_delivery(delivery, message_override=None):
    delivery.provider = "AakashSMS"
    delivery.provider_reference = ""
    delivery.provider_response = {}
    delivery.last_error = ""
    delivery.queued_at = None

    if delivery.event_type == SMSDelivery.EventType.TEMPORARY_PASSWORD and message_override is None:
        delivery.status = SMSDelivery.Status.FAILED
        delivery.last_error = "Temporary passwords are not stored. Reset the password again to send a new one."
        delivery.save()
        return delivery

    if not settings.SMS_ENABLED:
        delivery.status = SMSDelivery.Status.SKIPPED
        delivery.last_error = "SMS is disabled. Configure AAKASHSMS_AUTH_TOKEN or set SMS_ENABLED=True."
        delivery.save()
        return delivery

    delivery.attempt_count += 1
    delivery.last_attempt_at = timezone.now()
    try:
        delivery.recipient = normalize_nepal_mobile(delivery.recipient)
        provider_reference, response_data = send_aakash_sms(
            delivery.recipient,
            message_override or delivery.message,
        )
    except (AakashSMSError, ValueError) as exc:
        delivery.status = SMSDelivery.Status.FAILED
        delivery.last_error = str(exc)
        if isinstance(exc, AakashSMSError):
            delivery.provider_response = sanitize_provider_response(exc.response_data)
    else:
        delivery.status = SMSDelivery.Status.QUEUED
        delivery.provider_reference = provider_reference
        delivery.provider_response = sanitize_provider_response(response_data)
        delivery.queued_at = timezone.now()

    delivery.save()
    return delivery


def send_collection_receipt_sms(transaction_id, force=False):
    transaction_obj = Transaction.objects.select_related("customer").get(pk=transaction_id)
    raw_recipient = transaction_obj.customer.phone_number
    message = build_collection_receipt_message(transaction_obj)
    delivery, created = SMSDelivery.objects.get_or_create(
        transaction=transaction_obj,
        defaults={
            "customer": transaction_obj.customer,
            "recipient": raw_recipient,
            "message": message,
        },
    )
    if not created and not force:
        return delivery

    delivery.customer = transaction_obj.customer
    delivery.recipient = raw_recipient
    delivery.message = message
    delivery.provider = "AakashSMS"
    delivery.provider_reference = ""
    delivery.provider_response = {}
    delivery.last_error = ""
    delivery.queued_at = None
    return attempt_sms_delivery(delivery)


def send_ebanking_login_sms(credential_id):
    credential = EBankingCredential.objects.select_related("customer").get(pk=credential_id)
    delivery = SMSDelivery.objects.create(
        customer=credential.customer,
        event_type=SMSDelivery.EventType.EBANKING_LOGIN,
        recipient=credential.customer.phone_number,
        message=build_ebanking_login_message(credential),
    )
    return attempt_sms_delivery(delivery)


def send_temporary_password_sms(credential_id, temporary_password):
    credential = EBankingCredential.objects.select_related("customer").get(pk=credential_id)
    delivery = SMSDelivery.objects.create(
        customer=credential.customer,
        event_type=SMSDelivery.EventType.TEMPORARY_PASSWORD,
        recipient=credential.customer.phone_number,
        message=build_redacted_temporary_password_message(credential),
    )
    return attempt_sms_delivery(
        delivery,
        message_override=build_temporary_password_message(credential, temporary_password),
    )


def schedule_collection_receipt_sms(transaction_id):
    db_transaction.on_commit(
        partial(send_collection_receipt_sms, transaction_id),
        robust=True,
    )
