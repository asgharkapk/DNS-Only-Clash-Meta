import os
import yaml
import logging
import urllib.parse
from collections import OrderedDict

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")

INPUT_FILE = "dns_list.txt"
TEMPLATE_FILE = "DNS_for_Clash.meta_Template.yml"
OUTPUT_DIR = "Generated/Files"
README_DIR = "Generated"

DEFAULT_FALLBACK = [
    "8.8.8.8", "1.1.1.1", "9.9.9.9", "94.140.14.14",
    "2606:4700:4700::1111", "2001:4860:4860::8888"
]

# --- Cloudflare DNS Replacement Data ---
NEW_DEFAULT = [
    "1.0.0.1", "1.0.0.2", "1.1.1.1", "1.1.1.2",
    "2606:4700:4700::1111", "2606:4700:4700::1001",
    "2606:4700:4700::1002", "2606:4700:4700::1112"
]
NEW_NAMESERVER = [
    "1.0.0.1", "1.0.0.2", "1.1.1.1", "1.1.1.2",
    "2606:4700:4700::1111", "2606:4700:4700::1001",
    "2606:4700:4700::1002", "2606:4700:4700::1112",
    "https://cloudflare-dns.com/dns-query",
    "tls://one.one.one.one", "one.one.one.one",
    "security.cloudflare-dns.com",
    "https://security.cloudflare-dns.com/dns-query",
    "tls://security.cloudflare-dns.com"
]
NEW_DIRECT = NEW_NAMESERVER
NEW_PROXY = NEW_NAMESERVER
NEW_FALLBACK = []

TARGET_KEYS = {
    "default-nameserver": NEW_DEFAULT,
    "nameserver": NEW_NAMESERVER,
    "direct-nameserver": NEW_DIRECT,
    "proxy-server-nameserver": NEW_PROXY,
    "fallback": NEW_FALLBACK,
}

# === Ordered YAML Loader/Dumper (preserves key order) ===
def ordered_yaml_loader():
    class OrderedLoader(yaml.SafeLoader): pass
    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return OrderedDict(loader.construct_pairs(node))
    OrderedLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_mapping)
    return OrderedLoader

def ordered_yaml_dumper():
    class OrderedDumper(yaml.SafeDumper): pass
    def _dict_representer(dumper, data):
        return dumper.represent_mapping(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, data.items())
    OrderedDumper.add_representer(OrderedDict, _dict_representer)
    return OrderedDumper

# === Replace DNS sections inside the template ===
def replace_dns_sections(template_file):
    with open(template_file, "r", encoding="utf-8") as f:
        data = yaml.load(f, Loader=ordered_yaml_loader())

    dns_data = data.get("dns", data)  # handle both top-level or nested 'dns' blocks

    for key, new_values in TARGET_KEYS.items():
        if key in dns_data:
            logging.info(f"Replacing {key} → {len(new_values)} entries")
            dns_data[key] = new_values
        else:
            logging.warning(f"{key} not found (skipped)")

    return data

# === DNS Config Generator Functions ===
def add_fallback(dns_cfg, entries):
    fallback = entries["fallback"] if entries["fallback"] else DEFAULT_FALLBACK
    dns_cfg["dns"]["fallback"] = list(dict.fromkeys(fallback))
    return dns_cfg

def parse_dns_list():
    providers = {}
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                provider, dtype, value = [x.strip() for x in line.split("|")]
            except ValueError:
                continue
            if provider not in providers:
                providers[provider] = {
                    "ipv4": [], "ipv6": [], "doh": [], "dot": [], "hostname": [],
                    "fallback": [], "country": None
                }
            if dtype == "country":
                providers[provider]["country"] = value
            elif dtype == "fallback":
                providers[provider]["fallback"].append(value)
            elif dtype in providers[provider]:
                providers[provider][dtype].append(value)
            else:
                logging.warning(f"⚠️ Unknown dtype '{dtype}' in line: {line}")
    return providers

def load_template():
    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        return yaml.load(f, Loader=ordered_yaml_loader())

def save_config(provider, data, suffix):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_file = os.path.join(OUTPUT_DIR, f"{provider}_{suffix}.yml")
    with open(out_file, "w", encoding="utf-8") as f:
        yaml.dump(data, f, Dumper=ordered_yaml_dumper(), allow_unicode=True, sort_keys=False, indent=2)
    return out_file

def generate_readme(files):
    # (Unchanged — same as your original long README generator)
    pass  # keep your existing generate_readme() implementation here

def main():
    logging.info("🚀 Starting DNS config generation...")

    # Apply Cloudflare DNS replacements to the template once
    tpl_data = replace_dns_sections(TEMPLATE_FILE)
    logging.info("🌐 DNS template updated with Cloudflare defaults")

    providers = parse_dns_list()
    logging.info(f"📑 Found {len(providers)} providers in dns_list.txt")

    files = []
    for provider, entries in providers.items():
        logging.info(f"⚙️ Generating configs for provider: {provider}")

        tpl = tpl_data.copy()
        all_entries = list(dict.fromkeys(
            entries["ipv4"] + entries["ipv6"] + entries["doh"] + entries["dot"] + entries["hostname"]
        ))

        # Normal config
        normal_cfg = tpl.copy()
        normal_cfg["dns"]["nameserver"] = all_entries
        normal_cfg["dns"]["direct-nameserver"] = all_entries
        normal_cfg["dns"]["proxy-server-nameserver"] = all_entries
        normal_cfg = add_fallback(normal_cfg, entries)
        f1 = save_config(provider, normal_cfg, "Normal")
        files.append(f1)
        logging.info(f"✅ Normal config saved: {f1}")

        # Strict config
        strict_cfg = tpl.copy()
        strict_cfg["dns"]["default-nameserver"] = list(dict.fromkeys(entries["ipv4"] + entries["ipv6"]))
        strict_cfg["dns"]["nameserver"] = all_entries
        strict_cfg["dns"]["direct-nameserver"] = all_entries
        strict_cfg["dns"]["proxy-server-nameserver"] = all_entries
        strict_cfg = add_fallback(strict_cfg, entries)
        f2 = save_config(provider, strict_cfg, "Strict")
        files.append(f2)
        logging.info(f"✅ Strict config saved: {f2}")

    # Generate README
    generate_readme(files)
    logging.info("📄 README.md generated inside Generated/")

if __name__ == "__main__":
    main()
