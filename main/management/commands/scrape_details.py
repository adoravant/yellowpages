# main/management/commands/scrape_details.py

import asyncio
import aiohttp
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from asgiref.sync import sync_to_async
from main.models import LeadFull

BASE_URL = "https://www.guiacores.com.ar/index.php?r=search/detail&id="


async def fetch_html(session, url):
    try:
        async with session.get(url, timeout=20) as r:
            if r.status == 200:
                return await r.text()
    except:
        return None
    return None


def parse_lead(html, detalle_url):
    soup = BeautifulSoup(html, "html.parser")
    root = soup.select_one("#datosContacto")
    if not root:
        return None

    data = {
        "name": None,
        "phone": None,
        "email": None,
        "website": None,
        "website_type": None,
        "website_status": None,
        "detalle_url": detalle_url,
        "redes_sociales": {},
        "logo_url": None,
        "rubros": [],
    }

    # Nombre
    name = root.select_one(".search-result-name h1")
    if name:
        data["name"] = name.get_text(strip=True)

    # Teléfono
    tel = root.select_one("a[href^='tel:']")
    if tel:
        data["phone"] = tel.get_text(strip=True)

    # Email
    email = root.select_one("a[href^='mailto:']")
    if email:
        data["email"] = email.get_text(strip=True)
    else:
        # Intentar extraer de texto visible
        text_email = root.find(string=lambda t: t and "@" in t)
        if text_email:
            data["email"] = text_email.strip()

    # Website real
    for a in root.select("a.search-result-link[target='_blank']"):
        href = a.get("href", "").lower()
        if href.startswith("http") and "guiacores" not in href and "whatsapp" not in href:
            data["website"] = href
            break

    # Clasificación website
    w = data["website"]
    if w:
        if "facebook.com" in w:
            data["website_type"] = "FACEBOOK"
            data["website_status"] = "SOCIAL"
        elif "instagram.com" in w:
            data["website_type"] = "INSTAGRAM"
            data["website_status"] = "SOCIAL"
        elif "linkedin.com" in w:
            data["website_type"] = "LINKEDIN"
            data["website_status"] = "SOCIAL"
        elif "linktr" in w:
            data["website_type"] = "LINKTR"
            data["website_status"] = "SOCIAL"
        else:
            data["website_type"] = "REGULAR"

    # Redes sociales
    redes = {}
    fb = root.select_one("a[href*='facebook']")
    if fb:
        redes["facebook"] = fb["href"]
    ig = root.select_one("a[href*='instagram']")
    if ig:
        redes["instagram"] = ig["href"]
    data["redes_sociales"] = redes

    # Logo
    logo_img = root.select_one("img[src*='upload/registro']")
    if logo_img:
        src = logo_img.get("src", "").strip()
        if src.startswith("/"):
            src = "https://www.guiacores.com.ar" + src
        data["logo_url"] = src

    # Rubros
    rubros = []
    for r in root.select(".rubros .items a.search-result-link"):
        rubros.append(r.get_text(strip=True))
    data["rubros"] = rubros

    return data


@sync_to_async
def save_lead(data):
    if not data or (not data.get("phone") and not data.get("email")):
        return None

    existing = None

    # Buscar por teléfono primero
    if data.get("phone"):
        existing = LeadFull.objects.filter(phone=data["phone"]).first()

    # Si no hay por teléfono, buscar por email
    if not existing and data.get("email"):
        existing = LeadFull.objects.filter(email=data["email"]).first()

    # Si existe, actualizar solo campos válidos
    if existing:
        for key, value in data.items():
            if value is not None:
                # Protege website_status existente
                if key == "website_status" and existing.website_status is not None:
                    continue

                # Protege email si ya existe en otro lead
                if key == "email":
                    conflict = LeadFull.objects.filter(email=value).exclude(pk=existing.pk).exists()
                    if conflict:
                        continue  # no sobrescribir email

                setattr(existing, key, value)

        existing.save()
        return existing, False

    # Si no existe, crear nuevo lead
    # Evitamos crear si el email ya está en otro registro
    if data.get("email"):
        if LeadFull.objects.filter(email=data["email"]).exists():
            # Saltar creación porque ya existe email
            return None

    obj = LeadFull.objects.create(**data)
    return obj, True

async def scrape_id(session, url):
    html = await fetch_html(session, url)
    if not html:
        return None

    parsed = parse_lead(html, url)
    if not parsed:
        return None

    result = await save_lead(parsed)
    if result:
        obj, created = result
        print(f"{'CREADO' if created else 'ACTUALIZADO'} → {obj.phone or obj.email}")


async def loop_ids(start_id, end_id):
    async with aiohttp.ClientSession() as session:
        for x in range(start_id, end_id + 1):
            url = f"{BASE_URL}{x}"
            await scrape_id(session, url)


async def loop_queryset(objs):
    async with aiohttp.ClientSession() as session:
        for obj in objs:
            if not obj.detalle_url:
                print(f"❌ OBJ {obj.id} sin detalle_url, skip")
                continue
            await scrape_id(session, obj.detalle_url)


class Command(BaseCommand):
    help = "Scraper detalle Guía Cores (por IDs o queryset)"

    def add_arguments(self, parser):
        parser.add_argument("--start", type=int)
        parser.add_argument("--end", type=int)
        parser.add_argument("--iter", type=str, help="Queryset evaluable")

    def handle(self, *a, **opts):
        qs_expr = opts.get("iter")

        if qs_expr:
            print(f"➡ Ejecutando queryset: {qs_expr}")
            qs = list(eval(qs_expr))
            print(f"➡ Objetos cargados: {len(qs)}")
            asyncio.run(loop_queryset(qs))
            return

        start = opts.get("start")
        end = opts.get("end")

        if start is None:
            print("❌ Error: --start es obligatorio si no usás --iter")
            return

        if end is None:
            end = start

        print(f"➡ Scrapeando IDs {start} → {end}")
        asyncio.run(loop_ids(start, end))
