# Initialize a new microservice

SERVICE_NAME=$1
if [ -z "$SERVICE_NAME" ]; then
    echo "Usage: ./init-service.sh <service-name>"
    exit 1
fi

SERVICE_DIR="services/$SERVICE_NAME"
mkdir -p $SERVICE_DIR/{src/{api,domain,services,repositories,infrastructure},tests}
