import asyncio
from django.core.management.base import BaseCommand
from playwright.async_api import async_playwright
from asgiref.sync import sync_to_async
from main.models import LeadFull


class Command(BaseCommand):
    help = "Chequea URLs y clasifica: DOWN / SSL_ERROR / TIMEOUT / OK — guarda solo website_status"

    # ------------------------------------------------------
    # ARGUMENTOS
    # ------------------------------------------------------
    def add_arguments(self, parser):
        parser.add_argument("--url", type=str, help="Chequea una única URL")
        parser.add_argument("--iter", action="store_true", help="Iterar queryset por defecto")

    # ------------------------------------------------------
    # SAFE CHECK
    # ------------------------------------------------------
    async def safe_check(self, browser, url):
        context = await browser.new_context(ignore_https_errors=False)
        page = await context.new_page()

        if not url.startswith("http"):
            url = "https://" + url

        try:
            response = await page.goto(url, wait_until="domcontentloaded", timeout=12000)
        except Exception as e:
            msg = str(e).lower()
            await context.close()
            if "timeout" in msg:
                return "TIMEOUT"
            if "ssl" in msg or "cert" in msg:
                return "SSL_ERROR"
            return "DOWN"

        if response is None or response.status >= 500:
            await context.close()
            return "DOWN"

        ssl_selectors = [
            "#main-message",
            "#error-code",
            "text=Your connection is not private",
            "text=Tu conexión no es privada",
            "text=NET::ERR_CERT",
            "text=ERR_CERT",
        ]

        for sel in ssl_selectors:
            try:
                if await page.query_selector(sel):
                    await context.close()
                    return "SSL_ERROR"
            except:
                pass

        try:
            await page.wait_for_load_state("networkidle", timeout=6000)
        except:
            pass

        html = await page.content()
        await context.close()

        if len(html) < 200:
            return "DOWN"

        return "OK"

    # ------------------------------------------------------
    # QUERYSET
    # ------------------------------------------------------
    @sync_to_async
    def get_queryset(self):
        return list(
            LeadFull.objects.filter(
                website_status="ERROR",
                website__isnull=False
            ).exclude(website="")
        )

    # ------------------------------------------------------
    # GUARDADO
    # ------------------------------------------------------
    @sync_to_async
    def update_status(self, lead_id, status):
        LeadFull.objects.filter(id=lead_id).update(website_status=status)

    # ------------------------------------------------------
    # MAIN
    # ------------------------------------------------------
    async def run(self, url=None, iterate=False):

        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)

            if url:
                result = await self.safe_check(browser, url)
                print(f"\n🔎 {url} ➜ {result}\n")
                await self.update_status_by_url(url, result)
                await browser.close()
                return

            if iterate:
                qs = await self.get_queryset()
                total = len(qs)
                print(f"\n🔎 Iterando {total} sitios con website_status='ERROR'...\n")

                for lead in qs:
                    url = lead.website.strip()
                    print(f"➡ {url}")

                    try:
                        result = await self.safe_check(browser, url)
                    except Exception as e:
                        print(f"   ❌ ERROR → {e}")
                        result = "DOWN"

                    await self.update_status(lead.id, result)
                    print(f"   ➜ {result}\n")

            await browser.close()

    # ------------------------------------------------------
    # HANDLE
    # ------------------------------------------------------
    def handle(self, *args, **opts):
        url = opts.get("url")
        iterate = opts.get("iter")
        asyncio.run(self.run(url=url, iterate=iterate))
