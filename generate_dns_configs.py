import os
import yaml
import logging
import urllib.parse
import copy
import re

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")

INPUT_FILE = "dns_list.txt"
TEMPLATE_FILE = "DNS_for_Clash.meta_Template.yml"
OUTPUT_DIR = "Generated/Files"
README_DIR = "Generated"

DEFAULT_FALLBACK = [
    "8.8.8.8", "1.1.1.1", "9.9.9.9", "94.140.14.14",
    "2606:4700:4700::1111", "2001:4860:4860::8888"
]


def sanitize_name(name: str) -> str:
    """Make a safe filename from provider name."""
    # remove anything that's not alnum, dash, underscore or dot and collapse spaces
    name = re.sub(r'\s+', '_', name.strip())
    name = re.sub(r'[^A-Za-z0-9_\-\.]', '', name)
    return name or "provider"


def dedupe_keep_order(seq):
    seen = set()
    out = []
    for x in seq:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def add_fallback(dns_cfg, entries):
    # entries["fallback"] should be a list (possibly empty)
    fb = entries.get("fallback", []) or DEFAULT_FALLBACK
    # ensure it's a list
    if isinstance(fb, str):
        fb = [fb]
    dns_cfg.setdefault("dns", {})
    dns_cfg["dns"]["fallback"] = dedupe_keep_order(fb)
    return dns_cfg


def parse_dns_list():
    providers = {}
    if not os.path.exists(INPUT_FILE):
        logging.warning(f"Input file '{INPUT_FILE}' not found.")
        return providers

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue

            # Split into exactly 3 parts: provider | dtype | value (value may contain pipes)
            parts = [p.strip() for p in line.split("|", 2)]
            if len(parts) < 3:
                logging.warning(f"Skipping malformed line: {line}")
                continue
            provider, dtype, value = parts
            dtype = dtype.lower()

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
    # dedupe lists
    for p, data in providers.items():
        for k in ("ipv4", "ipv6", "doh", "dot", "hostname", "fallback"):
            data[k] = dedupe_keep_order(data.get(k, []))
    return providers


def load_template():
    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_config(provider, data, suffix):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    safe_provider = sanitize_name(provider)
    out_file = os.path.join(OUTPUT_DIR, f"{safe_provider}_{suffix}.yml")
    # Use safe_dump with useful options: preserve insertion order, no key-sorting, readable block style
    with open(out_file, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True, default_flow_style=False)
    return out_file


def generate_readme(files):
    lines = [
        "# 📂 Generated DNS Configs",
        "",
        "This repository provides **automatically generated Clash.Meta DNS configurations**. ",
        "The configs are created from the input file **dns_list.txt** and a base template `DNS_for_Clash.meta_Template.yml`.",
        "",
        "## 📜 Available Configs",
        "",
        "| Provider | Country | Normal | Strict | Fallback DNS | Description |",
        "|----------|---------|--------|--------|--------------|-------------|",
    ]

    providers = parse_dns_list()

    grouped = {}
    for f in files:
        name = os.path.basename(f)
        # expect <provider>_<Suffix>.yml
        if "_" in name:
            provider_part, tpart = name.rsplit("_", 1)
            t = tpart.rsplit(".", 1)[0]
            # try to map sanitized provider back to original provider name if possible
            grouped.setdefault(provider_part, {})[t] = f
        else:
            grouped.setdefault(name, {})["file"] = f

    repo = os.environ.get("GITHUB_REPOSITORY", "OWNER/REPO")
    for provider_sanitized, types in grouped.items():
        # try find original provider from parsed providers by comparing sanitized names
        orig_provider = next((p for p in providers.keys() if sanitize_name(p) == provider_sanitized), provider_sanitized)
        country = providers.get(orig_provider, {}).get("country", "N/A")
        fallback_list = providers.get(orig_provider, {}).get("fallback", []) or DEFAULT_FALLBACK
        fallback_list = dedupe_keep_order(fallback_list)
        fallback_str = ", ".join(fallback_list)

        normal_url = strict_url = "N/A"
        desc = "Basic DNS replacement / Full strict DNS replacement"

        if "Normal" in types:
            normal_name = os.path.basename(types["Normal"])
            normal_encoded = urllib.parse.quote(normal_name)
            normal_url = f"[Link](https://raw.githubusercontent.com/{repo}/main/{OUTPUT_DIR}/{normal_encoded})"

        if "Strict" in types:
            strict_name = os.path.basename(types["Strict"])
            strict_encoded = urllib.parse.quote(strict_name)
            strict_url = f"[Link](https://raw.githubusercontent.com/{repo}/main/{OUTPUT_DIR}/{strict_encoded})"

        lines.append(f"| {orig_provider} | {country} | {normal_url} | {strict_url} | `{fallback_str}` | {desc} |")

    lines.append("\n---\n✅ Generated automatically. Do not edit manually.")
    os.makedirs(README_DIR, exist_ok=True)
    with open(os.path.join(README_DIR, "README.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    logging.info("🚀 Starting DNS config generation...")
    providers = parse_dns_list()
    logging.info(f"📑 Found {len(providers)} providers in dns_list.txt")

    files = []
    for provider, entries in providers.items():
        logging.info(f"⚙️ Generating configs for provider: {provider}")
        tpl = load_template()
        # deep copy template so modifications don't leak across providers
        tpl_copy = copy.deepcopy(tpl)

        # build `all_entries`: ipv4 + ipv6 + doh + dot + hostname
        all_entries = (
            dedupe_keep_order(entries["ipv4"])
            + dedupe_keep_order(entries["ipv6"])
            + dedupe_keep_order(entries["doh"])
            + dedupe_keep_order(entries["dot"])
            + dedupe_keep_order(entries["hostname"])
        )
        all_entries = dedupe_keep_order(all_entries)

        # Normal config (replace nameserver/direct/proxy lists)
        normal_cfg = copy.deepcopy(tpl_copy)
        normal_cfg.setdefault("dns", {})
        if all_entries:
            normal_cfg["dns"]["nameserver"] = all_entries
            normal_cfg["dns"]["direct-nameserver"] = all_entries
            normal_cfg["dns"]["proxy-server-nameserver"] = all_entries
        normal_cfg = add_fallback(normal_cfg, entries)
        f1 = save_config(provider, normal_cfg, "Normal")
        files.append(f1)
        logging.info(f"✅ Normal config saved: {f1}")

        # Strict config (replace default-nameserver with ip-only lists)
        strict_cfg = copy.deepcopy(tpl_copy)
        strict_cfg.setdefault("dns", {})
        strict_default = dedupe_keep_order(entries["ipv4"] + entries["ipv6"])
        if strict_default:
            strict_cfg["dns"]["default-nameserver"] = strict_default
        strict_cfg["dns"]["nameserver"] = all_entries
        strict_cfg["dns"]["direct-nameserver"] = all_entries
        strict_cfg["dns"]["proxy-server-nameserver"] = all_entries
        strict_cfg = add_fallback(strict_cfg, entries)
        f2 = save_config(provider, strict_cfg, "Strict")
        files.append(f2)
        logging.info(f"✅ Strict config saved: {f2}")

    generate_readme(files)
    logging.info("📄 README.md generated inside Generated/")


if __name__ == "__main__":
    main()
