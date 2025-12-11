FUNNEL_RULES = {

    "actions": {
        "avanzar": {
            "name": "Avanzar",
            "priority": 1,
            "appearance": "always",
        },
        "presentacion": {
            "name": "Presentación",
            "priority": 2,
            "appearance": "once",
        },
        "disculpame": {
            "name": "Disculpame",
            "priority": 3,
            "appearance": "once",
        },
        "ask_call": {
            "name": "Ask Call",
            "priority": 4,
            "appearance": "until_used",   # ← persiste TODO el funnel
        },
        "not_owner": {
            "name": "Not Owner",
            "priority": 5,
            "appearance": "once",
            "close_status": "closed_not_owner",
        },
        "equivocado": {
            "name": "Equivocado",
            "priority": 6,
            "appearance": "once",
            "close_status": "closed_equivocado",
        },
        "not_interested": {
            "name": "Not Interested",
            "priority": 7,
            "appearance": "until_used",
            "close_status": "closed_not_interested",
        },
        "objecion_diagnostico": {
            "name": "Objeción Diagnóstico",
            "priority": 8,
            "appearance": "once",
        },
        "objecion_oferta": {
            "name": "Objeción Oferta",
            "priority": 9,
            "appearance": "once",
        },
        "objecion_seguimiento": {
            "name": "Objeción Seguimiento",
            "priority": 10,
            "appearance": "once",
        },
        "descuento": {
            "name": "Descuento",
            "priority": 11,
            "appearance": "once",
        },
        "recordatorio": {
            "name": "Recordatorio",
            "priority": 12,
            "appearance": "once",
        },
        "presion": {
            "name": "Presión",
            "priority": 13,
            "appearance": "once",
        },
    },

    "steps": {

        "validacion": {
            "actions": [
                "not_owner",
                "equivocado",
                "presentacion",
                "disculpame",
                "ask_call",
            ]
        },

        "diagnostico": {
            "actions": [
                "objecion_diagnostico",
                "not_interested",
            ]
        },

        "oferta": {
            "actions": [
                "objecion_oferta",
            ]
        },

        "seguimiento": {
            "actions": [
                "objecion_seguimiento",
                "descuento",
                "recordatorio",
                "presion",
            ]
        },
    },

    "global_rules": {
        "nunca_sugerir": ["manual"],
        "siempre_sugerir": ["avanzar"],    # siempre incluida en todos
    },
}
