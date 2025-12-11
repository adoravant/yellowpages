import asyncio
from django.core.management.base import BaseCommand
from asgiref.sync import sync_to_async
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import re
from main.models import LeadFull


# ============================================================
# DETECTOR (igual que antes)
# ============================================================
def detect_stack(html: str, url: str = ""):
    soup = BeautifulSoup(html, "html.parser")
    text = html.lower()

    result = {
        "cms": None,
        "builder": None,
        "frameworks": [],
        "cdn": [],
        "server": None,
        "tags": [],
    }

    if "wp-content" in text or "wp-json" in text:
        result["cms"] = "WordPress"
    if "content=\"joomla!" in text:
        result["cms"] = "Joomla"
    if "sites/default/files" in text:
        result["cms"] = "Drupal"
    if "static.wixstatic.com" in text:
        result["cms"] = "Wix"
    if "squarespace.com" in text:
        result["cms"] = "Squarespace"
    if "tiendanube" in text or "nuvemshop" in text:
        result["cms"] = "Tienda Nube"

    scripts = [s.get("src", "").lower() for s in soup.find_all("script") if s.get("src")]
    links = [l.get("href", "").lower() for l in soup.find_all("link") if l.get("href")]
    all_assets = scripts + links

    if any("jquery" in a for a in all_assets):
        result["frameworks"].append("jQuery")
    if any("bootstrap" in a for a in all_assets):
        result["frameworks"].append("Bootstrap")
    if any("vue" in a for a in all_assets):
        result["frameworks"].append("Vue.js")
    if any("react" in a for a in all_assets):
        result["frameworks"].append("React")

    if any("cloudflare" in a for a in all_assets) or "cf-ray" in text:
        result["cdn"].append("Cloudflare")
    if any("cdn.jsdelivr.net" in a for a in all_assets):
        result["cdn"].append("jsDelivr")
    if any("cdnjs" in a for a in all_assets):
        result["cdn"].append("CDNJS")

    if "googletagmanager.com" in text:
        result["tags"].append("Google Tag Manager")
    if "gtag(" in text:
        result["tags"].append("Analytics GA4")
    if "analytics.js" in text:
        result["tags"].append("Analytics Universal")
    if "facebook.com/tr" in text:
        result["tags"].append("Facebook Pixel")
    if "hotjar.com" in text:
        result["tags"].append("Hotjar")

    if "wp-content" in text:
        result["server"] = "Apache/Nginx (WordPress)"
    if ".asp" in text or ".aspx" in text:
        result["server"] = "IIS (Windows)"

    return result


# ============================================================
# COMANDO
# ============================================================
class Command(BaseCommand):
    help = "Analiza el stack tecnológico: acepta --url o --iter QUERYSET"

    def add_arguments(self, parser):
        parser.add_argument("--url", help="URL única a analizar")
        parser.add_argument("--iter", help='Evalúa un queryset, ej: --iter "LeadFull.objects.filter(website_type=\'REGULAR\')"')

    async def fetch_html(self, url):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=20000)
                await page.wait_for_load_state("networkidle", timeout=15000)
                html = await page.content()
                final_url = page.url
            except Exception as e:
                await browser.close()
                return None, None, str(e)

            await browser.close()
            return html, final_url, None

    def print_report(self, obj_name, final_url, stack):
        self.stdout.write("---------------------------------------------------")
        self.stdout.write(f"🔍 Lead: {obj_name}")
        self.stdout.write(f"🌐 URL final: {final_url}\n")

        def line(label, value):
            v = value if value else "(no detectado)"
            self.stdout.write(f"{label}: {v}")

        line("CMS", stack["cms"])
        line("Builder", stack["builder"])
        line("Frameworks", ", ".join(stack["frameworks"]) or None)
        line("CDN", ", ".join(stack["cdn"]) or None)
        line("Server", stack["server"])
        line("Tags", ", ".join(stack["tags"]) or None)

        self.stdout.write("---------------------------------------------------\n")

    # ========================================================
    # MAIN
    # ========================================================
    def handle(self, *args, **opts):
        url = opts.get("url")
        queryset_str = opts.get("iter")

        if url and queryset_str:
            self.stdout.write("❌ Debes usar solo --url o solo --iter, no ambos.")
            return

        # ----------------------------------------
        # MODO 1: URL única
        # ----------------------------------------
        if url:
            if not url.startswith("http"):
                url = "https://" + url
            html, final_url, err = asyncio.run(self.fetch_html(url))

            if err:
                self.stdout.write(f"❌ Error cargando {url}: {err}")
                return

            stack = detect_stack(html)
            self.print_report(url, final_url, stack)
            return

        # ----------------------------------------
        # MODO 2: Queryset dinámico
        # ----------------------------------------
        if queryset_str:
            try:
                qs = eval(queryset_str, {"LeadFull": LeadFull})
            except Exception as e:
                self.stdout.write(f"❌ Error evaluando queryset: {e}")
                return

            count = qs.count()
            self.stdout.write(f"📌 Analizando {count} sitios...\n")

            for obj in qs:
                if not obj.website:
                    continue

                url = obj.website if obj.website.startswith("http") else "https://" + obj.website

                html, final_url, err = asyncio.run(self.fetch_html(url))
                if err or not html:
                    self.stdout.write(f"❌ {obj.website}: ERROR → {err}")
                    continue

                stack = detect_stack(html)
                name = getattr(obj, "name", obj.pk)
                self.print_report(name, final_url, stack)

            return

        self.stdout.write("❌ Debes usar --url o --iter.")
