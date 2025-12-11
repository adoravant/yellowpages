STEP_ACTIONS = [
    ("ask_call", "Ask Call", 1),
    ("avanzar", "Avanzar", 2),
    ("descuento", "Descuento", 3),
    ("disculpame", "Disculpame", 4),
    ("equivocado", "Equivocado", 5),
    ("not_interested", "Not Interested", 6),
    ("not_owner", "Not Owner", 7),
    ("objecion_diagnostico", "Objeción Diagnóstico", 8),
    ("objecion_oferta", "Objeción Oferta", 9),
    ("objecion_seguimiento", "Objeción Seguimiento", 10),
    ("presentacion", "Presentación", 11),
    ("presion", "Presión", 12),
    ("recordatorio", "Recordatorio", 13),
]



CLOSING_ACTIONS = {
    "not_owner": "closed_not_owner",
    "equivocado": "closed_equivocado",
    "not_interested": "closed_not_interested",
    "phone_dead": "closed_phone_dead",
    "win": "closed_won",
}