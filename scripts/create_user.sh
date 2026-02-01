#!/bin/bash

# Load helper functions
source "$(dirname "$0")/helper.sh"

# Run setup checks
setup_checks

# Export token
export_token

# Create invitation for user
log_step "Creating invitation for user..."
INVITATION_RESPONSE=$(execute_with_retry \
    "curl -L -s -X POST \"$AUTH_SERVICE_URL/api/v1/invitations/\" \
        -H \"Authorization: Bearer \$ADMIN_TOKEN\" \
        -H \"Content-Type: application/json\" \
        -d '{
            \"email\": \"user@company.com\",
            \"employee_id\": \"EMP001\",
            \"first_name\": \"John\",
            \"last_name\": \"Doe\",
            \"department\": \"Engineering\",
            \"position\": \"Software Engineer\",
            \"level\": \"JUNIOR\",
            \"expires_in_days\": 7
        }'" 3 2)

log_debug "Invitation response: $INVITATION_RESPONSE"

INVITATION_TOKEN=$(echo "$INVITATION_RESPONSE" | jq -r '.token')
if [ -z "$INVITATION_TOKEN" ] || [ "$INVITATION_TOKEN" = "null" ]; then
    log_error "Failed to get invitation token"
    exit 1
fi

log_info "Invitation token: $INVITATION_TOKEN"

# Register user using invitation token
log_step "Registering user with invitation..."
USER_RESPONSE=$(execute_with_retry \
    "curl -L -s -X POST \"$AUTH_SERVICE_URL/api/v1/auth/register/$INVITATION_TOKEN\" \
        -H \"Content-Type: application/json\" \
        -H \"X-API-Key: $API_KEY\" \
        -d '{
            \"telegram_id\": \"769517888\",
            \"username\": \"romanandr\",
            \"phone\": \"+1234567890\"
        }'" 3 2)

if echo "$USER_RESPONSE" | jq -e '.access_token' > /dev/null 2>&1; then
    log_success "User registered successfully"
    log_info "Access token: $(echo "$USER_RESPONSE" | jq -r '.access_token')"
else
    log_error "Failed to register user"
    log_debug "Response: $USER_RESPONSE"
    exit 1
fi

log_divider