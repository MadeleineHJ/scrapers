#!/bin/bash
if [ -n "$GCP_SA_KEY" ]; then
    echo "$GCP_SA_KEY" > /tmp/sa.json
    export GOOGLE_APPLICATION_CREDENTIALS=/tmp/sa.json
fi

exec "$@"