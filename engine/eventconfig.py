# engine/eventconfig.py

EVENT_DEFAULTS = {
    # ==========================
    # STATUS
    # ==========================
    "status_validated": dict(should_alert=False, alert_priority=5, allowed_auto=True, max_consumes=1),
    "status_pain": dict(should_alert=True, alert_priority=8, allowed_auto=False, max_consumes=1),
    "status_interest": dict(should_alert=False, alert_priority=5, allowed_auto=True, max_consumes=1),
    "status_capacity": dict(should_alert=False, alert_priority=4, allowed_auto=True, max_consumes=1),
    "status_offer": dict(should_alert=True, alert_priority=7, allowed_auto=True, max_consumes=1),
    "status_call": dict(should_alert=False, alert_priority=5, allowed_auto=True, max_consumes=1),
    "status_meeting": dict(should_alert=True, alert_priority=6, allowed_auto=True, max_consumes=1),
    "status_quote": dict(should_alert=True, alert_priority=6, allowed_auto=True, max_consumes=1),
    "status_contract": dict(should_alert=True, alert_priority=10, allowed_auto=False, max_consumes=1),

    # ==========================
    # INTENTS
    # ==========================
    "intent_validation": dict(should_alert=False, alert_priority=3, allowed_auto=True, max_consumes=1),
    "intent_interest": dict(should_alert=False, alert_priority=3, allowed_auto=True, max_consumes=1),
    "intent_capacity": dict(should_alert=False, alert_priority=3, allowed_auto=True, max_consumes=1),
    "intent_offer": dict(should_alert=True, alert_priority=6, allowed_auto=True, max_consumes=1),
    "intent_call": dict(should_alert=False, alert_priority=4, allowed_auto=True, max_consumes=1),
    "intent_meeting": dict(should_alert=True, alert_priority=6, allowed_auto=True, max_consumes=1),
    "intent_quote": dict(should_alert=True, alert_priority=6, allowed_auto=True, max_consumes=1),
    "intent_followup": dict(should_alert=False, alert_priority=4, allowed_auto=True, max_consumes=1),
    "intent_closing": dict(should_alert=True, alert_priority=9, allowed_auto=False, max_consumes=1),

    # ==========================
    # REPLIES
    # ==========================
    "reply_validation": dict(should_alert=False, alert_priority=3, allowed_auto=True, max_consumes=1),
    "reply_interest": dict(should_alert=False, alert_priority=3, allowed_auto=True, max_consumes=1),
    "reply_capacity": dict(should_alert=False, alert_priority=3, allowed_auto=True, max_consumes=1),
    "reply_offer": dict(should_alert=True, alert_priority=6, allowed_auto=True, max_consumes=1),
    "reply_call": dict(should_alert=False, alert_priority=4, allowed_auto=True, max_consumes=1),
    "reply_meeting": dict(should_alert=True, alert_priority=6, allowed_auto=True, max_consumes=1),
    "reply_quote": dict(should_alert=True, alert_priority=6, allowed_auto=True, max_consumes=1),
    "reply_followup": dict(should_alert=False, alert_priority=4, allowed_auto=True, max_consumes=1),
    "reply_closing": dict(should_alert=True, alert_priority=9, allowed_auto=False, max_consumes=1),

    # ==========================
    # COMMUNICATION
    # ==========================
    "comm_whatsapp_ignored": dict(should_alert=True, alert_priority=5, allowed_auto=True, max_consumes=1),
    "comm_whatsapp_failed": dict(should_alert=True, alert_priority=7, allowed_auto=True, max_consumes=1),
    "comm_email_bounced": dict(should_alert=True, alert_priority=7, allowed_auto=True, max_consumes=1),
    "comm_email_failed": dict(should_alert=True, alert_priority=6, allowed_auto=True, max_consumes=1),
    "comm_email_ignored": dict(should_alert=True, alert_priority=5, allowed_auto=True, max_consumes=1),

    # ==========================
    # LIFECYCLE
    # ==========================
    "life_created": dict(should_alert=False, alert_priority=2, allowed_auto=True, max_consumes=None),
    "life_updated": dict(should_alert=False, alert_priority=2, allowed_auto=True, max_consumes=None),
    "life_deleted": dict(should_alert=True, alert_priority=6, allowed_auto=False, max_consumes=1),

    # ==========================
    # CONTEXTO / MICROACCIONES
    # ==========================
    "ctx_email_open": dict(should_alert=False, alert_priority=2, allowed_auto=True, max_consumes=99),
    "ctx_email_click": dict(should_alert=False, alert_priority=2, allowed_auto=True, max_consumes=99),
    "ctx_form_submit": dict(should_alert=False, alert_priority=3, allowed_auto=True, max_consumes=99),
    "ctx_website_visit": dict(should_alert=False, alert_priority=2, allowed_auto=True, max_consumes=99),
    "ctx_inactivity": dict(should_alert=True, alert_priority=5, allowed_auto=True, max_consumes=1),

    # ==========================
    # STRATEGY / SCORING
    # ==========================
    "str_hot_lead": dict(should_alert=True, alert_priority=9, allowed_auto=False, max_consumes=1),
    "str_cold_lead": dict(should_alert=False, alert_priority=3, allowed_auto=True, max_consumes=1),
    "str_engaged": dict(should_alert=True, alert_priority=6, allowed_auto=True, max_consumes=1),
    "str_sequence_detected": dict(should_alert=True, alert_priority=7, allowed_auto=True, max_consumes=1),
    "str_priority_boost": dict(should_alert=True, alert_priority=8, allowed_auto=True, max_consumes=1),

    # ==========================
    # TIME / TEMPORALIDAD
    # ==========================
    "time_task_overdue": dict(should_alert=True, alert_priority=6, allowed_auto=True, max_consumes=1),
    "time_no_reply_24h": dict(should_alert=True, alert_priority=6, allowed_auto=True, max_consumes=1),
    "time_no_interaction_72h": dict(should_alert=True, alert_priority=6, allowed_auto=True, max_consumes=1),
    "time_last_click_48h": dict(should_alert=False, alert_priority=3, allowed_auto=True, max_consumes=1),
    "time_milestone_delay": dict(should_alert=True, alert_priority=7, allowed_auto=True, max_consumes=1),

    # ==========================
    # MISC / MICROEVENTOS ATÓMICOS
    # ==========================
    "misc_message_sent": dict(should_alert=False, alert_priority=3, allowed_auto=True, max_consumes=99),
    "misc_message_received": dict(should_alert=False, alert_priority=3, allowed_auto=True, max_consumes=99),
    "misc_link_clicked": dict(should_alert=False, alert_priority=2, allowed_auto=True, max_consumes=99),
    "misc_resource_sent": dict(should_alert=False, alert_priority=3, allowed_auto=True, max_consumes=99),
    "misc_call_attempted": dict(should_alert=False, alert_priority=4, allowed_auto=True, max_consumes=99),
    "misc_call_completed": dict(should_alert=True, alert_priority=6, allowed_auto=True, max_consumes=1),
    "misc_meeting_scheduled": dict(should_alert=False, alert_priority=4, allowed_auto=True, max_consumes=1),
    "misc_meeting_done": dict(should_alert=True, alert_priority=6, allowed_auto=True, max_consumes=1),
    "misc_objection_raised": dict(should_alert=True, alert_priority=7, allowed_auto=True, max_consumes=1),
    "misc_feedback_provided": dict(should_alert=False, alert_priority=4, allowed_auto=True, max_consumes=1),
}