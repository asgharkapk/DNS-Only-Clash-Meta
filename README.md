# DNS-Only-Clash-Meta
Clash meta dns only configs

---

# Clash.Meta DNS-Only Configuration Template

A minimal Clash.Meta template focused solely on DNS resolution. This template is ideal for users who want **fast, reliable DNS handling** without routing full traffic through proxies. Perfect for circumventing local DNS hijacking, enhancing privacy, or simply testing DNS features.

---

## Features

* **DNS-Only Mode**: The configuration only handles DNS queries and doesn’t route general internet traffic.
* **Enhanced DNS**: Supports `fake-ip` and `redir-host` modes to bypass DNS-based blocking.
* **Custom Nameservers**: Easily switch to trusted DNS servers (Cloudflare, Google, Quad9, or regional).
* **NTP Support**: Optional NTP synchronization for timestamp-sensitive domains.
* **Lightweight**: Minimal resource usage.

---

## Configuration Example

```yaml
port: 7890
socks-port: 7891
mixed-port: 7892
allow-lan: true
mode: rule
log-level: info
external-controller: 127.0.0.1:9090

dns:
  enable: true
  listen: 0.0.0.0:7874
  default-nameserver:
    - 1.1.1.1
    - 8.8.8.8
  enhanced-mode: fake-ip
  nameserver:
    - 1.1.1.1
    - 8.8.8.8
    - 9.9.9.9
  fallback:
    - 8.8.4.4
    - 1.0.0.1

ntp:
  enable: true
  server: time.apple.com
  port: 123
  interval: 30
```

---

## How to Use

1. **Download the template** and save it as `config.yaml`.
2. **Edit DNS servers** if necessary to match your preferred providers.
3. **Start Clash.Meta** with the configuration:

   ```bash
   clash-meta -f config.yaml
   ```
4. **Verify DNS resolution** using tools like `nslookup` or `dig`.

---

## Recommended DNS Providers

| Provider   | IPv4         | Notes                            |
| ---------- | ------------ | -------------------------------- |
| Cloudflare | 1.1.1.1      | Fast, privacy-focused            |
| Google     | 8.8.8.8      | Widely available                 |
| Quad9      | 9.9.9.9      | Security-focused, blocks malware |
| AdGuard    | 94.140.14.14 | Blocks ads and trackers          |

---

## Notes

* This template **does not route web traffic**; only DNS queries are handled.
* If you want to combine this with full proxy routing, use `mode: rule` and add proxy groups.
* `enhanced-mode: fake-ip` is recommended in regions with DNS hijacking, as it provides more reliable domain resolution.

---

## Contributing

If you have better DNS servers, fallback strategies, or improvements to the configuration, feel free to submit a pull request.

---

