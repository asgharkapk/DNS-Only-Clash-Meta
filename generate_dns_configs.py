import os
import yaml
import logging
import urllib.parse
import copy

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")

class NoAliasDumper(yaml.Dumper):
    def ignore_aliases(self, data):
        return True

INPUT_FILE = "dns_list.txt"
TEMPLATE_FILE = "DNS_for_Clash.meta_Template.yml"
OUTPUT_DIR = "Generated/Files"
README_DIR = "Generated"

DEFAULT_FALLBACK = [
    "8.8.8.8", "1.1.1.1", "9.9.9.9", "94.140.14.14",
    "2606:4700:4700::1111", "2001:4860:4860::8888"
]

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
        return yaml.safe_load(f)

def save_config(provider, data, suffix):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_file = os.path.join(OUTPUT_DIR, f"{provider}_{suffix}.yml")
    print(f"Writing {out_file} with data: {data['dns']}")
    if not data:
        logging.warning(f"⚠️ No data to write for {provider}_{suffix}")
    with open(out_file, "w", encoding="utf-8") as f:
        yaml.dump(
            data,
            f,
            Dumper=NoAliasDumper,
            allow_unicode=True,
            sort_keys=False,
            default_flow_style=False   # <- forces each list item on its own line
        )
    return out_file

