# constants.py - raíz del proyecto
# ========================

# ------------------------
# Tipos de Trigger
# ------------------------
TRIGGER_TYPE_CHOICES = [
    ("AUTOMATIC", "Automatic"),
    ("MANUAL", "Manual"),
    ("SCHEDULED", "Periodic"),
]

# ------------------------
# Estados de Leads
# ------------------------
LEAD_STATUS_CHOICES = [
    ("NEW", "New"),
    ("IN_PROGRESS", "In Progress"),
    ("LOST", "Lost"),
    ("WON", "Won"),
]

# ------------------------
# Estados de Tasks
# ------------------------
TASK_STATUS_CHOICES = [
    ("pending", "Pending"),
    ("running", "Running"),
    ("success", "Success"),
    ("failed", "Failed"),
]

# ------------------------
# Hitos / Milestones del Lead
# ------------------------
LEAD_MILESTONE_CHOICES = [
    ('1_VAL', 'Validation'),
    ('2_PAIN', 'Pain Identification'),
    ('3_HOOK', 'Hook / Interest'),
    ('4_CAP', 'Capacity Check'),
    ('5_OFF', 'Offer / Solution'),
    ('6_CALL', 'Call Scheduled'),
    ('7_MEET', 'Meeting Done'),
    ('8_QUO', 'Quote Sent'),
    ('9_CON', 'Contract Signed'),
]

# ------------------------
# Modo de Ejecución de Tasks
# ------------------------
TASK_EXECUTION_MODE_CHOICES = [
    ("AUTO", "Automática (System)"),
    ("HUMAN", "Manual (User)"),
]

# ------------------------
# Canales de comunicación
# ------------------------
COMMUNICATION_CHANNEL_CHOICES = [
    ("WHATSAPP", "📱 WhatsApp"),
    ("EMAIL", "📧 Email"),
    ("CALL", "📞 Llamada"),
]

# ------------------------
# Categorías de EventType
# ------------------------
EVENT_CATEGORY_CHOICES = [
    ("STATUS", "Status"),
    ("INTENT", "Intent"),
    ("REPLY", "Reply"),
    ("CONTEXT", "Context / Microacciones"),
    ("LIFECYCLE", "Lifecycle"),
    ("STRATEGY", "Strategy / Scoring"),
    ("TIME", "Temporal / Triggers"),
    ("MISC", "Otros / Microeventos"),
    ("COMM", "Communication")
]



TRIGGER_MODE_CHOICES = [
    ("AUTO", "Automatic"),
    ("MANUAL", "Manual Only"),
    ("BOTH", "Auto + Manual"),
]



WEBSITE_STATUS_SEGMENTS = [
('CORES', 'Cores (Optimizable)'),
('DOWN', 'Down (Web Caída)'),
('NO_CORES', 'No Cores (Infra Débil)'),
('SOCIAL', 'Social (Solo Redes)'),
('SSL_ERROR', 'SSL Error (Inseguro)'),
('TIMEOUT', 'Timeout (Lenta)'),
]