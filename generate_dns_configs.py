import yaml
import os
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")

INPUT_FILE = "dns_list.txt"
TEMPLATE_FILE = "DNS_for_Clash.meta_Template.yml"
OUTPUT_FILE = "DNS_for_Clash.meta_Output.yml"

TARGET_KEYS = [
    "default-nameserver",
    "nameserver",
    "direct-nameserver",
    "proxy-server-nameserver",
    "fallback",
]

def load_dns_list(path):
    """Load lines from dns_list.txt, stripping whitespace and ignoring empties."""
    with open(path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    return lines

def replace_dns_sections(template_path, output_path, new_dns_list):
    """Replace only the 5 target DNS keys in the YAML file."""
    with open(template_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    for key in TARGET_KEYS:
        if key in data:
            logging.info(f"Replacing {key} → {len(new_dns_list)} entries")
            data[key] = new_dns_list
        else:
            logging.warning(f"{key} not found in template (skipped)")

    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, sort_keys=False, allow_unicode=True)

    logging.info(f"✅ DNS replacement complete → {output_path}")

if __name__ == "__main__":
    if not os.path.exists(TEMPLATE_FILE):
        raise FileNotFoundError(f"Template file not found: {TEMPLATE_FILE}")
    if not os.path.exists(INPUT_FILE):
        raise FileNotFoundError(f"DNS list file not found: {INPUT_FILE}")

    dns_list = load_dns_list(INPUT_FILE)
    replace_dns_sections(TEMPLATE_FILE, OUTPUT_FILE, dns_list)
