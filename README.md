# Cloudflare Dynamic DNS Updater

This Docker image automatically updates specified DNS records in your Cloudflare account with your current public IP address. It's designed to be simple and lightweight, ideal for dynamic IP environments where DNS records need frequent updates.

## Quick Setup

You will need your [Cloudflare Zone ID](https://developers.cloudflare.com/fundamentals/setup/find-account-and-zone-ids/) and your [Cloudflare Token](https://developers.cloudflare.com/fundamentals/api/get-started/create-token/)

1. Install Docker and Docker-Compose

- [Docker Install documentation](https://docs.docker.com/install/)
- [Docker-Compose Install documentation](https://docs.docker.com/compose/install/)

2. Create a docker-compose.yml file similar to this and edit the fields with your domain/cloudflare information. The default update interval is 900 seconds (15 min):

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

3. Bring up your stack by running

```bash
docker-compose up -d

# If using docker-compose-plugin
docker compose up -d

```
