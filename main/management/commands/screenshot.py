import os
import asyncio
import subprocess
from urllib.parse import urlparse

from django.core.management.base import BaseCommand
from django.conf import settings
from asgiref.sync import sync_to_async

from playwright.async_api import async_playwright
from main.models import LeadFull


def extract_domain(url: str) -> str:
    parsed = urlparse(url)
    host = parsed.netloc or parsed.path
    host = host.replace("www.", "")
    return host.split(":")[0]


class Command(BaseCommand):
    help = "Chequea LeadFull(website_status=ERROR) y captura pantallas incluso de errores SSL usando Xvfb + Chrome (con zoom)."

    async def capture_with_xvfb(self, url: str, output_png: str):
        """
        Levanta Xvfb, lanza Chrome headful dentro del DISPLAY, aplica zoom por DPI+scale,
        espera a que pinte y captura el framebuffer con ffmpeg.
        """

        # eliminar si existe
        if os.path.exists(output_png):
            try:
                os.remove(output_png)
            except Exception:
                pass

        display = ":99"
        xvfb_proc = None
        browser = None

        try:
            # 🔥 Iniciar Xvfb con DPI alto para zoom real
            xvfb_proc = subprocess.Popen(
                [
                    "Xvfb", display,
                    "-screen", "0",
                    "1920x1080x24",
                    "-dpi", "180"   # ajustar si querés más/menos
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            # pequeño delay para que Xvfb arranque
            await asyncio.sleep(0.6)

            env = os.environ.copy()
            env["DISPLAY"] = display

            async with async_playwright() as pw:
                # Lanzar Chromium en modo headful dentro del DISPLAY virtual
                browser = await pw.chromium.launch(
                    headless=False,
                    args=[
                        "--start-maximized",
                        "--force-device-scale-factor=1.7",  # escala global (ajustable)
                        "--high-dpi-support=1",
                        "--ozone-platform=x11",
                        "--noerrdialogs",
                        "--disable-infobars",
                        "--allow-insecure-localhost",
                        "--disable-features=IsolateOrigins,site-per-process",
                    ],
                    env=env,
                )

                context = await browser.new_context(
                    viewport={"width": 1080, "height": 720},
                    locale="es-AR",
                    ignore_https_errors=False,  # necesario para que Chrome muestre la interstitial SSL
                )

                page = await context.new_page()

                # Intento de navegación; si falla, igual esperamos para que Chrome pinte interstitial
                try:
                    await page.goto(url, wait_until="commit", timeout=6000)
                except Exception:
                    # navegación fallida: dejamos que Chrome muestre lo que tenga
                    pass

                # Espera progresiva para que pinte completo (media - 1.5s)
                for ms in (500, 700, 1000, 1500):
                    await page.wait_for_timeout(ms)

                # Captura framebuffer con ffmpeg (1 frame)
                ffmpeg_cmd = [
                    "ffmpeg", "-y",
                    "-f", "x11grab",
                    "-video_size", "1920x1080",
                    "-i", f"{display}.0",
                    "-vframes", "1",
                    output_png,
                ]

                # Ejecutar ffmpeg silenciosamente (no lanzar excepción si falla; lo informamos)
                try:
                    subprocess.run(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
                except Exception:
                    # no queremos que falle el flujo completo si ffmpeg tiene problema
                    pass

                # cerrar context + browser
                try:
                    await context.close()
                except Exception:
                    pass

                try:
                    await browser.close()
                except Exception:
                    pass

        finally:
            # asegurar cierre de browser si quedó abierto
            try:
                if browser:
                    await browser.close()
            except Exception:
                pass

            # matar Xvfb
            if xvfb_proc:
                try:
                    xvfb_proc.kill()
                except Exception:
                    pass

    async def run_check(self):
        # Query asíncrono de LeadFull
        queryset = LeadFull.objects.filter(website_status="ERROR").exclude(website=None)
        leads = await sync_to_async(list)(queryset)

        screenshot_dir = os.path.join(settings.BASE_DIR, "screenshots")
        os.makedirs(screenshot_dir, exist_ok=True)

        self.stdout.write(f"\n🔎 Procesando {len(leads)} sitios (LeadFull)...")

        for lead in leads:
            raw = (lead.website or "").strip()
            if not raw:
                continue

            url = raw if raw.startswith(("http://", "https://")) else ("https://" + raw)
            domain = extract_domain(url)
            safe_name = domain or raw.replace("https://", "").replace("http://", "").replace("/", "_")
            output_png = os.path.join(screenshot_dir, f"{safe_name}.png")

            self.stdout.write(f"➡ Capturando: {url}")

            try:
                await self.capture_with_xvfb(url, output_png)
                self.stdout.write(f"   ✔ Guardado en: {output_png}\n")
            except Exception as e:
                self.stdout.write(f"   ❌ Error al capturar {url}: {type(e).__name__} {e}\n")

        self.stdout.write("🎉 Finalizado.\n")

    def handle(self, *args, **options):
        asyncio.run(self.run_check())
