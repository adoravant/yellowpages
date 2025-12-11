# main/management/commands/scrape_playwright.py
import asyncio
import re
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from main.models import LeadFull
from asgiref.sync import sync_to_async
from playwright.async_api import async_playwright

class Command(BaseCommand):
    help = "Scraper async de Guia Cores con Playwright"

    def handle(self, *args, **options):
        asyncio.run(self.scrape())

    async def scrape(self):
        base_url = "https://www.guiacores.com.ar/index.php?r=search/index&b=&R=&L=&NTtc=1&idb="
        page_number = 740
        scraped_count = 0
        total_results = None

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            while True:
                url = f"{base_url}&page={page_number}"
                await page.goto(url)
                self.stdout.write(f"Cargando página {page_number}...")

                # Esperar que carguen las cards
                try:
                    await page.wait_for_selector("div.card-mobile.gc-item", timeout=20000)
                except:
                    self.stdout.write(f"No se encontraron cards en la página {page_number}. Fin.")
                    break

                html = await page.content()
                soup = BeautifulSoup(html, "html.parser")

                # Extraer total de resultados si no lo tenemos
                if total_results is None:
                    total_div = soup.find("div", class_="col-sm-12")
                    if total_div:
                        match = re.search(r"ha generado\s+([\d\.]+)", total_div.text)
                        if match:
                            total_results = int(match.group(1).replace(".", ""))
                            self.stdout.write(f"Total resultados estimados: {total_results}")

                cards = soup.select("div.card-mobile.gc-item")
                if not cards:
                    break

                for card in cards:
                    datos = card.select_one("div.datos")
                    botones = card.select_one("div.botones")
                    if not datos or not botones:
                        self.stdout.write("Card ignorada: falta 'datos' o 'botones'")
                        continue

                    # Nombre y detalle URL
                    nombre_tag = datos.select_one("span.nombre-comercio a")
                    nombre_comercio = nombre_tag.text.strip() if nombre_tag else None
                    detalle_url = f"https://www.guiacores.com.ar/index.php{nombre_tag['href']}" if nombre_tag else None

                    # Dirección
                    street_tag = datos.select_one("span[itemprop='streetAddress']")
                    street_address = street_tag.text.strip() if street_tag else None

                    # Teléfono y WhatsApp
                    whatsapp_tag = datos.select("a.search-result-link")
                    whatsapp_url = None
                    phone = None
                    for tag in whatsapp_tag:
                        href = tag.get("href", "")
                        if "api.whatsapp.com" in href:
                            whatsapp_url = href
                            phone_match = re.search(r'phone=(\d+)', href)
                            phone = phone_match.group(1) if phone_match else None
                            break
                        else:
                            phone = tag.text.strip()
                            whatsapp_url = href
                            break

                    # Horario
                    opening_tag = datos.select_one("a[data-original-title]")
                    opening_hours = opening_tag['data-original-title'].replace("&lt;br&gt;", " ") if opening_tag else None

                    # Logo
                    logo_tag = datos.select_one("img.img-logo-card")
                    logo_url = logo_tag['src'].strip() if logo_tag else None

                    # Rating
                    rating_icons = datos.select("i.fas.fa-star")
                    rating = len(rating_icons) if rating_icons else 0

                    # Website (botones)
                    website_tag = botones.select_one("a.icono-web")
                    website = website_tag['href'].strip() if website_tag else None

                    # Guardar o actualizar en la DB usando sync_to_async
                    await sync_to_async(LeadFull.objects.update_or_create)(
                        phone=phone or f"NO-WEB-{scraped_count}",
                        defaults={
                            'name': nombre_comercio,
                            'phone_type': "WHATSAPP" if whatsapp_url else "REGULAR",
                            'country': "ARGENTINA",
                            'city': "NEUQUEN",
                            'state': "NQ",
                            'website': website,
                            'detalle_url': detalle_url,
                            'street_address': street_address,
                            'whatsapp_url': whatsapp_url,
                            'opening_hours': opening_hours,
                            'logo_url': logo_url,
                            'rating': rating,
                        }
                    )
                    scraped_count += 1

                self.stdout.write(f"Página {page_number} procesada, total scrapeados: {scraped_count}")

                # Si alcanzamos el total de resultados, salimos
                if total_results and scraped_count >= total_results:
                    break

                page_number += 1

            await browser.close()
            self.stdout.write("Scraper finalizado.")
