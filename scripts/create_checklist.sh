#!/bin/bash

# Load helper functions
source "$(dirname "$0")/helper.sh"

# Run setup checks
setup_checks

# Export token
export_token

# Get HR user ID
log_step "Getting HR user ID..."
HR_USER_RESPONSE=$(execute_with_retry \
    "curl -L -s -X GET \"$AUTH_SERVICE_URL/api/v1/users/by-email/hr@company.com\" \
        -H \"Authorization: Bearer \$ADMIN_TOKEN\"" 3 2)

HR_USER_ID=$(echo "$HR_USER_RESPONSE" | jq -r '.id')
if [ -z "$HR_USER_ID" ] || [ "$HR_USER_ID" = "null" ]; then
    log_error "Failed to get HR user ID"
    exit 1
fi
log_info "HR User ID: $HR_USER_ID"

# Get the regular user ID (created via invitation)
log_step "Getting regular user ID..."
USER_RESPONSE=$(execute_with_retry \
    "curl -L -s -X GET \"$AUTH_SERVICE_URL/api/v1/users/by-email/user@company.com\" \
        -H \"Authorization: Bearer \$ADMIN_TOKEN\"" 3 2)

USER_ID=$(echo "$USER_RESPONSE" | jq -r '.id')
USER_EMPLOYEE_ID=$(echo "$USER_RESPONSE" | jq -r '.employee_id')

if [ -z "$USER_ID" ] || [ "$USER_ID" = "null" ]; then
    log_error "Failed to get regular user ID"
    exit 1
fi
log_info "User ID: $USER_ID, Employee ID: $USER_EMPLOYEE_ID"

# Create a template
log_step "Creating checklist template..."
TEMPLATE_RESPONSE=$(execute_with_retry \
    "curl -L -s -X POST \"$CHECKLISTS_SERVICE_URL/api/v1/templates/\" \
        -H \"Authorization: Bearer \$ADMIN_TOKEN\" \
        -H \"Content-Type: application/json\" \
        -d '{
            \"name\": \"Onboarding Checklist\",
            \"description\": \"Standard onboarding for new employees\",
            \"department\": \"Engineering\",
            \"position\": \"Software Engineer\",
            \"level\": \"JUNIOR\",
            \"duration_days\": 30,
            \"task_categories\": [\"INTRODUCTION\", \"DOCUMENTATION\", \"TECHNICAL\"],
            \"default_assignee_role\": \"MENTOR\",
            \"status\": \"ACTIVE\",
            \"is_default\": true
        }'" 3 2)

TEMPLATE_ID=$(echo "$TEMPLATE_RESPONSE" | jq -r '.id')
if [ -z "$TEMPLATE_ID" ] || [ "$TEMPLATE_ID" = "null" ]; then
    log_error "Failed to create template"
    log_debug "Response: $TEMPLATE_RESPONSE"
    exit 1
fi
log_success "Template created with ID: $TEMPLATE_ID"

# Add tasks to template
log_step "Adding tasks to template..."

# Task 1: Welcome meeting
execute_with_retry \
    "curl -L -s -X POST \"$CHECKLISTS_SERVICE_URL/api/v1/templates/$TEMPLATE_ID/tasks\" \
        -H \"Authorization: Bearer \$ADMIN_TOKEN\" \
        -H \"Content-Type: application/json\" \
        -d '{
            \"template_id\": $TEMPLATE_ID,
            \"title\": \"Welcome Meeting with Manager\",
            \"description\": \"Meet with your direct manager to discuss role expectations\",
            \"instructions\": \"Schedule a 30-minute meeting with your manager\",
            \"category\": \"INTRODUCTION\",
            \"order\": 1,
            \"due_days\": 1,
            \"estimated_minutes\": 30,
            \"resources\": [{\"type\": \"link\", \"title\": \"Meeting Guide\", \"url\": \"https://example.com/meeting-guide\"}],
            \"required_documents\": [],
            \"assignee_role\": \"MENTOR\",
            \"auto_assign\": true,
            \"depends_on\": []
        }' | jq ." 3 2

