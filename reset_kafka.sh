#!/bin/bash
echo "Stopping Kafka & Zookeeper..."
docker compose down

echo "Removing meta.properties..."
rm -f ./data/kafka_data/meta.properties

echo "Restarting services..."
docker compose up -d