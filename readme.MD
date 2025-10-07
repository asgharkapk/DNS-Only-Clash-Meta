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

In **Clash / Clash.Meta YAML configs**, the DNS section can define multiple types of upstream resolvers. Each serves a different role in the DNS workflow:

---

### 🔹 `default-nameserver`

* Used for **bootstrapping DNS** before Clash’s own DNS is ready.
* Typically set to **public, reliable IP-based resolvers** (not domain names, because Clash hasn’t resolved anything yet).
* Example:

  ```yaml
  default-nameserver:
    - 1.1.1.1
    - 8.8.8.8
  ```
* Purpose: resolve domain names of your configured `nameserver` (especially if those are DoH/DoT endpoints).

* * **`SHOULD BE ONLY PURE IP (IPV4/IPV6)`**

---

### 🔹 `nameserver`

* The **main resolvers Clash uses** to resolve domains.
* You can mix plain DNS, DoH, DoT.
* Example:

  ```yaml
  nameserver:
    - https://dns.google/dns-query
    - tls://1.1.1.1:853
  ```
* Clash uses these to resolve most queries, depending on rules and fake-IP setup.

---

### 🔹 `direct-nameserver`

* Used **only when traffic is DIRECT** (bypasses proxy).
* Ensures local/IR domains resolve correctly without being forced through foreign resolvers.
* Example:

  ```yaml
  direct-nameserver:
    - 178.22.122.100   # Shecan (Iran DNS)
    - 185.51.200.2
  ```
* Purpose: avoid DNS poisoning/hijacking when accessing local sites directly.

---

### 🔹 `proxy-server-nameserver`

* Used when **queries for proxy servers themselves** need resolution.
* Example: if your proxy node’s hostname (`hk.example.com`) needs resolving, Clash uses this.
* Example:

  ```yaml
  proxy-server-nameserver:
    - 8.8.8.8
    - 1.1.1.1
  ```
* Keeps node resolution separate from normal traffic, so proxies can still be reached if normal DNS is blocked.

---

✅ **Summary table:**

| Field                     | Purpose                                          |
| ------------------------- | ------------------------------------------------ |
| `default-nameserver`      | Bootstrap resolver to reach your DoH/DoT servers |
| `nameserver`              | Main resolvers for general queries               |
| `direct-nameserver`       | Used for DIRECT connections only                 |
| `proxy-server-nameserver` | Used for resolving proxy server hostnames        |

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

### Cloudflare

```
nameserver:
    - 1.1.1.1
    - 1.0.0.1
    - 2606:4700:4700::1111
    - 2606:4700:4700::1001
    - https://1.1.1.1/dns-query
    - https://security.cloudflare-dns.com/dns-query
    - tls://one.one.one.one
    - one.one.one.one
    - tls://security.cloudflare-dns.com
```

### Google Public DNS

```
nameserver:
    - 8.8.8.8
    - 8.8.4.4
    - 2001:4860:4860::8888
    - 2001:4860:4860::8844
    - https://dns.google.com/resolve
    - https://dns.google/dns-query
    - tls://dns.google
    - dns.google
    - tls://dns.google
```

### Quad9

```
nameserver:
    - 9.9.9.9
    - 149.112.112.112
    - 2620:fe::fe
    - 2620:fe::9
    - https://dns.quad9.net/dns-query
    - https://dns.quad9.net/dns-query
    - tls://dns.quad9.net
    - dns.quad9.net
    - tls://dns.quad9.net
```

### CleanBrowsing

```
nameserver:
    - 185.228.168.9
    - 185.228.169.9
    - 2a0d:2a00:1::1
    - 2a0d:2a00:2::2
    - https://doh.cleanbrowsing.org/doh/family-filter/
    - https://doh.cleanbrowsing.org/doh/security-filter/
    - tls://dns.cleanbrowsing.org
    - dns.cleanbrowsing.org
    - tls://dns.cleanbrowsing.org
```

### AdGuard DNS

```
nameserver:
    - 94.140.14.14
    - 94.140.15.15
    - 2a10:50c0::ad1:ff
    - 2a10:50c0::ad2:ff
    - https://dns.adguard-dns.com/dns-query
    - https://dns.adguard-dns.com/dns-query
    - tls://dns.adguard-dns.com
    - dns.adguard-dns.com
    - tls://dns.adguard-dns.com
```

In **Clash.Meta**, the **`nameserver-policy`** (sometimes called `dns-policy` in older configs) controls **how DNS queries are routed to your configured nameservers**. It’s useful when you have multiple DNS servers and want to specify **which queries go to which server**.

Here’s a breakdown:

---

### **1. Basic `nameserver` config**

Example:

```yaml
dns:
  enable: true
  listen: 0.0.0.0:7874
  enhanced-mode: fake-ip
  nameserver:
    - 1.1.1.1
    - 8.8.8.8
```

