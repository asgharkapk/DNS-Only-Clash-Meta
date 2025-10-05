import os
import yaml
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")

INPUT_FILE = "dns_list.txt"
TEMPLATE_FILE = "DNS_for_Clash.meta_Template.yml"
OUTPUT_DIR = "Generated"

DEFAULT_FALLBACK = [
    "8.8.8.8", "1.1.1.1", "9.9.9.9", "94.140.14.14",
    "2606:4700:4700::1111", "2001:4860:4860::8888"
]

def add_fallback(dns_cfg, entries):
    fallback = entries["fallback"] if entries["fallback"] else DEFAULT_FALLBACK
    dns_cfg["dns"]["fallback"] = fallback
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
            elif dtype in providers[provider]:
                providers[provider][dtype].append(value)
            else:
                logging.warning(f"⚠️ Unknown dtype '{dtype}' in line: {line}")
    return providers

def load_template():
    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def save_config(provider, data, suffix):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_file = os.path.join(OUTPUT_DIR, f"{provider}_{suffix}.yml")
    with open(out_file, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False)
    return out_file

def generate_readme(files):
    lines = [
        "# 📂 Generated DNS Configs",
        "",
        "These configs were automatically generated from **dns_list.txt** using the template `DNS_for_Clash.meta_Template.yml`.",
        "",
        "## ℹ️ How it works",
        "- **Normal configs** → Replace only `nameserver` and `proxy-server-nameserver`.",
        "- **Strict configs** → Replace *all* DNS fields (`default-nameserver`, `nameserver`, `direct-nameserver`, `proxy-server-nameserver`).",
        "- **Fallback** → If a provider defines `fallback` entries in `dns_list.txt`, those are used. Otherwise, a default global fallback list is applied.",
        "- **Country** → Each provider can define its main host country with a `country` entry.",
        "",
        "## 📜 Available configs",
        "| Provider | Country | Type | Raw Link | Fallback DNS | Description |",
        "|----------|---------|------|----------|--------------|-------------|",
    ]

    # build a map of provider -> fallback list from dns_list.txt
    providers = parse_dns_list()

    for f in files:
        name = os.path.basename(f)
        provider, t = name.replace(".yml","").rsplit("_",1)
        repo = os.environ.get("GITHUB_REPOSITORY","OWNER/REPO")
        url = f"https://raw.githubusercontent.com/{repo}/main/{OUTPUT_DIR}/{name}"
        desc = "Basic DNS replacement" if t == "Normal" else "Full strict DNS replacement"
        fallback_list = providers.get(provider, {}).get("fallback", [])
        if not fallback_list:
            fallback_list = DEFAULT_FALLBACK
        fallback_str = ", ".join(fallback_list)
        country = providers.get(provider, {}).get("country", "N/A")
        lines.append(f"| {provider} | {country} | {t} | [Link]({url}) | `{fallback_str}` | {desc} |")

    lines.append("\n---\n✅ Generated automatically. Do not edit manually.")
    with open(os.path.join(OUTPUT_DIR,"README.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def main():
    logging.info("🚀 Starting DNS config generation...")
    providers = parse_dns_list()
    logging.info(f"📑 Found {len(providers)} providers in dns_list.txt")

    files = []
    for provider, entries in providers.items():
        logging.info(f"⚙️ Generating configs for provider: {provider}")
        tpl = load_template()

        # Normal config
        normal_cfg = tpl.copy()
        normal_cfg["dns"]["nameserver"] = entries["ipv4"] + entries["ipv6"] + entries["doh"] + entries["dot"] + entries["hostname"]
        normal_cfg["dns"]["proxy-server-nameserver"] = entries["ipv4"] + entries["ipv6"]
        normal_cfg = add_fallback(normal_cfg, entries)
        f1 = save_config(provider, normal_cfg, "Normal")
        files.append(f1)
        logging.info(f"✅ Normal config saved: {f1}")

        # Strict config
        strict_cfg = tpl.copy()
        all_entries = entries["ipv4"] + entries["ipv6"] + entries["doh"] + entries["dot"] + entries["hostname"]
        strict_cfg["dns"]["default-nameserver"] = entries["ipv4"] + entries["ipv6"]
        strict_cfg["dns"]["nameserver"] = all_entries
        strict_cfg["dns"]["direct-nameserver"] = entries["ipv4"] + entries["ipv6"]
        strict_cfg["dns"]["proxy-server-nameserver"] = entries["ipv4"] + entries["ipv6"]
        strict_cfg = add_fallback(strict_cfg, entries)   # ✅ fixed
        f2 = save_config(provider, strict_cfg, "Strict")
        files.append(f2)
        logging.info(f"✅ Strict config saved: {f2}")

    generate_readme(files)
    logging.info("📄 README.md generated inside Generated/")

if __name__ == "__main__":
    main()
