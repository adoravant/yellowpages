# sales/events.py

from sales.models import Event
from engine.models import EventTypeConfig, TriggerRule


class Events:

    # ==========================
    # STATUS
    # ==========================
    STATUS_VALIDATED = "status_validated"
    STATUS_PAIN = "status_pain"
    STATUS_INTEREST = "status_interest"
    STATUS_CAPACITY = "status_capacity"
    STATUS_OFFER = "status_offer"
    STATUS_CALL = "status_call"
    STATUS_MEETING = "status_meeting"
    STATUS_QUOTE = "status_quote"
    STATUS_CONTRACT = "status_contract"

    # ==========================
    # INTENTS (mensajes salientes tuyos)
    # ==========================
    INTENT_VALIDATION = "intent_validation"
    INTENT_INTEREST = "intent_interest"
    INTENT_CAPACITY = "intent_capacity"
    INTENT_OFFER = "intent_offer"
    INTENT_CALL = "intent_call"
    INTENT_MEETING = "intent_meeting"
    INTENT_QUOTE = "intent_quote"
    INTENT_FOLLOWUP = "intent_followup"
    INTENT_CLOSING = "intent_closing"

    # ==========================
    # REPLIES (mensajes entrantes del lead)
    # ==========================
    REPLY_VALIDATION = "reply_validation"
    REPLY_INTEREST = "reply_interest"
    REPLY_CAPACITY = "reply_capacity"
    REPLY_OFFER = "reply_offer"
    REPLY_CALL = "reply_call"
    REPLY_MEETING = "reply_meeting"
    REPLY_QUOTE = "reply_quote"
    REPLY_FOLLOWUP = "reply_followup"
    REPLY_CLOSING = "reply_closing"

    # ==========================
    # COMMS (errores de comunicación)
    # ==========================
    COMM_WHATSAPP_IGNORED = "comm_whatsapp_ignored"
    COMM_WHATSAPP_FAILED = "comm_whatsapp_failed"
    COMM_EMAIL_BOUNCED = "comm_email_bounced"
    COMM_EMAIL_FAILED = "comm_email_failed"
    COMM_EMAIL_IGNORED = "comm_email_ignored"

    # ==========================
    # LIFECYCLE
    # ==========================
    LIFE_CREATED = "life_created"
    LIFE_UPDATED = "life_updated"
    LIFE_DELETED = "life_deleted"

    # ==========================
    # CONTEXTO / MICROACCIONES
    # ==========================
    CTX_EMAIL_OPEN = "ctx_email_open"
    CTX_EMAIL_CLICK = "ctx_email_click"
    CTX_FORM_SUBMIT = "ctx_form_submit"
    CTX_WEBSITE_VISIT = "ctx_website_visit"
    CTX_INACTIVITY = "ctx_inactivity"

    # ==========================
    # STRATEGY / SCORING
    # ==========================
    STR_HOT_LEAD = "str_hot_lead"
    STR_COLD_LEAD = "str_cold_lead"
    STR_ENGAGED = "str_engaged"
    STR_SEQUENCE_DETECTED = "str_sequence_detected"
    STR_PRIORITY_BOOST = "str_priority_boost"

    # ==========================
    # TIME / TEMPORALIDAD
    # ==========================
    TIME_TASK_OVERDUE = "time_task_overdue"
    TIME_NO_REPLY_24H = "time_no_reply_24h"
    TIME_NO_INTERACTION_72H = "time_no_interaction_72h"
    TIME_LAST_CLICK_48H = "time_last_click_48h"
    TIME_MILESTONE_DELAY = "time_milestone_delay"

    # ==========================
    # MISC / MICROEVENTOS ATÓMICOS
    # ==========================
    MISC_MESSAGE_SENT = "misc_message_sent"
    MISC_MESSAGE_RECEIVED = "misc_message_received"
    MISC_LINK_CLICKED = "misc_link_clicked"
    MISC_RESOURCE_SENT = "misc_resource_sent"
    MISC_CALL_ATTEMPTED = "misc_call_attempted"
    MISC_CALL_COMPLETED = "misc_call_completed"
    MISC_MEETING_SCHEDULED = "misc_meeting_scheduled"
    MISC_MEETING_DONE = "misc_meeting_done"
    MISC_OBJECTION_RAISED = "misc_objection_raised"
    MISC_FEEDBACK_PROVIDED = "misc_feedback_provided"


def event_choices():
    return [
        (value, value.replace("_", " ").title())
        for key, value in Events.__dict__.items()
        if isinstance(value, str) and not key.startswith("_")
    ]


def create_event(lead, event_slug, channel=None, metadata=None):
    event_type = EventTypeConfig.objects.get(slug=event_slug)
    event = Event.objects.create(
        lead=lead,
        event_type=event_type,
        channel=channel,
        metadata=metadata or {}
    )
    rules = TriggerRule.objects.filter(
        event_type=event_type,
        active=True
    )
    for rule in rules:
        rule.create_task_for_lead(lead)
    return event