def generate_readme(files):
    lines = [
        "# 📂 Generated DNS Configs",
        "",
        "This repository provides **automatically generated Clash.Meta DNS configurations**. ",
        "The configs are created from the input file **dns_list.txt** and a base template `DNS_for_Clash.meta_Template.yml`.",
        "",
        "## 🌐 How DNS works in Clash.Meta / MiHoYo",
        "Clash.Meta and MiHoYo clients rely on DNS (Domain Name System) to resolve domain names into IP addresses for both direct and proxied connections. ",
        "Correct DNS configuration is critical for improving connection speed, avoiding regional restrictions, and maintaining privacy. Misconfigured DNS can lead to slow connections, blocked services, or leaks of DNS queries outside the intended network path.",
        "",
        "Key DNS concepts in Clash.Meta / MiHoYo:",
        "- **nameserver** → Primary DNS servers used for general traffic resolution.",
        "- **direct-nameserver** → DNS servers used specifically for direct (non-proxied) connections.",
        "- **proxy-server-nameserver** → DNS servers used for traffic routed through a proxy.",
        "- **default-nameserver** → The fallback for all queries if no other DNS is matched.",
        "",
        "### ⚙️ The `dns-out` Proxy Entry",
        "In some configs, you may see:",
        "```yaml",
        "proxies:",
        "- name: \"dns-out\"",
        "  type: dns",
        "```",
        "- **What it does:** This defines a DNS-type proxy in Clash.Meta, allowing DNS queries to be routed through a specific proxy rather than the default system resolver. It can help in situations where you want DNS requests to follow the same path as proxied traffic or to bypass certain network restrictions.",
        "- **When to use it:**",
        "  - You want all DNS queries to be resolved by a controlled server (e.g., for privacy or to avoid ISP DNS blocking).",
        "  - You are using a proxy that requires DNS resolution through it (to avoid leaks or misrouting).",
        "- **When it might be unnecessary or problematic:**",
        "  - If your DNS queries do not need to go through a proxy, adding `dns-out` may slightly increase latency.",
        "  - Some users may experience conflicts if the proxy server is misconfigured or unavailable, which could break DNS resolution.",
        "- **Recommendation:** Include `dns-out` only if your use case requires routing DNS through a proxy. Otherwise, standard `nameserver` settings are sufficient.",
        "",
        "These configs allow you to:",
        "- Override default DNS servers with custom providers.",
        "- Provide fallback DNS servers to ensure reliability.",
        "- Apply normal or strict rules to control how DNS queries are resolved in different scenarios.",
        "- Ensure that sensitive DNS queries do not leak outside of the intended path.",
        "",
        "Each provider has two versions of configuration for different use cases:",
        "",
        "* **`-REJECT-DROP`** → This action blocks the DNS query or network request entirely. It rejects the request and drops it silently, preventing it from reaching the destination. This is useful for filtering unwanted domains, ads, or malicious traffic.",
        "* **`-PASS`** → This action allows the DNS query or network request to continue normally. It essentially means “let this traffic pass through without interference,” using the defined DNS or proxy rules.",
        "",
        "## ℹ️ How it works",
        "- **Normal configs** → Replace only `nameserver` and `proxy-server-nameserver`. Suitable for general use when you want to override the main DNS without affecting other DNS settings.",
        "- **Strict configs** → Replace *all* DNS fields (`default-nameserver`, `nameserver`, `direct-nameserver`, `proxy-server-nameserver`). Use this when you need full control over DNS resolution, ensuring that all queries go through the specified servers and fallbacks.",
        "- **Why the difference?** Normal configs are lighter and safer for casual usage, while Strict configs enforce complete DNS replacement to avoid leaks or fallback to undesired DNS servers.",
        "- **Fallback** → If a provider defines `fallback` entries in `dns_list.txt`, those are prioritized. Otherwise, a global default fallback list is used.",
        "- **Country** → Each provider can define its host country using a `country` entry. If none is defined, it's marked as `N/A`.",
        "",
        "## 📜 Available Configs",
        "Below is a list of all providers with their generated configs:",
        "",
        "| Provider | Country | Normal | Strict | Fallback DNS | Description |",
        "|----------|---------|--------|--------|--------------|-------------|",
    ]

    # build a map of provider -> fallback list from dns_list.txt
    providers = parse_dns_list()

    # group files by provider
    grouped = {}
    for f in files:
        name = os.path.basename(f)
        provider, t = name.replace(".yml","").rsplit("_",1)
        grouped.setdefault(provider, {})[t] = f

    for provider, types in grouped.items():
        country = providers.get(provider, {}).get("country", "N/A")
        fallback_list = providers.get(provider, {}).get("fallback", [])
        if not fallback_list:
            fallback_list = DEFAULT_FALLBACK
        # Deduplicate while preserving order
        fallback_list = list(dict.fromkeys(fallback_list))
        fallback_str = ", ".join(fallback_list)

        normal_url = strict_url = "N/A"
        desc = "Basic DNS replacement / Full strict DNS replacement"

        repo = os.environ.get("GITHUB_REPOSITORY","OWNER/REPO")

        if "Normal" in types:
            normal_name = os.path.basename(types["Normal"])
            normal_encoded = urllib.parse.quote(normal_name)
            normal_url = f"[Link](https://raw.githubusercontent.com/{repo}/main/{OUTPUT_DIR}/{normal_encoded})"

        if "Strict" in types:
            strict_name = os.path.basename(types["Strict"])
            strict_encoded = urllib.parse.quote(strict_name)
            strict_url = f"[Link](https://raw.githubusercontent.com/{repo}/main/{OUTPUT_DIR}/{strict_encoded})"

        lines.append(f"| {provider} | {country} | {normal_url} | {strict_url} | `{fallback_str}` | {desc} |")

    lines.append("\n---\n✅ Generated automatically. Do not edit manually.")
    with open(os.path.join(README_DIR,"README.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def main():
    logging.info("🚀 Starting DNS config generation...")
    providers = parse_dns_list()
    logging.info(f"📑 Found {len(providers)} providers in dns_list.txt")

    files = []
    for provider, entries in providers.items():
        logging.info(f"⚙️ Generating configs for provider: {provider}")
        tpl = load_template()
        if not tpl:
            logging.error("❌ Template file is empty or invalid YAML!")
            return

        all_entries = list(dict.fromkeys(entries["ipv4"])) + list(dict.fromkeys(entries["ipv6"])) + list(dict.fromkeys(entries["doh"])) + list(dict.fromkeys(entries["dot"])) + list(dict.fromkeys(entries["hostname"]))
        if not all_entries:
            logging.warning(f"⚠️ Provider {provider} has no DNS entries. Skipping...")
            continue

        # Normal config
        normal_cfg = copy.deepcopy(tpl) or {}
        normal_cfg["dns"]["nameserver"] = all_entries
        normal_cfg["dns"]["direct-nameserver"] = all_entries
        normal_cfg["dns"]["proxy-server-nameserver"] = all_entries
        normal_cfg = add_fallback(normal_cfg, entries)
        f1 = save_config(provider, normal_cfg, "Normal")
        files.append(f1)
        logging.info(f"✅ Normal config saved: {f1}")

        # Strict config
        strict_cfg = copy.deepcopy(tpl) or {}
        strict_cfg["dns"]["default-nameserver"] = list(dict.fromkeys(entries["ipv4"])) + list(dict.fromkeys(entries["ipv6"]))
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
