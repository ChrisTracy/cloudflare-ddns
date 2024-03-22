import requests
import time
import logging
import os
import sys
import json

# Basic logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Cloudflare API endpoint
CF_API_ENDPOINT = "https://api.cloudflare.com/client/v4"

# Helper function to strip quotes from environment variables
def strip_quotes(value):
    if value.startswith(("'", '"')) and value.endswith(("'", '"')):
        return value[1:-1]
    return value

# Read and clean environment variables
CF_TOKEN = strip_quotes(os.getenv('CF_TOKEN', ''))
DOMAINS = strip_quotes(os.getenv('DOMAINS', ''))
ZONE_ID = strip_quotes(os.getenv('ZONE_ID', ''))
INTERVAL = int(os.getenv('INTERVAL', '900'))

# Ensure required environment variables are provided
if not CF_TOKEN or not DOMAINS or not ZONE_ID:
    logging.error("CF_TOKEN, DOMAINS, and ZONE_ID environment variables are required.")
    sys.exit(1)

# Convert DOMAINS string to a list
DOMAINS = [strip_quotes(domain) for domain in DOMAINS.split(',')]

def get_public_ip() -> str:
    """Fetch the current public IP using ipify API."""
    try:
        response = requests.get("https://api.ipify.org")
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logging.error(f"Error fetching public IP: {e}")
        return None

def get_current_dns_ip(zone_id: str, domain: str) -> str:
    """Fetch the current IP set in the DNS record for the domain."""
    headers = {
        "Authorization": f"Bearer {CF_TOKEN}",
        "Content-Type": "application/json"
    }
    try:
        dns_response = requests.get(f"{CF_API_ENDPOINT}/zones/{zone_id}/dns_records", headers=headers, params={"name": domain, "type": "A"})
        dns_response.raise_for_status()
        dns_records = dns_response.json()["result"]
        if dns_records:
            return dns_records[0]['content']
        else:
            return None
    except requests.RequestException as e:
        logging.error(f"Error fetching DNS record for {domain}: {e}")
        return None

def update_dns_record(zone_id: str, domain: str, ip: str):
    """Update or create the A record for the specified domain with the given IP."""
    current_ip = get_current_dns_ip(zone_id, domain)
    if current_ip == ip:
        logging.info(f"IP for {domain} has not changed. No update needed.")
        return
    
    headers = {
        "Authorization": f"Bearer {CF_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # The payload for creating/updating a DNS record
    payload = {
        "type": "A",
        "name": domain,
        "content": ip
    }

    try:
        # Check if the DNS record already exists
        dns_response = requests.get(f"{CF_API_ENDPOINT}/zones/{zone_id}/dns_records", headers=headers, params={"name": domain, "type": "A"})
        dns_response.raise_for_status()
        dns_records = dns_response.json()["result"]

        if dns_records:
            # Update the existing DNS record
            record_id = dns_records[0]['id']
            update_response = requests.put(f"{CF_API_ENDPOINT}/zones/{zone_id}/dns_records/{record_id}", headers=headers, json=payload)
            update_response.raise_for_status()
            logging.info(f"Updated DNS record for {domain} to {ip}")
        else:
            # Create the DNS record if it does not exist
            create_response = requests.post(f"{CF_API_ENDPOINT}/zones/{zone_id}/dns_records", headers=headers, json=payload)
            create_response.raise_for_status()
            logging.info(f"Created DNS record for {domain} with IP {ip}")
    except requests.RequestException as e:
        logging.error(f"Error updating/creating DNS record for {domain}: {e}")
        logging.error(f"Request payload: {json.dumps(payload, indent=2)}")

def main():
    while True:
        ip = get_public_ip()
        if ip:
            logging.info(f"Current public IP: {ip}")
            for domain in DOMAINS:
                update_dns_record(ZONE_ID, domain, ip)
        else:
            logging.error("Skipping updates due to IP fetch failure.")
        # Wait for the specified interval before checking again
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
