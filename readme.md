### Purpose

WireGuard Watchdog service resetting WG interface when public IP changes (due to WAN failover on the firewall) 

### Setup
1. Move `wg-watchdog.py` file to `/scripts` folder (create the folder if it doesn't exist already).
2. Paste `wireguard-watchdog.service` file into `/etc/systemd/system` folder.
3. Enable and run `wireguard-watchdog.service`:

```
systemctl enable wireguard-watchdog
systemctl daemon-reload
systemctl start wireguard-watchdog
```