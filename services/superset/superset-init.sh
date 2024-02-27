#!/bin/bash

superset db upgrade

# Add your database connection
superset set_database_uri --database_name=other --uri=dynamodb://${AWS_ACCESS_KEY}:${AWS_SECRET_KEY}@dynamodb.us-west-2.amazonaws.com:443?connector=superset

# Check if the admin user exists before creating
if ! superset fab list-users | grep -q "${ADMIN_USERNAME}"; then
    superset fab create-admin \
        --username ${ADMIN_USERNAME} \
        --firstname ${ADMIN_FIRSTNAME} \
        --lastname ${ADMIN_LASTNAME} \
        --email ${ADMIN_EMAIL} \
        --password ${ADMIN_PASSWORD}
fi

# Initialize Superset if not already done
if ! [ -e "/app/superset_init_flag" ]; then
    superset init
    touch /app/superset_init_flag
fi

# Start Superset
superset run -h 0.0.0.0 -p 8088 --with-threads --reload --debugger
