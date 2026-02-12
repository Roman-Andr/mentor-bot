#!/bin/bash
# Testing Escalation Service: creation, assignment, update, resolution, deletion of escalations

# Load common functions
source "$(dirname "$0")/helper.sh"

# ----------------------------------------------------------------------
# 1. Environment Setup
# ----------------------------------------------------------------------
log_divider
log_step "🚀 Starting Escalation Service testing"

# Perform basic checks (presence of jq, curl, waiting for auth/checklists/knowledge services)
setup_checks

# Additionally wait for Escalation Service
wait_for_service "$ESCALATION_SERVICE_URL" "Escalation Service" 30 2

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
# 3. Creating escalation requests
# ----------------------------------------------------------------------
log_step "Creating first escalation request (HR, MANUAL)"
CREATE_RESPONSE1=$(execute_with_retry \
    "curl -L -s -X POST \"$ESCALATION_SERVICE_URL/api/v1/escalations/\" \
        -H \"Authorization: Bearer \$ADMIN_TOKEN\" \
        -H \"Content-Type: application/json\" \
        -d '{
            \"user_id\": $ADMIN_ID,
            \"type\": \"HR\",
            \"source\": \"MANUAL\",
            \"reason\": \"Test escalation 1 (HR)\",
            \"metadata\": {\"test\": true}
        }'" 3 2)

echo "$CREATE_RESPONSE1" | jq .
ESCALATION_ID1=$(echo "$CREATE_RESPONSE1" | jq -r '.id')
if [ "$ESCALATION_ID1" = "null" ] || [ -z "$ESCALATION_ID1" ]; then
    log_error "Failed to create first escalation"
    exit 1
fi
log_success "First escalation created, ID: $ESCALATION_ID1"

log_step "Creating second escalation request (IT, AUTO_OVERDUE)"
CREATE_RESPONSE2=$(execute_with_retry \
    "curl -L -s -X POST \"$ESCALATION_SERVICE_URL/api/v1/escalations/\" \
        -H \"Authorization: Bearer \$ADMIN_TOKEN\" \
        -H \"Content-Type: application/json\" \
        -d '{
            \"user_id\": $ADMIN_ID,
            \"type\": \"IT\",
            \"source\": \"AUTO_OVERDUE\",
            \"reason\": \"Task overdue by more than 3 days\",
            \"metadata\": {\"task_id\": 12345}
        }'" 3 2)

echo "$CREATE_RESPONSE2" | jq .
ESCALATION_ID2=$(echo "$CREATE_RESPONSE2" | jq -r '.id')
if [ "$ESCALATION_ID2" = "null" ] || [ -z "$ESCALATION_ID2" ]; then
    log_error "Failed to create second escalation"
    exit 1
fi
log_success "Second escalation created, ID: $ESCALATION_ID2"

# ----------------------------------------------------------------------
# 4. Getting list of escalations with filtering
# ----------------------------------------------------------------------
log_step "Getting list of escalations (no filters)"
LIST_RESPONSE=$(execute_with_retry \
    "curl -L -s -X GET \"$ESCALATION_SERVICE_URL/api/v1/escalations/?skip=0&limit=10\" \
        -H \"Authorization: Bearer \$ADMIN_TOKEN\"" 3 2)

TOTAL=$(echo "$LIST_RESPONSE" | jq -r '.total')
log_success "Total escalations in the system: $TOTAL"

log_step "Filtering by type IT"
FILTER_RESPONSE=$(execute_with_retry \
    "curl -L -s -X GET \"$ESCALATION_SERVICE_URL/api/v1/escalations/?type=IT\" \
        -H \"Authorization: Bearer \$ADMIN_TOKEN\"" 3 2)

IT_COUNT=$(echo "$FILTER_RESPONSE" | jq -r '.total')
if [ "$IT_COUNT" -lt 1 ]; then
    log_error "No escalations with type IT found"
else
    log_success "Escalations with type IT found: $IT_COUNT"
fi

