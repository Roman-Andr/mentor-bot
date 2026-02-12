#!/bin/bash

# Configuration
AUTH_SERVICE_URL="http://localhost:8001"
CHECKLISTS_SERVICE_URL="http://localhost:8002"
KNOWLEDGE_SERVICE_URL="http://localhost:8003"
NOTIFICATION_SERVICE_URL="http://localhost:8004"
ESCALATION_SERVICE_URL="http://localhost:8005"
ADMIN_EMAIL="andrroman07@yandex.ru"
ADMIN_PASSWORD="admin123"
API_KEY="test_api_key"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Logging functions
log_info() {
    echo -e "${CYAN}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_debug() {
    if [ "${DEBUG:-false}" = "true" ]; then
        echo -e "${MAGENTA}[DEBUG]${NC} $1"
    fi
}

log_step() {
    echo -e "${BLUE}>>>${NC} ${BOLD}$1${NC}"
}

log_divider() {
    echo -e "${BLUE}========================================${NC}"
}

# Get JWT token for admin
get_admin_token() {
    log_debug "Getting admin token for $ADMIN_EMAIL"
    
    response=$(curl -L -s -X POST "$AUTH_SERVICE_URL/api/v1/auth/login" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=$ADMIN_EMAIL&password=$ADMIN_PASSWORD&grant_type=password")
    
    token=$(echo "$response" | jq -r '.access_token')
    
    if [ -z "$token" ] || [ "$token" = "null" ]; then
        log_error "Failed to get admin token. Response: $response"
        return 1
    fi
    
    log_debug "Admin token obtained successfully"
    echo "$token"
}

# Extract token from file if exists, otherwise get new one
ensure_token() {
    log_debug "Ensuring valid admin token"
    
    if [ -f ".admin_token" ] && [ -s ".admin_token" ]; then
        token=$(cat .admin_token)
        log_debug "Found existing token in file"
        
        # Verify token is still valid
        if verify_token "$token"; then
            log_debug "Existing token is valid"
            echo "$token"
            return
        else
            log_warning "Existing token is invalid, getting new one"
        fi
    fi
    
    token=$(get_admin_token)
    if [ $? -eq 0 ]; then
        echo "$token" > .admin_token
        log_debug "New token saved to file"
        echo "$token"
    else
        log_error "Failed to get admin token"
        return 1
    fi
}

# Verify token is valid
verify_token() {
    local token=$1
    log_debug "Verifying token validity"
    
    response=$(curl -s -o /dev/null -w "%{http_code}" \
        -X GET "$AUTH_SERVICE_URL/api/v1/auth/me" \
        -H "Authorization: Bearer $token")
    
    if [ "$response" = "200" ]; then
        log_debug "Token is valid (HTTP $response)"
        return 0
    else
        log_debug "Token is invalid (HTTP $response)"
        return 1
    fi
}

# Export token for use
export_token() {
    log_step "Getting admin authentication token"
    
    token=$(ensure_token)
    if [ $? -eq 0 ]; then
        export ADMIN_TOKEN="$token"
        log_success "Token exported as ADMIN_TOKEN"
    else
        log_error "Failed to get authentication token"
        exit 1
    fi
}

# Check if service is healthy
check_service_health() {
    local service_url=$1
    local service_name=$2
    
    log_debug "Checking health of $service_name at $service_url"
    
    response=$(curl -s -o /dev/null -w "%{http_code}" \
        -X GET "$service_url/health" \
        --max-time 5)
    
    if [ "$response" = "200" ]; then
        log_debug "$service_name is healthy (HTTP $response)"
        return 0
    else
        log_debug "$service_name health check failed (HTTP $response)"
        return 1
    fi
}

# Wait for service to become available
wait_for_service() {
    local service_url=$1
    local service_name=$2
    local max_attempts=${3:-30}
    local wait_seconds=${4:-2}
    
    log_step "Waiting for $service_name to be available"
    
    for i in $(seq 1 $max_attempts); do
        if check_service_health "$service_url" "$service_name"; then
            return 0
        fi
        
        log_warning "Attempt $i/$max_attempts: $service_name not ready yet"
        sleep $wait_seconds
    done
    
    log_error "$service_name failed to start after $max_attempts attempts"
    return 1
}

# Setup function for initial checks
setup_checks() {
    log_divider
    log_step "Starting setup checks"
    
    # Check required tools
    if ! command -v jq &> /dev/null; then
        log_error "jq is required but not installed. Please install jq first."
        exit 1
    fi
    
    if ! command -v curl &> /dev/null; then
        log_error "curl is required but not installed. Please install curl first."
        exit 1
    fi
    
    log_success "Required tools are available"
    
    # Check services
    wait_for_service "$AUTH_SERVICE_URL" "Auth Service"
    wait_for_service "$CHECKLISTS_SERVICE_URL" "Checklists Service"
    wait_for_service "$KNOWLEDGE_SERVICE_URL" "Knowledge Service"
    
    log_success "All services are available"
    log_divider
}

# Pretty print JSON
pprint_json() {
    echo "$1" | jq .
}

# Execute with error handling
execute_with_retry() {
    local command=$1
    local max_retries=${2:-3}
    local delay=${3:-2}
    
    local retry_count=0
    local exit_code=0
    
    while [ $retry_count -lt $max_retries ]; do
        log_debug "Executing command (attempt $((retry_count + 1))/$max_retries)"
        
        eval "$command"
        exit_code=$?
        
        if [ $exit_code -eq 0 ]; then
            log_debug "Command executed successfully"
            return 0
        fi
        
        retry_count=$((retry_count + 1))
        if [ $retry_count -lt $max_retries ]; then
            log_warning "Command failed, retrying in ${delay}s..."
            sleep $delay
        fi
    done
    
    log_error "Command failed after $max_retries attempts"
    return $exit_code
}