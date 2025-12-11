# main/management/commands/urls_v1.py

import asyncio
from asgiref.sync import sync_to_async
from django.core.management.base import BaseCommand
from playwright.async_api import async_playwright
from main.models import LeadFull


class Command(BaseCommand):
    help = "Revisa LeadFull con website y detecta Guía Cores, guardando resultados."

    def add_arguments(self, parser):
        parser.add_argument("--url", type=str, help="URL individual a revisar")

    # ---------------------------
    # SAFE SELECTOR
    # ---------------------------
    async def safe_query(self, page, selector):
        try:
            return await page.query_selector(selector)
        except:
            return None

    # ---------------------------
    # FULL LOAD
    # ---------------------------
    async def full_load(self, page):
        for state in ["load", "networkidle"]:
            try:
                await page.wait_for_load_state(state, timeout=15000)
            except:
                pass
        await page.wait_for_timeout(1500)

    # ---------------------------
    # MAIN
    # ---------------------------
    async def run_check(self, single_url=None):

        if single_url:
            leads = [LeadFull(website=single_url)]
            self.stdout.write(f"🔎 Chequeando URL individual: {single_url}\n")

        else:
            queryset = LeadFull.objects.filter(
                website__isnull=False
            ).exclude(website__exact="").exclude(
                website__contains="guiacores"
            ).exclude(
                website__contains="facebook"
            ).filter(website_status="NO_CORES")

            leads = await sync_to_async(list)(queryset)
            self.stdout.write(f"🔎 Chequeando {len(leads)} sitios...\n")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()

            for lead in leads:

                url = (lead.website or "").strip()
                if not url:
                    continue

                if not url.startswith("http"):
                    url = "https://" + url

                page = await context.new_page()
                self.stdout.write(f"➡ {url}")

                # ---------------------------
                # INTENTO DE LOAD
                # ---------------------------
                try:
                    await page.goto(url, wait_until="domcontentloaded", timeout=20000)
                    await self.full_load(page)

                except Exception as e:
                    self.stdout.write(f"   ❌ ERROR LOAD: {e}")
                    self.stdout.write(f"   → website_status = ERROR (GUARDADO)")

                    if lead.pk:
                        lead.website_status = "ERROR"
                        await sync_to_async(lead.save)(update_fields=["website_status"])

                    await page.close()
                    continue

                # ---------------------------
                # DETECCIÓN CORES
                # ---------------------------
                logo = await self.safe_query(
                    page,
                    "img[src*='logo-cores'], img[src*='cores-150'], img[src*='logo_cores']"
                )

                link = await self.safe_query(
                    page,
                    "a[href*='cores.com.ar/paginas-web']"
                )

                text = await self.safe_query(
                    page,
                    "text=/Gu[ií]a Cores/"
                )

                found = bool(logo or link or text)

                self.stdout.write(f"   ✔ Encontrado CORES: {found}")
                self.stdout.write(f"   🌐 URL final: {page.url}")

                # ---------------------------
                # GUARDADO DB
                # ---------------------------
                if lead.pk:
                    lead.website_status = "CORES" if found else "NO_CORES"
                    await sync_to_async(lead.save)(update_fields=["website_status"])

                await page.close()

            await browser.close()

        self.stdout.write("\n✅ Finalizado (resultados GUARDADOS).\n")

    # ---------------------------
    # HANDLE
    # ---------------------------
    def handle(self, *a, **opts):
        asyncio.run(self.run_check(opts.get("url")))
