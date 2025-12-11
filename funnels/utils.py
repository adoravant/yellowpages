# funnels/utils.py
def render_template(template, lead):
    if not template:
        return None

    ctx = {
        "name": getattr(lead, "name", "") or "",
        "phone": getattr(lead, "phone", "") or "",
        "email": getattr(lead, "email", "") or "",
        "lead_id": getattr(lead, "pk", "") or "",
    }

    text = template.contenido
    for k, v in ctx.items():
        text = text.replace(f"{{{k}}}", str(v))
    return text
