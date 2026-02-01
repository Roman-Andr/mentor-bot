#!/bin/bash

# Load helper functions
source "$(dirname "$0")/helper.sh"

# Run setup checks
setup_checks

# Export token
export_token

# Get HR user ID (optional, for assigning HR to invitation)
log_step "Getting HR user ID..."
HR_USER_RESPONSE=$(execute_with_retry \
    "curl -L -s -X GET \"$AUTH_SERVICE_URL/api/v1/users/by-email/hr@company.com\" \
        -H \"Authorization: Bearer \$ADMIN_TOKEN\"" 3 2)

HR_USER_ID=$(echo "$HR_USER_RESPONSE" | jq -r '.id')
if [ -n "$HR_USER_ID" ] && [ "$HR_USER_ID" != "null" ]; then
    log_info "HR User ID found: $HR_USER_ID"
    HR_ASSIGNMENT="\"hr_id\": $HR_USER_ID,"
else
    log_warning "HR user not found, creating invitation without HR assignment"
    HR_ASSIGNMENT=""
fi

# Create invitation for user
log_step "Creating invitation..."
INVITATION_RESPONSE=$(execute_with_retry \
    "curl -L -s -X POST \"$AUTH_SERVICE_URL/api/v1/invitations/\" \
        -H \"Authorization: Bearer \$ADMIN_TOKEN\" \
        -H \"Content-Type: application/json\" \
        -d '{
            \"email\": \"romanandr07@yandex.ru\",
            \"employee_id\": \"EMP002\",
            \"first_name\": \"Roman\",
            \"last_name\": \"Andrusevich\",
            \"department\": \"Engineering\",
            \"position\": \"Software Engineer\",
            \"level\": \"JUNIOR\",
            \"expires_in_days\": 7,
            $HR_ASSIGNMENT
            \"notes\": \"Invitation created via script\"
        }'" 3 2)

log_debug "Full invitation response: $INVITATION_RESPONSE"

# Extract invitation details
INVITATION_ID=$(echo "$INVITATION_RESPONSE" | jq -r '.id')
INVITATION_TOKEN=$(echo "$INVITATION_RESPONSE" | jq -r '.token')
INVITATION_EXPIRES=$(echo "$INVITATION_RESPONSE" | jq -r '.expires_at')
INVITATION_STATUS=$(echo "$INVITATION_RESPONSE" | jq -r '.status')
INVITATION_URL="$AUTH_SERVICE_URL/api/v1/auth/register/$INVITATION_TOKEN"

if [ -z "$INVITATION_TOKEN" ] || [ "$INVITATION_TOKEN" = "null" ]; then
    log_error "Failed to create invitation"
    log_debug "Response: $INVITATION_RESPONSE"
    exit 1
fi

log_success "Invitation created successfully!"
log_divider
log_info "Invitation ID: $INVITATION_ID"
log_info "Token: $INVITATION_TOKEN"
log_info "Status: $INVITATION_STATUS"
log_info "Expires: $INVITATION_EXPIRES"
log_info "Registration URL: $INVITATION_URL"
log_divider

# Show invitation details
log_step "Invitation details:"
curl -L -s -X GET "$AUTH_SERVICE_URL/api/v1/invitations/$INVITATION_ID" \
    -H "Authorization: Bearer $ADMIN_TOKEN" | jq .

log_divider

log_success "Invitation created. Share the token or URL with the user to complete registration."
log_info "Token: $INVITATION_TOKEN"
log_info "URL: https://t.me/company_hr_mentor_bot?start=$INVITATION_TOKEN"