# Cloudflare Dynamic DNS Updater

This Docker image automatically updates specified DNS records in your Cloudflare account with your current public IP address. It's designed to be simple and lightweight, ideal for dynamic IP environments where DNS records need frequent updates.

```yml
version: '3'
services:
  cloudflare-ddns:
    image: christracy/cloudflare-ddns
    environment:
      CF_TOKEN: "your_cloudflare_api_token"
      DOMAINS: "yourdomain.com, subdomain.yourdomain.com, *.yourdomain.com"
      ZONE_ID: "your_cloudflare_zone_id"
      INTERVAL: "900"
    restart: unless-stopped
```
