# sales/functions.py
def send_message(lead, template_id, channel=None):
    # envía mensaje usando template
    pass

def send_email(lead, template_id):
    pass

def send_whatsapp(lead, template_id):
    pass

def create_task(lead, title, assigned_to=None):
    pass

def notify_user(user_id, message):
    pass

def follow_up(lead, status):
    pass


def update_lead_status(lead, status):
    pass



# registrar todas las funciones para el admin
FUNCTIONS_AVAILABLE = {
    "send_message": send_message,
    "send_email": send_email,
    "send_whatsapp": send_whatsapp,
    "create_task": create_task,
    "notify_user": notify_user,
    "update_lead_status": update_lead_status,
    "follow_up": follow_up,
}