This just sets the DNS servers Clash will use. But **all queries are sent to these servers in order**, without policy control.

---

### **2. `nameserver-policy`**

You can define **policies for specific domains**. Syntax:

```yaml
dns:
  enable: true
  listen: 0.0.0.0:7874
  enhanced-mode: fake-ip
  nameserver:
    - 1.1.1.1
    - 8.8.8.8
  default-nameserver-policy: all
  nameserver-policy:
    - domain: "geosite:cn"
      server:
        - 223.5.5.5
        - 223.6.6.6
    - domain: "geosite:private"
      server:
        - 127.0.0.1
```

**Explanation:**

| Field                       | Meaning                                                                        |
| --------------------------- | ------------------------------------------------------------------------------ |
| `default-nameserver-policy` | Which server(s) are used if no policy matches (`all`, `random`, `round-robin`) |
| `nameserver-policy`         | List of domain-based rules mapping queries to specific DNS servers             |
| `domain`                    | Can be an exact domain, suffix, or geosite category (requires `geosite.dat`)   |
| `server`                    | DNS server(s) to use for that domain                                           |

---

### **3. Example Scenarios**

**Split DNS:**

* Chinese domains → China DNS
* Foreign domains → Public DNS

```yaml
dns:
  enable: true
  enhanced-mode: fake-ip
  nameserver:
    - 1.1.1.1
    - 8.8.8.8
  default-nameserver-policy: all
  nameserver-policy:
    - domain: "geosite:cn"
      server:
        - 223.5.5.5
        - 223.6.6.6
```

Here, queries to `geosite:cn` (China sites) go to AliDNS, others go to Cloudflare/Google.

---

### **4. Key Notes**

1. **Order matters**: Clash checks `nameserver-policy` first, then falls back to `default-nameserver-policy`.
2. **Enhanced-mode options**:

   * `fake-ip` → resolves domains to fake IPs for routing through proxies
   * `redir-host` → normal host-based resolution
3. **Works with rule providers**: You can reference geosite categories for policy-based routing.

---

Here’s a **Clash.Meta DNS config optimized for Iran**, using `nameserver-policy` to avoid DNS hijacking while maintaining fast resolution:

```yaml
dns:
  enable: true
  listen: 0.0.0.0:7874
  ipv6: false
  default-nameserver-policy: all
  enhanced-mode: fake-ip
  fake-ip-range: 198.18.0.1/16   # standard fake IP range
  nameserver:
    # Public, secure DNS for foreign sites
    - 1.1.1.1          # Cloudflare
    - 1.0.0.1
    - 8.8.8.8          # Google
    - 8.8.4.4
    - https://cloudflare-dns.com/dns-query    # Cloudflare DoH
    - https://dns.google/dns-query            # Google DoH
    - tls://1.1.1.1                           # Cloudflare DoT
    - tls://8.8.8.8                            # Google DoT
  nameserver-policy:
    # Iran domains go to local/ISP DNS to prevent hijacking
    - domain: "geosite:ir"
      server:
        - 2.188.21.140   # local Iranian DNS (Fars, etc.)
        - 37.10.67.10
    # Private networks go to local resolver
    - domain: "geosite:private"
      server:
        - 127.0.0.1
    # Optional: Chinese domains to AliDNS
    - domain: "geosite:cn"
      server:
        - 223.5.5.5
        - 223.6.6.6
```

### ✅ Key Points

1. **`fake-ip-range`** ensures Clash can route connections through proxies even for foreign domains.
2. **`default-nameserver-policy: all`** → all other domains not matched in `nameserver-policy` will use the public DNS servers.
3. **`nameserver-policy`** prevents hijacking of `.ir` domains by routing them to trusted local DNS servers.
4. **Private networks (`geosite:private`)** use `127.0.0.1` if you have a local resolver.

---

```yml
dns:
  enable: true
  listen: 0.0.0.0:7874
  ipv6: false
  default-nameserver-policy: all
  enhanced-mode: fake-ip
  fake-ip-range: 198.18.0.1/16
  query-url-ttl: 600      # optional: cache TTL for faster responses
  fallback:
    - https://cloudflare-dns.com/dns-query
    - https://dns.google/dns-query
    - tls://1.1.1.1
    - tls://8.8.8.8

  # Primary nameservers for different regions
  nameserver:
    # Foreign/Public domains
    - https://cloudflare-dns.com/dns-query
    - https://dns.google/dns-query
    - tls://1.1.1.1
    - tls://8.8.8.8
    - tls://9.9.9.9        # Quad9 DoT
    - tls://149.112.112.112

  nameserver-policy:
    # Iranian domains → local DNS (avoid hijacking)
    - domain: "geosite:ir"
      server:
        - 37.10.67.10
        - 2.188.21.140

    # Private/local networks
    - domain: "geosite:private"
      server:
        - 127.0.0.1

    # Chinese domains → AliDNS
    - domain: "geosite:cn"
      server:
        - 223.5.5.5
        - 223.6.6.6
        - 180.76.76.76

    # Optional: fallback for general regional categories
    - domain: "geosite:asia"
      server:
        - 1.1.1.1
        - 8.8.8.8
```

