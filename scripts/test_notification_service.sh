#!/bin/bash
# Testing Notification Service: sending, scheduling, history

# Load common functions
source "$(dirname "$0")/helper.sh"

# ----------------------------------------------------------------------
# 1. Environment Setup
# ----------------------------------------------------------------------

log_divider
log_step "🚀 Starting Notification Service testing"

# Perform basic checks (presence of jq, curl, waiting for auth/checklists/knowledge services)
setup_checks

# Additionally wait for Notification Service
wait_for_service "$NOTIFICATION_SERVICE_URL" "Notification Service" 30 2

# Get admin token
export_token

# ----------------------------------------------------------------------
# 2. Get information about the current user (admin)
# ----------------------------------------------------------------------
log_step "Getting current user information"
USER_INFO=$(execute_with_retry \
    "curl -L -s -X GET \"$AUTH_SERVICE_URL/api/v1/auth/me\" \
        -H \"Authorization: Bearer \$ADMIN_TOKEN\"" 3 2)

ADMIN_ID=$(echo "$USER_INFO" | jq -r '.id')
ADMIN_EMAIL=$(echo "$USER_INFO" | jq -r '.email')
if [ -z "$ADMIN_ID" ] || [ "$ADMIN_ID" = "null" ]; then
    log_error "Failed to get admin ID"
    exit 1
fi
log_info "Admin ID: $ADMIN_ID, Email: $ADMIN_EMAIL"

# ----------------------------------------------------------------------
# 3. Sending an immediate notification (send)
# ----------------------------------------------------------------------
log_step "Sending immediate notification (EMAIL channel)"
SEND_RESPONSE=$(execute_with_retry \
    "curl -L -s -X POST \"$NOTIFICATION_SERVICE_URL/api/v1/notifications/send\" \
        -H \"Authorization: Bearer \$ADMIN_TOKEN\" \
        -H \"Content-Type: application/json\" \
        -d '{
            \"user_id\": $ADMIN_ID,
            \"recipient_email\": \"$ADMIN_EMAIL\",
            \"type\": \"GENERAL\",
            \"channel\": \"EMAIL\",
            \"subject\": \"Test Notification\",
            \"body\": \"This is a test notification sent at $(date)\",
            \"data\": {\"test\": true}
        }'" 3 2)

echo "$SEND_RESPONSE" | jq .
NOTIFICATION_ID=$(echo "$SEND_RESPONSE" | jq -r '.id')
if [ "$NOTIFICATION_ID" = "null" ] || [ -z "$NOTIFICATION_ID" ]; then
    log_error "Failed to send notification"
    exit 1
fi
log_success "Immediate notification created, ID: $NOTIFICATION_ID"

# ----------------------------------------------------------------------
# 4. Creating a scheduled notification in 10 seconds
# ----------------------------------------------------------------------
SCHEDULED_TIME=$(date -u -d "10 seconds" +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || date -u -v+10S +"%Y-%m-%dT%H:%M:%SZ")
log_step "Creating scheduled notification for $SCHEDULED_TIME"
SCHEDULE_RESPONSE=$(execute_with_retry \
    "curl -L -s -X POST \"$NOTIFICATION_SERVICE_URL/api/v1/notifications/schedule\" \
        -H \"Authorization: Bearer \$ADMIN_TOKEN\" \
        -H \"Content-Type: application/json\" \
        -d '{
            \"user_id\": $ADMIN_ID,
            \"recipient_email\": \"$ADMIN_EMAIL\",
            \"type\": \"GENERAL\",
            \"channel\": \"EMAIL\",
            \"subject\": \"Scheduled Test\",
            \"body\": \"This is a scheduled notification\",
            \"data\": {\"test\": true},
            \"scheduled_time\": \"$SCHEDULED_TIME\"
        }'" 3 2)

echo "$SCHEDULE_RESPONSE" | jq .
SCHEDULED_ID=$(echo "$SCHEDULE_RESPONSE" | jq -r '.id')
if [ "$SCHEDULED_ID" = "null" ] || [ -z "$SCHEDULED_ID" ]; then
    log_error "Failed to create scheduled notification"
    exit 1
fi
log_success "Scheduled notification created, ID: $SCHEDULED_ID"

# ----------------------------------------------------------------------
# 5. Getting the current user's notification history
# ----------------------------------------------------------------------
log_step "Getting notification history"
HISTORY_RESPONSE=$(execute_with_retry \
    "curl -L -s -X GET \"$NOTIFICATION_SERVICE_URL/api/v1/notifications/history?skip=0&limit=10\" \
        -H \"Authorization: Bearer \$ADMIN_TOKEN\"" 3 2)

echo "$HISTORY_RESPONSE" | jq .
TOTAL=$(echo "$HISTORY_RESPONSE" | jq '. | length')
log_success "Notifications retrieved in history: $TOTAL"

# ----------------------------------------------------------------------
# 6. Getting history for a specific user (available only to HR/ADMIN)
# ----------------------------------------------------------------------
log_step "Getting notification history for user ID=$ADMIN_ID"
USER_HISTORY_RESPONSE=$(execute_with_retry \
    "curl -L -s -X GET \"$NOTIFICATION_SERVICE_URL/api/v1/notifications/history/$ADMIN_ID?skip=0&limit=10\" \
        -H \"Authorization: Bearer \$ADMIN_TOKEN\"" 3 2)

echo "$USER_HISTORY_RESPONSE" | jq .
USER_TOTAL=$(echo "$USER_HISTORY_RESPONSE" | jq '. | length')
log_success "Notifications retrieved for user $ADMIN_ID: $USER_TOTAL"

# ----------------------------------------------------------------------
# 7. Waiting for scheduled notification to be processed (15 seconds with buffer)
# ----------------------------------------------------------------------
log_step "Waiting 15 seconds for scheduled notification to be processed..."
sleep 15

# ----------------------------------------------------------------------
# 8. Checking that the scheduled notification was processed
# ----------------------------------------------------------------------
log_step "Checking status of scheduled notification"
HISTORY_AFTER=$(curl -L -s -X GET "$NOTIFICATION_SERVICE_URL/api/v1/notifications/history?skip=0&limit=20" \
    -H "Authorization: Bearer $ADMIN_TOKEN")

FOUND=$(echo "$HISTORY_AFTER" | jq '.[] | select(.subject == "Scheduled Test")')
if [ -n "$FOUND" ]; then
    STATUS=$(echo "$FOUND" | jq -r '.status')
    log_success "Scheduled notification processed, status: $STATUS"
else
    log_error "Scheduled notification not found in history after waiting"
fi

# ----------------------------------------------------------------------
# Completion
# ----------------------------------------------------------------------
log_divider
log_success "✅ Notification Service testing successfully completed!"
log_divider