# Task 2: Complete documentation
execute_with_retry \
    "curl -L -s -X POST \"$CHECKLISTS_SERVICE_URL/api/v1/templates/$TEMPLATE_ID/tasks\" \
        -H \"Authorization: Bearer \$ADMIN_TOKEN\" \
        -H \"Content-Type: application/json\" \
        -d '{
            \"template_id\": $TEMPLATE_ID,
            \"title\": \"Complete HR Documentation\",
            \"description\": \"Fill out all required HR forms and documentation\",
            \"instructions\": \"Visit the HR portal and complete all pending forms\",
            \"category\": \"DOCUMENTATION\",
            \"order\": 2,
            \"due_days\": 3,
            \"estimated_minutes\": 60,
            \"resources\": [{\"type\": \"link\", \"title\": \"HR Portal\", \"url\": \"https://hr.company.com\"}],
            \"required_documents\": [\"employment_contract\", \"tax_forms\", \"benefits_selection\"],
            \"assignee_role\": \"HR\",
            \"auto_assign\": true,
            \"depends_on\": []
        }' | jq ." 3 2

# Task 3: Technical setup
execute_with_retry \
    "curl -L -s -X POST \"$CHECKLISTS_SERVICE_URL/api/v1/templates/$TEMPLATE_ID/tasks\" \
        -H \"Authorization: Bearer \$ADMIN_TOKEN\" \
        -H \"Content-Type: application/json\" \
        -d '{
            \"template_id\": $TEMPLATE_ID,
            \"title\": \"Technical Environment Setup\",
            \"description\": \"Set up development environment and access credentials\",
            \"instructions\": \"Follow the technical onboarding guide to set up your workstation\",
            \"category\": \"TECHNICAL\",
            \"order\": 3,
            \"due_days\": 5,
            \"estimated_minutes\": 120,
            \"resources\": [{\"type\": \"link\", \"title\": \"Technical Guide\", \"url\": \"https://dev.company.com/onboarding\"}],
            \"required_documents\": [],
            \"assignee_role\": \"MENTOR\",
            \"auto_assign\": true,
            \"depends_on\": []
        }' | jq ." 3 2

log_success "Tasks added to template"

# Create checklist for the regular user with HR assigned
log_step "Creating checklist for user $USER_ID..."
CHECKLIST_RESPONSE=$(execute_with_retry \
    "curl -L -s -X POST \"$CHECKLISTS_SERVICE_URL/api/v1/checklists/\" \
        -H \"Authorization: Bearer \$ADMIN_TOKEN\" \
        -H \"Content-Type: application/json\" \
        -d '{
            \"user_id\": $USER_ID,
            \"employee_id\": \"$USER_EMPLOYEE_ID\",
            \"template_id\": $TEMPLATE_ID,
            \"start_date\": \"'\"\$(date -u +\"%Y-%m-%dT%H:%M:%SZ\")\"'\",
            \"mentor_id\": 1,
            \"hr_id\": $HR_USER_ID,
            \"notes\": \"Onboarding checklist for new software engineer\"
        }'" 3 2)

CHECKLIST_ID=$(echo "$CHECKLIST_RESPONSE" | jq -r '.id')
if [ -z "$CHECKLIST_ID" ] || [ "$CHECKLIST_ID" = "null" ]; then
    log_error "Failed to create checklist"
    log_debug "Response: $CHECKLIST_RESPONSE"
    exit 1
fi

log_success "Checklist created successfully with ID: $CHECKLIST_ID"

# Show checklist details
log_step "Checklist details:"
curl -L -s -X GET "$CHECKLISTS_SERVICE_URL/api/v1/checklists/$CHECKLIST_ID" \
    -H "Authorization: Bearer $ADMIN_TOKEN" | jq .

log_divider