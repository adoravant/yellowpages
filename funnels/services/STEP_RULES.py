STEP_RULES = {

    "validacion": {
        "not_owner": "once",
        "equivocado": "once",

        "presentacion": "until_used",
        "disculpame": "until_used",
        "ask_call": "until_used",
        # avanzar NO VA ACÁ → porque es always
    },

    "diagnostico": {
        "objecion_diagnostico": "once",
        "not_interested": "until_used",
        "disculpame": "until_used",   # este sí aparece en este step desde el step mismo
        # presentacion, ask_call, avanzar → se arrastran solos
    },

    "oferta": {
        "objecion_oferta": "once",
        "not_interested": "until_used",
        "disculpame": "until_used",
        # presentacion, ask_call, avanzar → se arrastran solos
    },

    "seguimiento": {
        "recordatorio": "once",
        "presion": "once",
        "descuento": "once",
        "objecion_seguimiento": "once",

        "not_interested": "until_used",
        "disculpame": "until_used",
        # presentacion, ask_call, avanzar → se arrastran solos
    },
}



GLOBAL_RULES = {
    "avanzar": "always",
}
