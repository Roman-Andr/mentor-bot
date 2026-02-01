#!/bin/bash

# Load helper functions
source "$(dirname "$0")/helper.sh"

# Run setup checks
setup_checks

# Export token
export_token

# Create HR user
log_step "Creating HR user..."
RESPONSE=$(execute_with_retry \
    "curl -L -s -X POST \"$AUTH_SERVICE_URL/api/v1/users/\" \
        -H \"Authorization: Bearer \$ADMIN_TOKEN\" \
        -H \"Content-Type: application/json\" \
        -d '{
            \"email\": \"hr@company.com\",
            \"first_name\": \"Jane\",
            \"last_name\": \"Smith\",
            \"employee_id\": \"HR001\",
            \"password\": \"\$2b\$12\$P.jE8VXPZ74Uj/vFz2Y.Xe7ShOwgl6hQ34vgl7DRts1ntnC1Q97i.\",
            \"role\": \"HR\",
            \"department\": \"Human Resources\",
            \"position\": \"HR Manager\",
            \"level\": \"SENIOR\"
        }'" 3 2)

if echo "$RESPONSE" | jq -e '.id' > /dev/null 2>&1; then
    log_success "HR user created successfully"
    log_info "User ID: $(echo "$RESPONSE" | jq -r '.id')"
else
    log_error "Failed to create HR user"
    log_debug "Response: $RESPONSE"
    exit 1
fi

log_divider