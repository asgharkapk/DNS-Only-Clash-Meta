# 📂 Generated DNS Configs

These configs were automatically generated from **dns_list.txt** using the template `DNS_for_Clash.meta_Template.yml`.

## ℹ️ How it works
- **Normal configs** → Replace only `nameserver` and `proxy-server-nameserver`.
- **Strict configs** → Replace *all* DNS fields (`default-nameserver`, `nameserver`, `direct-nameserver`, `proxy-server-nameserver`).
- **Fallback** → If a provider defines `fallback` entries in `dns_list.txt`, those are used. Otherwise, a default global fallback list is applied.

## 📜 Available configs
| Provider | Type | Raw Link | Fallback DNS | Description |
|----------|------|----------|--------------|-------------|
| Google | Normal | [Link](https://raw.githubusercontent.com/asgharkapk/DNS-Only-Clash-Meta/main/Generated/Google_Normal.yml) | `8.8.8.8, 1.1.1.1, 9.9.9.9, 94.140.14.14, 2606:4700:4700::1111, 2001:4860:4860::8888` | Basic DNS replacement |
| Google | Strict | [Link](https://raw.githubusercontent.com/asgharkapk/DNS-Only-Clash-Meta/main/Generated/Google_Strict.yml) | `8.8.8.8, 1.1.1.1, 9.9.9.9, 94.140.14.14, 2606:4700:4700::1111, 2001:4860:4860::8888` | Full strict DNS replacement |
| Cloudflare | Normal | [Link](https://raw.githubusercontent.com/asgharkapk/DNS-Only-Clash-Meta/main/Generated/Cloudflare_Normal.yml) | `8.8.8.8, 1.1.1.1, 9.9.9.9, 94.140.14.14, 2606:4700:4700::1111, 2001:4860:4860::8888` | Basic DNS replacement |
| Cloudflare | Strict | [Link](https://raw.githubusercontent.com/asgharkapk/DNS-Only-Clash-Meta/main/Generated/Cloudflare_Strict.yml) | `8.8.8.8, 1.1.1.1, 9.9.9.9, 94.140.14.14, 2606:4700:4700::1111, 2001:4860:4860::8888` | Full strict DNS replacement |

---
✅ Generated automatically. Do not edit manually.