---

# Clash / Clash.Meta Configuration Key Reference

This document explains what each configuration key does in a typical Clash/Clash.Meta configuration.

---

## Core Proxy Settings

| Key                   | Default / Example | Description                                                                                                                                                  |
| --------------------- | ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `port`                | `7890`            | The main HTTP proxy port. Applications can connect here using HTTP/HTTPS proxy.                                                                              |
| `socks-port`          | `7891`            | The SOCKS5 proxy port for applications that support SOCKS.                                                                                                   |
| `mixed-port`          | `7892`            | A hybrid port that accepts both HTTP and SOCKS connections. Useful for apps with unknown proxy type.                                                         |
| `allow-lan`           | `true`            | Whether devices on the local network (LAN) can connect to your proxy.                                                                                        |
| `mode`                | `rule`            | Determines how traffic is handled: <br> - `direct`: bypass proxy <br> - `global`: all traffic through proxy <br> - `rule`: use rules to decide per domain/IP |
| `log-level`           | `info`            | Sets logging verbosity: <br> - `info`: normal logs <br> - `warning`, `error`, `debug` available for troubleshooting                                          |
| `external-controller` | `127.0.0.1:9090`  | API/GUI controller endpoint. Allows external tools (like Clash Dashboard) to interact with Clash.                                                            |

---

## DNS Configuration

DNS is crucial for domain resolution, filtering, and preventing ISP hijacking.

| Key                         | Example            | Description                                                                                                                                                                                                                   |
| --------------------------- | ------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `enable`                    | `true`             | Turns DNS service on or off.                                                                                                                                                                                                  |
| `listen`                    | `0.0.0.0:7874`     | IP and port where the DNS service listens. `0.0.0.0` allows all interfaces.                                                                                                                                                   |
| `ipv6`                      | `false`            | Whether to enable IPv6 resolution.                                                                                                                                                                                            |
| `enhanced-mode`             | `fake-ip`          | Resolves certain domains to "fake" IPs so they can be proxied without DNS leaks. Options: `redir-host`, `fake-ip`.                                                                                                            |
| `fake-ip-range`             | `198.18.0.1/16`    | IP range used for fake-IP resolution. Standard private testing range.                                                                                                                                                         |
| `query-url-ttl`             | `600`              | Optional: cache time for DNS queries in seconds. Improves performance.                                                                                                                                                        |
| `default-nameserver`        | `1.1.1.1, 8.8.8.8` | The DNS servers used when no `nameserver-policy` matches.                                                                                                                                                                     |
| `nameserver`                | multiple           | List of DNS servers for general resolution, can include: <br> - Plain IP (UDP/TCP) <br> - `https://` (DoH) <br> - `tls://` (DoT)                                                                                              |
| `fallback`                  | multiple           | DNS servers used if primary servers fail. Supports DoH/DoT.                                                                                                                                                                   |
| `default-nameserver-policy` | `all`              | Which domains use the `default-nameserver`. Usually `all`.                                                                                                                                                                    |
| `nameserver-policy`         | structured list    | Domain-specific DNS overrides. Example: <br> - `"geosite:ir"` → local Iranian DNS to prevent hijacking <br> - `"geosite:cn"` → AliDNS for Chinese domains <br> - `"geosite:private"` → `127.0.0.1` for local/private networks |

### Notes on DNS Policies

* **`geosite:*`** domains are groups of domains categorized by region or type. Useful for selective DNS routing.
* DNS policies ensure sensitive or regional domains are resolved by trusted servers to prevent interference or hijacking.

---

## NTP Configuration

| Key        | Example          | Description                                               |
| ---------- | ---------------- | --------------------------------------------------------- |
| `enable`   | `true`           | Enables NTP client to synchronize system clock via Clash. |
| `server`   | `time.apple.com` | NTP server to query time from.                            |
| `port`     | `123`            | Standard NTP port.                                        |
| `interval` | `30`             | Interval (in seconds) for time synchronization.           |

NTP ensures accurate system time, which is critical for SSL/TLS verification, certificate validation, and some proxy behaviors.

---

## Summary

This configuration allows Clash/Clash.Meta to:

* Handle HTTP/SOCKS traffic with multiple ports and rules.
* Provide advanced DNS features: fake-IP, DoH/DoT, fallback, and domain-specific policies.
* Synchronize time using NTP for secure connections.

---

