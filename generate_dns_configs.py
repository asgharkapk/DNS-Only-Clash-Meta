import os
import yaml
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")

INPUT_FILE = "dns_list.txt"
TEMPLATE_FILE = "DNS_for_Clash.meta_Template.yml"
OUTPUT_DIR = "Generated"

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
                providers[provider] = {"ipv4": [], "ipv6": [], "doh": [], "dot": [], "hostname": []}
            providers[provider][dtype].append(value)
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
        "These configs were automatically generated from `dns_list.txt`.",
        "",
        "| Provider | Type | Raw Link |",
        "|----------|------|----------|",
    ]
    for f in files:
        name = os.path.basename(f)
        provider, t = name.replace(".yml","").rsplit("_",1)
        url = f"https://raw.githubusercontent.com/asgharkapk/DNS-Only-Clash-Meta/main/{OUTPUT_DIR}/{name}"
        lines.append(f"| {provider} | {t} | [Link]({url}) |")
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
        f2 = save_config(provider, strict_cfg, "Strict")
        files.append(f2)
        logging.info(f"✅ Strict config saved: {f2}")

    generate_readme(files)
    logging.info("📄 README.md generated inside Generated/")

if __name__ == "__main__":
    main()