# ----------------------------------------------------------------------
# 5. Getting a specific escalation by ID
# ----------------------------------------------------------------------
log_step "Getting escalation by ID = $ESCALATION_ID1"
GET_RESPONSE=$(execute_with_retry \
    "curl -L -s -X GET \"$ESCALATION_SERVICE_URL/api/v1/escalations/$ESCALATION_ID1\" \
        -H \"Authorization: Bearer \$ADMIN_TOKEN\"" 3 2)

RETRIEVED_STATUS=$(echo "$GET_RESPONSE" | jq -r '.status')
if [ "$RETRIEVED_STATUS" != "PENDING" ]; then
    log_error "Expected status PENDING, got $RETRIEVED_STATUS"
else
    log_success "Status is correct: $RETRIEVED_STATUS"
fi

# ----------------------------------------------------------------------
# 6. Assigning escalation to admin
# ----------------------------------------------------------------------
log_step "Assigning escalation $ESCALATION_ID1 to user $ADMIN_ID"
ASSIGN_RESPONSE=$(execute_with_retry \
    "curl -L -s -X POST \"$ESCALATION_SERVICE_URL/api/v1/escalations/$ESCALATION_ID1/assign/$ADMIN_ID\" \
        -H \"Authorization: Bearer \$ADMIN_TOKEN\"" 3 2)

ASSIGNED_TO=$(echo "$ASSIGN_RESPONSE" | jq -r '.assigned_to')
ASSIGNED_STATUS=$(echo "$ASSIGN_RESPONSE" | jq -r '.status')
if [ "$ASSIGNED_TO" != "$ADMIN_ID" ] || [ "$ASSIGNED_STATUS" != "ASSIGNED" ]; then
    log_error "Assignment error: assigned_to=$ASSIGNED_TO, status=$ASSIGNED_STATUS"
else
    log_success "Escalation assigned, status: $ASSIGNED_STATUS"
fi

# ----------------------------------------------------------------------
# 7. Updating escalation (changing status to IN_PROGRESS)
# ----------------------------------------------------------------------
log_step "Updating escalation $ESCALATION_ID1 status to IN_PROGRESS"
UPDATE_RESPONSE=$(execute_with_retry \
    "curl -L -s -X PATCH \"$ESCALATION_SERVICE_URL/api/v1/escalations/$ESCALATION_ID1\" \
        -H \"Authorization: Bearer \$ADMIN_TOKEN\" \
        -H \"Content-Type: application/json\" \
        -d '{
            \"status\": \"IN_PROGRESS\",
            \"resolution_note\": \"Started investigating\"
        }'" 3 2)

UPDATED_STATUS=$(echo "$UPDATE_RESPONSE" | jq -r '.status')
if [ "$UPDATED_STATUS" != "IN_PROGRESS" ]; then
    log_error "Failed to update status to IN_PROGRESS"
else
    log_success "Status updated: $UPDATED_STATUS"
fi

# ----------------------------------------------------------------------
# 8. Resolving escalation
# ----------------------------------------------------------------------
log_step "Resolving escalation $ESCALATION_ID1 (RESOLVED)"
RESOLVE_RESPONSE=$(execute_with_retry \
    "curl -L -s -X POST \"$ESCALATION_SERVICE_URL/api/v1/escalations/$ESCALATION_ID1/resolve\" \
        -H \"Authorization: Bearer \$ADMIN_TOKEN\"" 3 2)

RESOLVED_STATUS=$(echo "$RESOLVE_RESPONSE" | jq -r '.status')
RESOLVED_AT=$(echo "$RESOLVE_RESPONSE" | jq -r '.resolved_at')
if [ "$RESOLVED_STATUS" != "RESOLVED" ] || [ "$RESOLVED_AT" = "null" ]; then
    log_error "Escalation not resolved correctly"
else
    log_success "Escalation resolved, resolved_at: $RESOLVED_AT"
fi

# ----------------------------------------------------------------------
# 9. Getting current user's escalations
# ----------------------------------------------------------------------
log_step "Getting user escalations (GET /user/$ADMIN_ID)"
USER_ESC_RESPONSE=$(execute_with_retry \
    "curl -L -s -X GET \"$ESCALATION_SERVICE_URL/api/v1/escalations/user/$ADMIN_ID?skip=0&limit=5\" \
        -H \"Authorization: Bearer \$ADMIN_TOKEN\"" 3 2)

