# 📂 Generated DNS Configs

These configs were automatically generated from **dns_list.txt** using the template `DNS_for_Clash.meta_Template.yml`.

## ℹ️ How it works
- **Normal configs** → Replace only `nameserver` and `proxy-server-nameserver`.
- **Strict configs** → Replace *all* DNS fields (`default-nameserver`, `nameserver`, `direct-nameserver`, `proxy-server-nameserver`).
- **Fallback** → If a provider defines `fallback` entries in `dns_list.txt`, those are used. Otherwise, a default global fallback list is applied.
- **Country** → Each provider can define its main host country with a `country` entry.

## 📜 Available configs
| Provider | Country | Type | Raw Link | Fallback DNS | Description |
|----------|---------|------|----------|--------------|-------------|
| Google | United States | Normal | [Link](https://raw.githubusercontent.com/asgharkapk/DNS-Only-Clash-Meta/main/Generated/Google_Normal.yml) | `8.8.8.8, 2001:4860:4860::8844` | Basic DNS replacement |
| Google | United States | Strict | [Link](https://raw.githubusercontent.com/asgharkapk/DNS-Only-Clash-Meta/main/Generated/Google_Strict.yml) | `8.8.8.8, 2001:4860:4860::8844` | Full strict DNS replacement |
| Cloudflare | United States | Normal | [Link](https://raw.githubusercontent.com/asgharkapk/DNS-Only-Clash-Meta/main/Generated/Cloudflare_Normal.yml) | `1.0.0.1, 2606:4700:4700::1001` | Basic DNS replacement |
| Cloudflare | United States | Strict | [Link](https://raw.githubusercontent.com/asgharkapk/DNS-Only-Clash-Meta/main/Generated/Cloudflare_Strict.yml) | `1.0.0.1, 2606:4700:4700::1001` | Full strict DNS replacement |
| Quad9 | Switzerland | Normal | [Link](https://raw.githubusercontent.com/asgharkapk/DNS-Only-Clash-Meta/main/Generated/Quad9_Normal.yml) | `9.9.9.9` | Basic DNS replacement |
| Quad9 | Switzerland | Strict | [Link](https://raw.githubusercontent.com/asgharkapk/DNS-Only-Clash-Meta/main/Generated/Quad9_Strict.yml) | `9.9.9.9` | Full strict DNS replacement |

---
✅ Generated automatically. Do not edit manually.