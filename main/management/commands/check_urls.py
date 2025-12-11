# main/management/commands/check_cores_all.py
import asyncio
from asgiref.sync import sync_to_async
from django.core.management.base import BaseCommand
from playwright.async_api import async_playwright
from main.models import LeadFull

#https://www.habitataberturas.com.ar/ rota
#https://www.mundobulonpatagonia.com.ar/ SSL


class Command(BaseCommand):
    help = "Revisa todos los LeadFull con website para detectar si usan Guía Cores."

    def handle(self, *args, **options):
        asyncio.run(self.run_check())

    async def page_fully_loaded(self, page):
        """Garantiza carga COMPLETA más allá del DOM."""
        try:
            await page.wait_for_load_state("load", timeout=20000)
        except:
            pass

        try:
            await page.wait_for_load_state("networkidle", timeout=15000)
        except:
            pass

        # estabilidad visual por 2 segundos para contenido dinámico
        try:
            await page.wait_for_selector("body", timeout=8000)
            await page.wait_for_timeout(2000)
        except:
            pass

    async def run_check(self):
        leads = await sync_to_async(list)(
            LeadFull.objects.exclude(website__isnull=True).exclude(website="").filter(website_status="NO_CORES"))

        self.stdout.write(f"\n🔎 Verificando {len(leads)} sitios...\n")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()

            for lead in leads:
                original_url = lead.website.strip()
                url = original_url if original_url.startswith("http") else f"https://{original_url}"

                self.stdout.write(f"➡ Revisando: {url}")
                page = await context.new_page()

                # ======= Navegación =======
                try:
                    await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                    await self.page_fully_loaded(page)

                except Exception as e:
                    self.stdout.write(f"   ❌ Error al cargar: {e}")
                    await page.close()
                    continue

                # ======= Detectar link de Guía Cores =======
                cores_link = await page.query_selector(
                    "a[href='https://cores.com.ar/paginas-web'], "
                    "a[href='http://cores.com.ar/paginas-web'], "
                    "a[href='https://www.cores.com.ar/paginas-web']"
                )

                # ======= Detectar logo de Guía Cores (flexible) =======
                cores_logo = await page.query_selector(
                    "img[src*='logo-cores'], img[src*='cores-150'], img[src*='cores'], img[src*='logo_cores']"
                )

                found = bool(cores_link or cores_logo)

                self.stdout.write(f"   ✔ Guía Cores encontrado: {found}")
                self.stdout.write(f"   🌐 URL final: {page.url}")

                if cores_logo:
                    src = await cores_logo.get_attribute("src")
                    self.stdout.write(f"   🖼 Logo detectado en: {src}")

                self.stdout.write("\n")

                # ======= Guardar resultado =======
                lead.website_status = "CORES" if found else "NO_CORES"
                await sync_to_async(lead.save)(update_fields=["website_status"])

                await page.close()

            await browser.close()

        self.stdout.write("\n✅ Finalizado con detección de link + logo y carga completa.\n")
