import os
import logging
import urllib.parse

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")

INPUT_FILE = "dns_list.txt"
TEMPLATE_FILE = "DNS_for_Clash.meta_Template.yml"
OUTPUT_DIR = "Generated/Files"
README_DIR = "Generated"

DEFAULT_FALLBACK = [
    "8.8.8.8", "1.1.1.1", "9.9.9.9", "94.140.14.14",
    "2606:4700:4700::1111", "2001:4860:4860::8888"
]

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

def load_template_text():
    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        return f.read()

def replace_dns_section(template_text, section_name, dns_list):
    # Example: replace lines like "nameserver:" and its following list items
    start_marker = f"{section_name}:"
    lines = template_text.splitlines()
    new_lines = []
    in_section = False
    for line in lines:
        if line.strip().startswith(start_marker):
            new_lines.append(start_marker)
            for dns in dns_list:
                new_lines.append(f"  - {dns}")
            in_section = True
        elif in_section and (line.startswith(" ") or not line.strip()):
            # skip old DNS lines until next section
            continue
        else:
            in_section = False
            new_lines.append(line)
    return "\n".join(new_lines)

def replace_all_dns(template_text, entries, strict=False):
    ipv4 = list(dict.fromkeys(entries["ipv4"]))
    ipv6 = list(dict.fromkeys(entries["ipv6"]))
    doh = list(dict.fromkeys(entries["doh"]))
    dot = list(dict.fromkeys(entries["dot"]))
    host = list(dict.fromkeys(entries["hostname"]))
    fallback = entries["fallback"] if entries["fallback"] else DEFAULT_FALLBACK

    all_entries = ipv4 + ipv6 + doh + dot + host
    new_text = template_text

    if strict:
        new_text = replace_dns_section(new_text, "default-nameserver", ipv4 + ipv6)

    new_text = replace_dns_section(new_text, "nameserver", all_entries)
    new_text = replace_dns_section(new_text, "direct-nameserver", all_entries)
    new_text = replace_dns_section(new_text, "proxy-server-nameserver", all_entries)
    new_text = replace_dns_section(new_text, "fallback", fallback)

    return new_text

def save_config_text(provider, text, suffix):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_file = os.path.join(OUTPUT_DIR, f"{provider}_{suffix}.yml")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(text)
    return out_file

def generate_readme(files):
    lines = [
        "# 📂 Generated DNS Configs",
        "",
        "| Provider | Country | Normal | Strict | Fallback DNS |",
        "|----------|---------|--------|--------|--------------|",
    ]
    providers = parse_dns_list()
    grouped = {}
    for f in files:
        name = os.path.basename(f)
        provider, t = name.replace(".yml","").rsplit("_",1)
        grouped.setdefault(provider, {})[t] = f

    for provider, types in grouped.items():
        country = providers.get(provider, {}).get("country", "N/A")
        fallback_list = providers.get(provider, {}).get("fallback", []) or DEFAULT_FALLBACK
        fallback_str = ", ".join(fallback_list)

        repo = os.environ.get("GITHUB_REPOSITORY","OWNER/REPO")
        normal_url = strict_url = "N/A"

        if "Normal" in types:
            normal_name = os.path.basename(types["Normal"])
            normal_encoded = urllib.parse.quote(normal_name)
            normal_url = f"[Link](https://raw.githubusercontent.com/{repo}/main/{OUTPUT_DIR}/{normal_encoded})"

        if "Strict" in types:
            strict_name = os.path.basename(types["Strict"])
            strict_encoded = urllib.parse.quote(strict_name)
            strict_url = f"[Link](https://raw.githubusercontent.com/{repo}/main/{OUTPUT_DIR}/{strict_encoded})"

        lines.append(f"| {provider} | {country} | {normal_url} | {strict_url} | `{fallback_str}` |")

    os.makedirs(README_DIR, exist_ok=True)
    with open(os.path.join(README_DIR,"README.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def main():
    logging.info("🚀 Starting DNS config generation (copy-paste mode)...")
    providers = parse_dns_list()
    tpl_text = load_template_text()
    files = []

    for provider, entries in providers.items():
        logging.info(f"⚙️ Generating configs for provider: {provider}")

        normal_cfg = replace_all_dns(tpl_text, entries, strict=False)
        f1 = save_config_text(provider, normal_cfg, "Normal")
        files.append(f1)
        logging.info(f"✅ Normal config saved: {f1}")

        strict_cfg = replace_all_dns(tpl_text, entries, strict=True)
        f2 = save_config_text(provider, strict_cfg, "Strict")
        files.append(f2)
        logging.info(f"✅ Strict config saved: {f2}")

    generate_readme(files)
    logging.info("📄 README.md generated inside Generated/")

if __name__ == "__main__":
    main()
