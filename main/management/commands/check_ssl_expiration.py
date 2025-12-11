import ssl
from datetime import datetime
from cryptography import x509
from cryptography.hazmat.backends import default_backend

from django.core.management.base import BaseCommand


def normalize_url(raw_url: str) -> str:
    url = raw_url.strip()
    if url.startswith("http://"):
        url = url[7:]
    elif url.startswith("https://"):
        url = url[8:]
    if not url.startswith("www."):
        url = "www." + url
    return "https://" + url


def get_ssl_expiry_cryptography(hostname: str, port: int = 443):
    # Obtener certificado crudo en PEM
    cert_pem = ssl.get_server_certificate((hostname, port))
    
    # Parsear con cryptography
    cert = x509.load_pem_x509_certificate(cert_pem.encode(), default_backend())

    not_before = cert.not_valid_before
    not_after = cert.not_valid_after
    days_left = (not_after - datetime.utcnow()).days

    return {
        "valid_from": not_before,
        "valid_until": not_after,
        "days_left": days_left
    }


class Command(BaseCommand):
    help = "Verifica SSL de un dominio individual y normaliza URL a https://www.dominio"

    def add_arguments(self, parser):
        parser.add_argument("url", type=str, help="Dominio o URL a verificar")

    def handle(self, *args, **options):
        raw_url = options["url"]
        final_url = normalize_url(raw_url)

        # Extraer hostname sin https:// para ssl
        hostname = final_url.replace("https://", "")

        try:
            info = get_ssl_expiry_cryptography(hostname)
            self.stdout.write(f"URL final: {final_url}")
            self.stdout.write(f"valid_from : {info['valid_from']}")
            self.stdout.write(f"valid_until: {info['valid_until']}")
            self.stdout.write(f"days_left  : {info['days_left']}")
        except Exception as e:
            self.stdout.write(f"Error al obtener SSL para {final_url}: {type(e).__name__} {e}")

