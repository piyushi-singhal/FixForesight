#!/bin/bash
# Solr initialization script to index historical documents
set -e

SOLR_HOST=${1:-localhost}
SOLR_PORT=${2:-8983}
SOLR_CORE="incidents"

echo "Waiting for Apache Solr to start at $SOLR_HOST:$SOLR_PORT..."
until curl -s "http://$SOLR_HOST:$SOLR_PORT/solr/admin/cores?action=STATUS" | grep -q '"status"'; do
  sleep 2
done

echo "Apache Solr is up! Indexing historical incidents into core '$SOLR_CORE'..."

# Post sample data and commit changes immediately
curl -X POST -H 'Content-type:application/json' \
  "http://$SOLR_HOST:$SOLR_PORT/solr/$SOLR_CORE/update?commit=true" \
  --data-binary @infra/solr/sample_incidents.json

echo "Solr historical incident indexing completed!"
