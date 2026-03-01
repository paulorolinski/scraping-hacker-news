# resolução do país
import re
import time
import requests
import pycountry
from bs4 import BeautifulSoup

country_cache = {}


def get_country_code(country_name):
    """Converte o nome do país para a sigla"""
    if not country_name or country_name == "Unknown":
        return "Unknown"

    # Remove qualquer coisa entre parênteses (ex: "Cayman Islands (the)" → "Cayman Islands")
    clean_name = re.sub(r'\s*\([^)]*\)', '', country_name).strip()
    cn_upper = clean_name.upper()

    # validação de nomes ambíguos no pycountry
    if "UNITED STATES" in cn_upper: return "US"
    if "UNITED KINGDOM" in cn_upper: return "GB"
    if "MOLDOVA"        in cn_upper: return "MD"

    try:
        country = pycountry.countries.get(name=clean_name)
        if country: return country.alpha_2

        country = pycountry.countries.get(official_name=clean_name)
        if country: return country.alpha_2

        results = pycountry.countries.search_fuzzy(clean_name)
        if results: return results[0].alpha_2
    except Exception:
        pass

    return "Unknown"


def get_domain_country(tld):
    """Consulta a IANA para descobrir o país associado ao TLD"""
    clean_tld = tld.split('.')[-1].lower()

    if not clean_tld:
        return "Unknown"
    if clean_tld in country_cache:
        return country_cache[clean_tld]

    try:
        url = f"https://www.iana.org/whois?q={clean_tld}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        pre_tag = soup.find('pre')
        text_to_search = pre_tag.text if pre_tag else response.text

        country_full_name = _extract_country_from_iana(text_to_search)
        country_code = get_country_code(country_full_name)

        # ccTLDs de 2 letras são o próprio código do país
        if country_code == "Unknown" and len(clean_tld) == 2:
            country_code = clean_tld.upper()

        country_cache[clean_tld] = country_code
        time.sleep(1)
        return country_code

    except Exception:
        if len(clean_tld) == 2:
            return clean_tld.upper()
        return "Unknown"


def _extract_country_from_iana(text):
    """Extrai o nome do país da última linha de endereço no bloco de organização"""
    blocks = re.split(r'\r?\n\s*\r?\n', text)
    for block in blocks:
        if 'organisation:' in block and 'address:' in block:
            address_lines = re.findall(r'address:\s+(.+)', block, re.IGNORECASE)
            if address_lines:
                return address_lines[-1].strip()
    return "Unknown"
