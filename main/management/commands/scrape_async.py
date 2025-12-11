# main/management/commands/scrape_playwright_lotes.py
import asyncio
import re
from django.core.management.base import BaseCommand
from main.models import LeadFull
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from asgiref.sync import sync_to_async

class Command(BaseCommand):
    help = "Scraper async de Guia Cores con Playwright, procesando páginas en lotes"

    def handle(self, *args, **options):
        asyncio.run(self.scrape_all_pages())

    async def scrape_all_pages(self):
        base_url = "https://www.guiacores.com.ar/index.php?r=search/index&b=&R=&L=&NTtc=1&idb="
        page_number = 624
        scraped_count = 0
        total_results = None
        lote_size = 10  # cantidad de páginas a procesar antes de limpiar memoria

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            while True:
                lote_start = page_number
                lote_end = page_number + lote_size - 1

                for pn in range(lote_start, lote_end + 1):
                    url = f"{base_url}&page={pn}"
                    try:
                        await page.goto(url, timeout=30000)
                        await page.wait_for_selector("div.card-mobile.gc-item", timeout=10000)
                    except Exception:
                        self.stdout.write(f"No se pudo cargar la página {pn}. Se saltea.")
                        continue

                    html = await page.content()
                    soup = BeautifulSoup(html, "html.parser")

                    # Total resultados si no lo tenemos
                    if total_results is None:
                        total_div = soup.find("div", class_="col-sm-12")
                        if total_div:
                            match = re.search(r"ha generado\s+([\d\.]+)", total_div.text)
                            if match:
                                total_results = int(match.group(1).replace(".", ""))
                                self.stdout.write(f"Total resultados estimados: {total_results}")

                    cards = soup.select("div.card-mobile.gc-item")
                    page_scraped = 0

                    for card in cards:
                        datos = card.find("div", class_=lambda x: x and "datos" in x)
                        botones = card.find("div", class_=lambda x: x and "botones" in x)

                        if not datos or not botones:
                            continue  # no hay warning, solo se ignoran

                        # Nombre y detalle URL
                        nombre_tag = datos.select_one("span.nombre-comercio a")
                        nombre_comercio = nombre_tag.text.strip() if nombre_tag else None
                        detalle_url = f"https://www.guiacores.com.ar/index.php{nombre_tag['href']}" if nombre_tag else None

                        # Dirección
                        street_tag = datos.select_one("span[itemprop='streetAddress']")
                        street_address = street_tag.text.strip() if street_tag else None

                        # Teléfono y WhatsApp
                        whatsapp_tags = datos.select("a.search-result-link")
                        whatsapp_url, phone = None, None
                        for tag in whatsapp_tags:
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

                        # Guardar en DB de forma asincrónica
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
                        page_scraped += 1

                    self.stdout.write(f"Página {pn}: {page_scraped} cards extraídas (total scrapeadas: {scraped_count})")

                    if total_results and scraped_count >= total_results:
                        break

                # Limpiar memoria del page cada lote
                await page.close()
                page = await browser.new_page()
                page_number += lote_size

                if total_results and scraped_count >= total_results:
                    break

            await browser.close()
            self.stdout.write("Scraper finalizado.")