USER_ESC_COUNT=$(echo "$USER_ESC_RESPONSE" | jq 'length')
log_success "Escalations found for user $ADMIN_ID: $USER_ESC_COUNT"

# ----------------------------------------------------------------------
# 10. Getting escalations assigned to me
# ----------------------------------------------------------------------
log_step "Getting escalations assigned to current user (GET /assigned-to-me)"
ASSIGNED_RESPONSE=$(execute_with_retry \
    "curl -L -s -X GET \"$ESCALATION_SERVICE_URL/api/v1/escalations/assigned-to-me?skip=0&limit=5\" \
        -H \"Authorization: Bearer \$ADMIN_TOKEN\"" 3 2)

ASSIGNED_COUNT=$(echo "$ASSIGNED_RESPONSE" | jq 'length')
if [ "$ASSIGNED_COUNT" -lt 1 ]; then
    log_warning "No assigned escalations (maybe all are already resolved)"
else
    log_success "Assigned escalations: $ASSIGNED_COUNT"
fi

# ----------------------------------------------------------------------
# 11. Deleting the second escalation (admin)
# ----------------------------------------------------------------------
log_step "Deleting escalation $ESCALATION_ID2 (admin)"
DELETE_RESPONSE=$(curl -L -s -X DELETE "$ESCALATION_SERVICE_URL/api/v1/escalations/$ESCALATION_ID2" \
    -H "Authorization: Bearer $ADMIN_TOKEN")

if echo "$DELETE_RESPONSE" | jq -e '.message' > /dev/null 2>&1; then
    log_success "Escalation $ESCALATION_ID2 deleted"
else
    log_error "Failed to delete escalation $ESCALATION_ID2"
    echo "$DELETE_RESPONSE" | jq .
fi

# ----------------------------------------------------------------------
# 12. Checking that the deleted escalation is not found (404)
# ----------------------------------------------------------------------
log_step "Checking absence of deleted escalation $ESCALATION_ID2"
HTTP_CODE=$(curl -L -s -o /dev/null -w "%{http_code}" \
    -X GET "$ESCALATION_SERVICE_URL/api/v1/escalations/$ESCALATION_ID2" \
    -H "Authorization: Bearer $ADMIN_TOKEN")

if [ "$HTTP_CODE" -eq 404 ]; then
    log_success "Correctly received 404 for deleted escalation"
else
    log_error "Expected code 404, got $HTTP_CODE"
fi

# ----------------------------------------------------------------------
# 13. Additional: attempt to create escalation for another user (should be allowed for admin)
# ----------------------------------------------------------------------
log_step "Creating escalation for another user (user_id=999999) – admin can"
CREATE_OTHER=$(execute_with_retry \
    "curl -L -s -X POST \"$ESCALATION_SERVICE_URL/api/v1/escalations/\" \
        -H \"Authorization: Bearer \$ADMIN_TOKEN\" \
        -H \"Content-Type: application/json\" \
        -d '{
            \"user_id\": 999999,
            \"type\": \"GENERAL\",
            \"source\": \"MANUAL\",
            \"reason\": \"Escalation for non-existent user\"
        }'" 3 2)

OTHER_ID=$(echo "$CREATE_OTHER" | jq -r '.id')
if [ "$OTHER_ID" = "null" ] || [ -z "$OTHER_ID" ]; then
    log_warning "Failed to create escalation for another user (possibly database foreign key constraint?)"
else
    log_success "Escalation created for user_id=999999, ID: $OTHER_ID"
    # Delete it
    curl -L -s -X DELETE "$ESCALATION_SERVICE_URL/api/v1/escalations/$OTHER_ID" \
        -H "Authorization: Bearer $ADMIN_TOKEN" > /dev/null
fi

# ----------------------------------------------------------------------
# Completion
# ----------------------------------------------------------------------
log_divider
log_success "✅ Escalation Service testing successfully completed!"
log_divider