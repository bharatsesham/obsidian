#!/bin/sh

# Trap TERM signal to allow script to gracefully handle SIGTERM
trap 'exit' TERM

# Define your domains here as a space-separated list
DOMAINS="$CERTBOT_DOMAIN1 $CERTBOT_DOMAIN2"

# Initial certificate acquisition or renewal for each domain
for domain in $DOMAINS; do
    # Check if certificates already exist
    if [ ! -d "/etc/letsencrypt/live/$domain" ]; then
        echo "Certificates for $domain not found. Attempting initial acquisition."
        certbot certonly --webroot --webroot-path=/var/www/certbot --email $CERTBOT_EMAIL -d $domain --agree-tos --non-interactive
        # Note: The nginx reload command has been moved outside of the loop to avoid reloading nginx multiple times unnecessarily.
    fi
done

# Reload nginx once after attempting to acquire certificates for all domains
# nginx -s reload

# Renewal loop
while :; do
    certbot renew --webroot --webroot-path=/var/www/certbot --deploy-hook "nginx -s reload"
    # Wait for 30 mins before checking for renewal again
    sleep 12m &
    wait $!
done
