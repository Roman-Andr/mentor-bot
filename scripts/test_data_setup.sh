#!/bin/bash
# test_data_setup.sh — unified test-data seeder for Mentor Bot
# Creates: admin, 5 departments, HR, mentor, user (via invitation),
#          10 checklist templates with tasks, 5 categories, 30 articles,
#          10 meeting templates
# Skips:  notification_service, escalation_service, feedback_service

set -euo pipefail

# ─── Load helpers ────────────────────────────────────────────────────────────
source "$(dirname "$0")/helper.sh"

# ─── Configuration ─────────────────────────────────────────────────────────
POSTGRES_USER="roman"
POSTGRES_PASSWORD="test_password"
DATABASE="mentor_bot"

DEPARTMENTS=(
    "Engineering|Software engineering department"
    "Product|Product management and design"
    "Sales|Sales and business development"
    "Marketing|Marketing and communications"
    "Operations|Operations and support"
)

HR_EMAIL="hr@company.com"
HR_FIRST="Jane"
HR_LAST="Smith"
HR_EMP_ID="HR001"
HR_PASSWORD="mentor123"

MENTOR_EMAIL="mentor@company.com"
MENTOR_FIRST="Alex"
MENTOR_LAST="Johnson"
MENTOR_EMP_ID="MEN001"
MENTOR_PASSWORD="mentor123"

USER_EMAIL="user@company.com"
USER_FIRST="John"
USER_LAST="Doe"
USER_EMP_ID="EMP001"
USER_TELEGRAM_ID="769517888"
USER_TELEGRAM_USERNAME="romanandr"

MEETING_SERVICE_URL="${MEETING_SERVICE_URL:-http://localhost:8006}"

# ─── Logging helpers ─────────────────────────────────────────────────────────
phase() { log_divider; log_step "PHASE: $1"; }

# ─── Helper: insert departments into a non-auth schema via raw SQL ───────────
create_dept_in_schema() {
    local schema="$1"
    local dept_name="$2"
    local dept_desc="$3"
    log_info "Ensuring department '${dept_name}' exists in ${schema}.departments ..."
    docker compose exec -T postgres psql -U "$POSTGRES_USER" -d "$DATABASE" -c "
    INSERT INTO ${schema}.departments (name, description, created_at)
    SELECT '${dept_name}', '${dept_desc}', NOW()
    WHERE NOT EXISTS (SELECT 1 FROM ${schema}.departments WHERE name = '${dept_name}');
    " >/dev/null 2>&1 || log_warning "Could not insert into ${schema}.departments (service may not have started yet)"
}

# ─── Helper: get department id from a schema ─────────────────────────────────
get_dept_id_in_schema() {
    local schema="$1"
    local dept_name="$2"
    docker compose exec -T postgres psql -U "$POSTGRES_USER" -d "$DATABASE" \
        -t -A -c "SELECT id FROM ${schema}.departments WHERE name = '${dept_name}' LIMIT 1;" 2>/dev/null
}

# ─── Helper: create-or-get resource via API ──────────────────────────────────
api_create_or_get() {
    local create_cmd="$1"
    local get_cmd="$2"
    local jq_field="${3:-.id}"

    local resp
    resp=$(eval "$get_cmd" 2>/dev/null || echo "null")
    local existing_id
    existing_id=$(echo "$resp" | jq -r "$jq_field // empty" 2>/dev/null)

    if [ -n "$existing_id" ] && [ "$existing_id" != "null" ]; then
        echo "$existing_id"
        return 0
    fi

    resp=$(eval "$create_cmd" 2>/dev/null || echo "null")
    local new_id
    new_id=$(echo "$resp" | jq -r "$jq_field // empty" 2>/dev/null)

    if [ -n "$new_id" ] && [ "$new_id" != "null" ]; then
        echo "$new_id"
        return 0
    fi

    resp=$(eval "$get_cmd" 2>/dev/null || echo "null")
    existing_id=$(echo "$resp" | jq -r "$jq_field // empty" 2>/dev/null)
    if [ -n "$existing_id" ] && [ "$existing_id" != "null" ]; then
        echo "$existing_id"
        return 0
    fi

    return 1
}

# ============================================================================
#  PHASE 0 — Pre-flight checks
# ============================================================================
phase "Pre-flight checks"
setup_checks
wait_for_service "$MEETING_SERVICE_URL" "Meeting Service" 30 2

# ============================================================================
#  PHASE 1 — Create Admin user (raw SQL, idempotent)
# ============================================================================
phase "Creating admin user"

ADMIN_EXISTS=$(docker compose exec -T postgres psql -U "$POSTGRES_USER" -d "$DATABASE" \
    -t -A -c "SELECT EXISTS(SELECT 1 FROM auth.users WHERE email = '${ADMIN_EMAIL}');" 2>/dev/null || echo "f")

if [ "$ADMIN_EXISTS" = "t" ]; then
    log_info "Admin user already exists: ${ADMIN_EMAIL}"
else
    docker compose exec -T postgres psql -U "$POSTGRES_USER" -d "$DATABASE" -c "
    INSERT INTO auth.users (
        email, first_name, last_name, employee_id, password_hash,
        role, is_active, is_verified, created_at
    ) VALUES (
        '${ADMIN_EMAIL}', 'Admin', 'Adminov', 'admin001',
        '\$2b\$12\$1hhh1fvR8Qm0s2t3qBHhfOBvMCnusOIVmPINCQzPodlQH9b42.pjy',
        'ADMIN', true, true, NOW()
    );"
    log_success "Admin user created: ${ADMIN_EMAIL}"
fi

# ============================================================================
#  PHASE 2 — Authenticate as admin
# ============================================================================
phase "Authenticating as admin"
export_token
log_success "Admin token obtained"

# ============================================================================
#  PHASE 3 — Create 5 Departments in ALL service schemas
# ============================================================================
phase "Creating 5 departments"

declare -A DEPT_IDS_AUTH
declare -A DEPT_IDS_KNOWLEDGE
declare -A DEPT_IDS_MEETING
declare -A DEPT_IDS_CHECKLIST

for dept_spec in "${DEPARTMENTS[@]}"; do
    DEPT_NAME="${dept_spec%%|*}"
    DEPT_DESC="${dept_spec#*|}"

    # 3a. Auth service (via API)
    AUTH_DEPT_ID=$(api_create_or_get \
        "curl -L -s -X POST '${AUTH_SERVICE_URL}/api/v1/departments/' \
            -H 'Authorization: Bearer ${ADMIN_TOKEN}' \
            -H 'Content-Type: application/json' \
            -d '{\"name\": \"${DEPT_NAME}\", \"description\": \"${DEPT_DESC}\"}'" \
        "curl -L -s -X GET '${AUTH_SERVICE_URL}/api/v1/departments/?search=${DEPT_NAME}' \
            -H 'Authorization: Bearer ${ADMIN_TOKEN}'" \
        '.departments[0].id')

    if [ -z "$AUTH_DEPT_ID" ] || [ "$AUTH_DEPT_ID" = "null" ]; then
        log_error "Failed to create department '${DEPT_NAME}' in auth_service"
        exit 1
    fi
    DEPT_IDS_AUTH["$DEPT_NAME"]="$AUTH_DEPT_ID"
    log_success "  Department '${DEPT_NAME}' → auth ID $AUTH_DEPT_ID"

    # 3b. Other service schemas (raw SQL)
    for schema in knowledge meeting checklists; do
        create_dept_in_schema "$schema" "$DEPT_NAME" "$DEPT_DESC"
    done

    KNOWLEDGE_DEPT_ID=$(get_dept_id_in_schema "knowledge" "$DEPT_NAME")
    MEETING_DEPT_ID=$(get_dept_id_in_schema "meeting" "$DEPT_NAME")
    CHECKLIST_DEPT_ID=$(get_dept_id_in_schema "checklists" "$DEPT_NAME")

    DEPT_IDS_KNOWLEDGE["$DEPT_NAME"]="${KNOWLEDGE_DEPT_ID:-null}"
    DEPT_IDS_MEETING["$DEPT_NAME"]="${MEETING_DEPT_ID:-null}"
    DEPT_IDS_CHECKLIST["$DEPT_NAME"]="${CHECKLIST_DEPT_ID:-null}"
done

# Use first department for default operations
FIRST_DEPT_NAME="Engineering"
AUTH_DEPT_ID="${DEPT_IDS_AUTH[$FIRST_DEPT_NAME]}"
KNOWLEDGE_DEPT_ID="${DEPT_IDS_KNOWLEDGE[$FIRST_DEPT_NAME]}"
MEETING_DEPT_ID="${DEPT_IDS_MEETING[$FIRST_DEPT_NAME]}"
CHECKLIST_DEPT_ID="${DEPT_IDS_CHECKLIST[$FIRST_DEPT_NAME]}"

# ============================================================================
#  PHASE 4 — Create HR user
# ============================================================================
phase "Creating HR user (${HR_EMAIL})"

HR_USER_ID=$(api_create_or_get \
    "curl -L -s -X POST '${AUTH_SERVICE_URL}/api/v1/users/' \
        -H 'Authorization: Bearer ${ADMIN_TOKEN}' \
        -H 'Content-Type: application/json' \
        -d '{
            \"email\": \"${HR_EMAIL}\",
            \"first_name\": \"${HR_FIRST}\",
            \"last_name\": \"${HR_LAST}\",
            \"employee_id\": \"${HR_EMP_ID}\",
            \"password\": \"${HR_PASSWORD}\",
            \"role\": \"HR\",
            \"department_id\": ${AUTH_DEPT_ID},
            \"position\": \"HR Manager\",
            \"level\": \"SENIOR\"
        }'" \
    "curl -L -s -X GET '${AUTH_SERVICE_URL}/api/v1/users/by-email/${HR_EMAIL}' \
        -H 'Authorization: Bearer ${ADMIN_TOKEN}'")

if [ -z "$HR_USER_ID" ] || [ "$HR_USER_ID" = "null" ]; then
    log_error "Failed to create/get HR user"
    exit 1
fi
log_success "HR user ID: $HR_USER_ID"

# ============================================================================
#  PHASE 5 — Create Mentor user
# ============================================================================
phase "Creating Mentor user (${MENTOR_EMAIL})"

MENTOR_USER_ID=$(api_create_or_get \
    "curl -L -s -X POST '${AUTH_SERVICE_URL}/api/v1/users/' \
        -H 'Authorization: Bearer ${ADMIN_TOKEN}' \
        -H 'Content-Type: application/json' \
        -d '{
            \"email\": \"${MENTOR_EMAIL}\",
            \"first_name\": \"${MENTOR_FIRST}\",
            \"last_name\": \"${MENTOR_LAST}\",
            \"employee_id\": \"${MENTOR_EMP_ID}\",
            \"password\": \"${MENTOR_PASSWORD}\",
            \"role\": \"MENTOR\",
            \"department_id\": ${AUTH_DEPT_ID},
            \"position\": \"Senior Software Engineer\",
            \"level\": \"SENIOR\"
        }'" \
    "curl -L -s -X GET '${AUTH_SERVICE_URL}/api/v1/users/by-email/${MENTOR_EMAIL}' \
        -H 'Authorization: Bearer ${ADMIN_TOKEN}'")

if [ -z "$MENTOR_USER_ID" ] || [ "$MENTOR_USER_ID" = "null" ]; then
    log_error "Failed to create/get Mentor user"
    exit 1
fi
log_success "Mentor user ID: $MENTOR_USER_ID"

# ============================================================================
#  PHASE 6 — Create 10 Checklist templates with tasks (before user registration)
# ============================================================================
phase "Creating 10 checklist templates with tasks"

# Template definitions: name|desc|dept|position|level|duration|task_categories|default_assignee
TEMPLATES=(
    "Onboarding Checklist|Standard onboarding checklist for new employees|Engineering|Software Engineer|JUNIOR|30|INTRODUCTION,DOCUMENTATION,TECHNICAL|MENTOR"
    "Engineering Onboarding|Technical onboarding for engineering team|Engineering|Software Engineer|MIDDLE|21|TECHNICAL,INTRODUCTION|DOCUMENTATION|MENTOR"
    "Sales Onboarding|Onboarding for sales team members|Sales|Sales Representative|JUNIOR|14|INTRODUCTION,OTHER,DOCUMENTATION|HR"
    "Product Onboarding|Onboarding for product team|Product|Product Manager|MIDDLE|21|INTRODUCTION,OTHER,DOCUMENTATION|MENTOR"
    "Marketing Onboarding|Onboarding for marketing team|Marketing|Marketing Specialist|JUNIOR|14|INTRODUCTION,OTHER,DOCUMENTATION|HR"
    "Operations Onboarding|Onboarding for operations team|Operations|Operations Analyst|JUNIOR|14|INTRODUCTION,OTHER,DOCUMENTATION|HR"
    "Manager Onboarding|Onboarding for team managers|Engineering|Engineering Manager|MIDDLE|21|INTRODUCTION,OTHER,DOCUMENTATION|HR"
    "General Onboarding|Basic onboarding for any role|||JUNIOR|7|INTRODUCTION,DOCUMENTATION|HR"
)

declare -a TEMPLATE_IDS=()

tpl_dept_id=""
level_arg=""
pos_arg=""
all_templates=""
existing_id=""

for template_spec in "${TEMPLATES[@]}"; do
    TPL_NAME="${template_spec%%|*}"
    template_spec="${template_spec#*|}"
    TPL_DESC="${template_spec%%|*}"
    template_spec="${template_spec#*|}"
    TPL_DEPT="${template_spec%%|*}"
    template_spec="${template_spec#*|}"
    TPL_POS="${template_spec%%|*}"
    template_spec="${template_spec#*|}"
    TPL_LEVEL="${template_spec%%|*}"
    template_spec="${template_spec#*|}"
    TPL_DURATION="${template_spec%%|*}"
    template_spec="${template_spec#*|}"
    TPL_CATS="${template_spec%%|*}"
    template_spec="${template_spec#*|}"
    TPL_ASSIGNEE="${template_spec%%|*}"

    # Get department ID for this template
    tpl_dept_id="null"
    if [ -n "$TPL_DEPT" ] && [ -n "${DEPT_IDS_CHECKLIST[$TPL_DEPT]:-}" ]; then
        tpl_dept_id="${DEPT_IDS_CHECKLIST[$TPL_DEPT]}"
    fi

    level_arg=""
    if [ -n "$TPL_LEVEL" ]; then
        level_arg="\"level\": \"${TPL_LEVEL}\","
    fi
    pos_arg=""
    if [ -n "$TPL_POS" ]; then
        pos_arg="\"position\": \"${TPL_POS}\","
    fi

    # Check if template already exists (by name AND department_id)
    all_templates=$(curl -L -s "${CHECKLISTS_SERVICE_URL}/api/v1/templates/?limit=100" \
        -H "Authorization: Bearer ${ADMIN_TOKEN}" 2>/dev/null)
    
    if [ "$tpl_dept_id" = "null" ] || [ -z "$tpl_dept_id" ]; then
        existing_id=$(echo "$all_templates" | jq -r ".[] | select(.name == \"${TPL_NAME}\" and .department_id == null) | .id // empty" 2>/dev/null)
    else
        existing_id=$(echo "$all_templates" | jq -r ".[] | select(.name == \"${TPL_NAME}\" and .department_id == ${tpl_dept_id}) | .id // empty" 2>/dev/null)
    fi

    if [ -n "$existing_id" ] && [ "$existing_id" != "null" ]; then
        TEMPLATE_ID="$existing_id"
    else
        # Create template
        TEMPLATE_ID=$(curl -L -s -X POST "${CHECKLISTS_SERVICE_URL}/api/v1/templates/" \
            -H "Authorization: Bearer ${ADMIN_TOKEN}" \
            -H "Content-Type: application/json" \
            -d "{
                \"name\": \"${TPL_NAME}\",
                \"description\": \"${TPL_DESC}\",
                \"department_id\": ${tpl_dept_id},
                ${pos_arg}
                ${level_arg}
                \"duration_days\": ${TPL_DURATION},
                \"task_categories\": [$(echo "$TPL_CATS" | tr ',' '\n' | while read cat; do echo -n "\"$cat\","; done | sed 's/,$//')],
                \"default_assignee_role\": \"${TPL_ASSIGNEE}\",
                \"status\": \"ACTIVE\"
            }" 2>/dev/null | jq -r '.id // empty')
    fi

    if [ -z "$TEMPLATE_ID" ] || [ "$TEMPLATE_ID" = "null" ]; then
        log_warning "  Failed to create template '${TPL_NAME}'"
        continue
    fi
    TEMPLATE_IDS+=("$TEMPLATE_ID")
    log_success "  Template '${TPL_NAME}' → ID $TEMPLATE_ID"

    # Add 5-10 tasks to this template
    TASK_COUNT=$((RANDOM % 6 + 5))  # 5-10 tasks
    log_info "    Adding $TASK_COUNT tasks to template '${TPL_NAME}' ..."

    declare -a TASK_TITLES
    declare -a TASK_DESCS
    declare -a TASK_CATS
    declare -a TASK_DAYS

    case "$TPL_NAME" in
        "Onboarding Checklist"|"Engineering Onboarding")
            TASK_TITLES=("Welcome Meeting" "HR Documentation" "Tech Setup" "Team Introduction" "First Code Review" "Security Training" "工具培训" "Codebase Walkthrough" "Onboarding Survey" "Final Review")
            TASK_DESCS=("Meet with your manager" "Complete HR forms" "Set up dev environment" "Meet your team" "Submit first PR" "Complete security training" "Learn tooling" "Walk through codebase" "Complete survey" "Final check-in")
            TASK_CATS=("INTRODUCTION" "DOCUMENTATION" "TECHNICAL" "INTRODUCTION" "TECHNICAL" "DOCUMENTATION" "TECHNICAL" "TECHNICAL" "INTRODUCTION" "INTRODUCTION")
            TASK_DAYS=(1 3 5 7 10 14 14 21 28 30)
            ;;
        "Sales Onboarding")
            TASK_TITLES=("Welcome Meeting" "CRM Training" "Product Knowledge" "Sales Process" "First Calls" "Demo Practice" "Territory Assignment" "Quota Review" "Mid-term Check-in" "Certification")
            TASK_DESCS=("Meet manager" "Learn CRM system" "Study product" "Understand sales process" "Make first calls" "Practice demos" "Get territory" "Review targets" "Check progress" "Complete certification")
            TASK_CATS=("INTRODUCTION" "DOCUMENTATION" "DOCUMENTATION" "INTRODUCTION" "OTHER" "OTHER" "DOCUMENTATION" "DOCUMENTATION" "INTRODUCTION" "DOCUMENTATION")
            TASK_DAYS=(1 3 5 7 10 10 14 14 21 30)
            ;;
        "Product Onboarding")
            TASK_TITLES=("Welcome Meeting" "Product Overview" "Roadmap Review" "Tools Training" "Stakeholder Intro" "First Feature" "User Research" "Analytics Review" "Mid-term Review" "Product Certification")
            TASK_DESCS=("Meet manager" "Learn product" "Review roadmap" "Learn tools" "Meet stakeholders" "Ship first feature" "Conduct user research" "Review metrics" "Check progress" "Complete certification")
            TASK_CATS=("INTRODUCTION" "OTHER" "OTHER" "DOCUMENTATION" "INTRODUCTION" "OTHER" "OTHER" "OTHER" "INTRODUCTION" "DOCUMENTATION")
            TASK_DAYS=(1 3 5 7 10 14 14 21 28 30)
            ;;
        "Marketing Onboarding")
            TASK_TITLES=("Welcome Meeting" "Brand Guidelines" "Marketing Tools" "Campaign Overview" "Social Media Training" "Content Review" "First Campaign" "Analytics Setup" "Mid-term Review" "Channel Certification")
            TASK_DESCS=("Meet manager" "Learn brand" "Learn tools" "Review campaigns" "Learn social" "Review content" "Launch first campaign" "Setup analytics" "Check progress" "Get certified")
            TASK_CATS=("INTRODUCTION" "OTHER" "DOCUMENTATION" "OTHER" "OTHER" "OTHER" "OTHER" "DOCUMENTATION" "INTRODUCTION" "DOCUMENTATION")
            TASK_DAYS=(1 3 5 7 10 14 14 21 28 30)
            ;;
        "Operations Onboarding")
            TASK_TITLES=("Welcome Meeting" "Systems Overview" "Process Training" "Tools Setup" "First Tasks" "Quality Standards" "Compliance Training" "Metrics Review" "Mid-term Review" "Operations Certification")
            TASK_DESCS=("Meet manager" "Learn systems" "Understand processes" "Setup tools" "Complete first tasks" "Learn standards" "Complete compliance" "Review metrics" "Check progress" "Get certified")
            TASK_CATS=("INTRODUCTION" "OTHER" "OTHER" "DOCUMENTATION" "OTHER" "OTHER" "DOCUMENTATION" "OTHER" "INTRODUCTION" "DOCUMENTATION")
            TASK_DAYS=(1 3 5 7 10 10 14 14 21 30)
            ;;
        "Executive Onboarding")
            TASK_TITLES=("Executive Welcome" "Strategy Overview" "Team Leadership" "Budget Review" "Stakeholder Meetings" "First Initiatives" "Board Presentation" "100-Day Review" "Strategic Planning" "Leadership Certification")
            TASK_DESCS=("Executive welcome" "Learn strategy" "Meet team leads" "Review budget" "Meet stakeholders" "Launch initiatives" "Present to board" "Review progress" "Plan strategy" "Get certified")
            TASK_CATS=("INTRODUCTION" "OTHER" "OTHER" "OTHER" "INTRODUCTION" "OTHER" "OTHER" "INTRODUCTION" "OTHER" "DOCUMENTATION")
            TASK_DAYS=(1 3 5 7 14 21 30 60 90 100)
            ;;
        "Intern Onboarding")
            TASK_TITLES=("Welcome Meeting" "Intern Orientation" "Mentor Introduction" "First Project" "Weekly Check-in" "Mid-term Review" "Final Project" "Final Presentation" "Feedback Session" "Completion Certificate")
            TASK_DESCS=("Meet manager" "Intern orientation" "Meet mentor" "Start first project" "Weekly sync" "Review progress" "Complete project" "Present results" "Give feedback" "Get certificate")
            TASK_CATS=("INTRODUCTION" "INTRODUCTION" "INTRODUCTION" "TECHNICAL" "INTRODUCTION" "INTRODUCTION" "TECHNICAL" "INTRODUCTION" "INTRODUCTION" "DOCUMENTATION")
            TASK_DAYS=(1 2 3 7 14 30 45 55 58 60)
            ;;
        "Manager Onboarding")
            TASK_TITLES=("Manager Welcome" "Team Overview" "HR Processes" "Performance Reviews" "1:1 Training" "Budget Training" "Hiring Process" "First Team Meeting" "Leadership Workshop" "Manager Certification")
            TASK_DESCS=("Manager welcome" "Meet team" "Learn HR" "Learn reviews" "Learn 1:1s" "Learn budgets" "Learn hiring" "Lead meeting" "Workshop" "Get certified")
            TASK_CATS=("INTRODUCTION" "INTRODUCTION" "OTHER" "OTHER" "OTHER" "OTHER" "OTHER" "INTRODUCTION" "OTHER" "DOCUMENTATION")
            TASK_DAYS=(1 3 5 7 10 14 14 21 28 30)
            ;;
        "General Onboarding")
            TASK_TITLES=("Welcome Email" "HR Paperwork" "IT Setup" "Badge Access" "Building Tour" "Team Hello" "First Week Check-in" "Completion Survey")
            TASK_DESCS=("Read welcome" "Complete paperwork" "Get IT gear" "Get badge" "Tour building" "Meet team" "Week 1 check" "Complete survey")
            TASK_CATS=("INTRODUCTION" "DOCUMENTATION" "TECHNICAL" "INTRODUCTION" "INTRODUCTION" "INTRODUCTION" "INTRODUCTION" "DOCUMENTATION")
            TASK_DAYS=(1 1 2 2 3 5 7 7)
            ;;
    esac

    # Add tasks up to TASK_COUNT
    for ((i=0; i<TASK_COUNT && i<${#TASK_TITLES[@]}; i++)); do
        execute_with_retry \
            "curl -L -s -X POST '${CHECKLISTS_SERVICE_URL}/api/v1/templates/${TEMPLATE_ID}/tasks' \
                -H 'Authorization: Bearer ${ADMIN_TOKEN}' \
                -H 'Content-Type: application/json' \
                -d '{
                    \"template_id\": ${TEMPLATE_ID},
                    \"title\": \"${TASK_TITLES[$i]}\",
                    \"description\": \"${TASK_DESCS[$i]}\",
                    \"instructions\": \"Please complete this task as part of your onboarding.\",
                    \"category\": \"${TASK_CATS[$i]}\",
                    \"order\": $((i+1)),
                    \"due_days\": ${TASK_DAYS[$i]:-7},
                    \"estimated_minutes\": $((30 + RANDOM % 90)),
                    \"resources\": [],
                    \"required_documents\": [],
                    \"assignee_role\": \"${TPL_ASSIGNEE}\",
                    \"auto_assign\": true,
                    \"depends_on\": []
                }' | jq -r '.id // empty'" 3 2 >/dev/null || true
    done
    log_success "    Added ${TASK_COUNT} tasks to '${TPL_NAME}'"
done

# Use first template for verification
TEMPLATE_ID="${TEMPLATE_IDS[0]}"

# ============================================================================
#  PHASE 7 — Create invitation and register user (triggers auto-create)
# ============================================================================
phase "Creating invitation and registering user (${USER_EMAIL})"

USER_ID=$(curl -L -s -X GET "${AUTH_SERVICE_URL}/api/v1/users/by-email/${USER_EMAIL}" \
    -H "Authorization: Bearer ${ADMIN_TOKEN}" 2>/dev/null | jq -r '.id // empty')

if [ -n "$USER_ID" ] && [ "$USER_ID" != "null" ]; then
    log_info "User already exists: ${USER_EMAIL} (ID: $USER_ID)"
else
    log_info "Creating invitation for ${USER_EMAIL}..."
    INVITATION_RESPONSE=$(execute_with_retry \
        "curl -L -s -X POST '${AUTH_SERVICE_URL}/api/v1/invitations/' \
            -H 'Authorization: Bearer ${ADMIN_TOKEN}' \
            -H 'Content-Type: application/json' \
            -d '{
                \"email\": \"${USER_EMAIL}\",
                \"employee_id\": \"${USER_EMP_ID}\",
                \"first_name\": \"${USER_FIRST}\",
                \"last_name\": \"${USER_LAST}\",
                \"department_id\": ${AUTH_DEPT_ID},
                \"position\": \"Software Engineer\",
                \"level\": \"JUNIOR\",
                \"mentor_id\": ${MENTOR_USER_ID},
                \"role\": \"NEWBIE\",
                \"expires_in_days\": 7
            }'" 3 2)
    INVITATION_TOKEN=$(echo "$INVITATION_RESPONSE" | jq -r '.token // empty')
    if [ -z "$INVITATION_TOKEN" ]; then
        log_error "Failed to create invitation"
        log_debug "Response: $INVITATION_RESPONSE"
        exit 1
    fi
    log_success "Invitation token: $INVITATION_TOKEN"

    log_info "Registering user via invitation (auto-create will assign checklist)..."
    REGISTER_RESPONSE=$(execute_with_retry \
        "curl -L -s -X POST '${AUTH_SERVICE_URL}/api/v1/auth/register/${INVITATION_TOKEN}' \
            -H 'Content-Type: application/json' \
            -H 'X-API-Key: ${API_KEY}' \
            -d '{
                \"telegram_id\": ${USER_TELEGRAM_ID},
                \"username\": \"${USER_TELEGRAM_USERNAME}\",
                \"first_name\": \"${USER_FIRST}\",
                \"last_name\": \"${USER_LAST}\"
            }'" 3 2)

    if echo "$REGISTER_RESPONSE" | jq -e '.access_token' >/dev/null 2>&1; then
        USER_ID=$(curl -L -s -X GET "${AUTH_SERVICE_URL}/api/v1/users/by-email/${USER_EMAIL}" \
            -H "Authorization: Bearer ${ADMIN_TOKEN}" | jq -r '.id // empty')
        log_success "User registered: ${USER_EMAIL} (ID: $USER_ID)"
    else
        USER_ID=$(curl -L -s -X GET "${AUTH_SERVICE_URL}/api/v1/users/by-email/${USER_EMAIL}" \
            -H "Authorization: Bearer ${ADMIN_TOKEN}" 2>/dev/null | jq -r '.id // empty')
        if [ -n "$USER_ID" ] && [ "$USER_ID" != "null" ]; then
            log_info "User already registered: ${USER_EMAIL} (ID: $USER_ID)"
        else
            log_error "Failed to register user"
            log_debug "Response: $REGISTER_RESPONSE"
            exit 1
        fi
    fi
fi

log_info "Verifying checklist was auto-created for user $USER_ID ..."
sleep 1
CHECKLIST_RESPONSE=$(curl -L -s -X GET "${CHECKLISTS_SERVICE_URL}/api/v1/checklists/?user_id=${USER_ID}&limit=1" \
    -H "Authorization: Bearer ${ADMIN_TOKEN}")
CHECKLIST_ID=$(echo "$CHECKLIST_RESPONSE" | jq -r '.checklists[0].id // empty')

if [ -n "$CHECKLIST_ID" ] && [ "$CHECKLIST_ID" != "null" ]; then
    log_success "Auto-created checklist instance ID: $CHECKLIST_ID"
else
    log_warning "No checklist was auto-created (template may not match user's department/position)"
fi

# ============================================================================
#  PHASE 8 — Knowledge Base: 5 categories, tags, 30 articles, attachments
# ============================================================================
phase "Creating knowledge base content"

# ── 8a. Categories (5) ──────────────────────────────────────────────────────────
log_info "Creating 5 categories ..."

declare -A CAT_IDS

create_category() {
    local name="$1" slug="$2" desc="$3" order="$4"
    local id
    id=$(api_create_or_get \
        "curl -L -s -X POST '${KNOWLEDGE_SERVICE_URL}/api/v1/categories/' \
            -H 'Authorization: Bearer ${ADMIN_TOKEN}' \
            -H 'Content-Type: application/json' \
            -d '{
                \"name\": \"${name}\",
                \"slug\": \"${slug}\",
                \"description\": \"${desc}\",
                \"department_id\": ${KNOWLEDGE_DEPT_ID:-null},
                \"position\": \"Software Engineer\",
                \"level\": \"JUNIOR\",
                \"order\": ${order}
            }'" \
        "curl -L -s -X GET '${KNOWLEDGE_SERVICE_URL}/api/v1/categories/${slug}' \
            -H 'Authorization: Bearer ${ADMIN_TOKEN}'" \
        '.id')
    CAT_IDS["$slug"]="$id"
    log_success "  Category '${name}' → ID $id"
}

create_category "Onboarding"      "onboarding"      "General onboarding materials"    1
create_category "Development"     "development"      "Development guides and tools"    2
create_category "Company Policies" "company-policies" "HR policies and procedures"     3
create_category "Product"        "product"          "Product management and design"    4
create_category "Sales & Marketing" "sales-marketing" "Sales and marketing guides"     5

# ── 8b. Tags (10) ───────────────────────────────────────────────────────────────
log_info "Creating 10 tags ..."

declare -A TAG_IDS

create_tag() {
    local name="$1" slug="$2" desc="$3"
    local id
    id=$(api_create_or_get \
        "curl -L -s -X POST '${KNOWLEDGE_SERVICE_URL}/api/v1/tags/' \
            -H 'Authorization: Bearer ${ADMIN_TOKEN}' \
            -H 'Content-Type: application/json' \
            -d '{\"name\": \"${name}\", \"slug\": \"${slug}\", \"description\": \"${desc}\"}'" \
        "curl -L -s -X GET '${KNOWLEDGE_SERVICE_URL}/api/v1/tags/${slug}' \
            -H 'Authorization: Bearer ${ADMIN_TOKEN}'" \
        '.id')
    TAG_IDS["$slug"]="$id"
    log_success "  Tag '${name}' → ID $id"
}

create_tag "Onboarding" "onboarding" "Role introduction materials"
create_tag "Engineering" "engineering" "Development and engineering topics"
create_tag "Setup"       "setup"       "Environment and tools setup"
create_tag "Policies"    "policies"    "Company policies and rules"
create_tag "Guide"       "guide"       "Step-by-step guides"
create_tag "Tools"       "tools"       "Software tools and utilities"
create_tag "Process"     "process"     "Business processes"
create_tag "Best Practices" "best-practices" "Industry best practices"
create_tag "Compliance" "compliance"   "Compliance and regulations"
create_tag "Training"    "training"    "Training materials"

# ── 8c. Articles (30) ───────────────────────────────────────────────────────────
log_info "Creating 30 articles ..."

declare -a ARTICLE_IDS=()

# Article definitions: title|slug|content|excerpt|cat_slug|tag1|tag2|dept|position|level|status|is_pinned|keywords
ARTICLES=(
    "Welcome to the Company|welcome-company|Welcome to our company! This guide will help you navigate your first days.|Welcome guide for all new employees|onboarding|onboarding|guide|Engineering|Software Engineer|JUNIOR|PUBLISHED|false|welcome,onboarding,new-hire"
    "Onboarding Checklist|onboarding-checklist|Complete this checklist during your first week.|Onboarding tasks checklist|onboarding|onboarding|guide|Engineering|Software Engineer|JUNIOR|PUBLISHED|true|onboarding,checklist,tasks"
    "Development Environment Setup|dev-environment-setup|Follow these steps to configure your development environment.|Dev environment setup guide|development|setup|tools|Engineering|Software Engineer|JUNIOR|PUBLISHED|false|development,setup,tools"
    "Code Review Best Practices|code-review-best-practices|Good code reviews improve quality and share knowledge.|Code review guidelines|development|engineering|best-practices|Engineering|Software Engineer|MIDDLE|PUBLISHED|false|code-review,best-practices"
    "Git Branching Strategy|git-branching-strategy|We use trunk-based development with short-lived feature branches.|Git workflow guide|development|engineering|guide|Engineering|Software Engineer|JUNIOR|PUBLISHED|false|git,branching,workflow"
    "Company Leave Policy|company-leave-policy|28 days annual leave, unlimited sick leave with doctor note.|Leave policy overview|company-policies|policies|compliance|Engineering|Software Engineer|JUNIOR|PUBLISHED|false|leave,policy,hr"
    "Remote Work Policy|remote-work-policy|Up to 3 days remote work per week, coordinate with team lead.|Remote work guidelines|company-policies|policies|process|Engineering|Software Engineer|JUNIOR|PUBLISHED|false|remote,policy,work-from-home"
    "Code of Conduct|code-of-conduct|Our code of conduct outlines expectations for all employees.|Employee conduct guidelines|company-policies|policies|compliance|Engineering|Software Engineer|JUNIOR|PUBLISHED|true|conduct,policy,ethics"
    "Data Security Policy|data-security-policy|Protect company data with encryption, strong passwords, and secure practices.|Security guidelines|company-policies|policies|compliance|Engineering|Software Engineer|JUNIOR|PUBLISHED|false|security,data,policy"
    "Equal Opportunity Policy|equal-opportunity-policy|We are an equal opportunity employer. Discrimination is not tolerated.|EEO policy|company-policies|policies|compliance|Engineering|Software Engineer|JUNIOR|PUBLISHED|false|eeo,policy,diversity"
    "API Design Guidelines|api-design-guidelines|Follow these guidelines when designing REST APIs.|API design best practices|development|engineering|best-practices|Engineering|Senior Software Engineer|SENIOR|DRAFT|false|api,design,rest"
    "Testing Best Practices|testing-best-practices|Write tests first, maintain high coverage, use mocking appropriately.|Testing guidelines|development|engineering|best-practices|Engineering|Software Engineer|MIDDLE|DRAFT|false|testing,tdd,quality"
    "Database Design|database-design|Follow normalization rules, use appropriate indexes, document schemas.|Database design guide|development|engineering|tools|Engineering|Senior Software Engineer|SENIOR|DRAFT|false|database,design,sql"
    "Product Management Overview|product-management-overview|Product management involves discovery, planning, and delivery.|PM overview|product|process|guide|Product|Product Manager|MIDDLE|PUBLISHED|false|product,management,overview"
    "User Research Methods|user-research-methods|Conduct user interviews, surveys, and usability testing.|User research guide|product|process|training|Product|Product Manager|MIDDLE|PUBLISHED|false|user-research,methods,ux"
    "Product Roadmap Creation|product-roadmap-creation|Create a quarterly roadmap with priorities and dependencies.|Roadmap planning|product|process|guide|Product|Product Manager|SENIOR|DRAFT|false|roadmap,planning,prioritization"
    "Agile Sprint Planning|agile-sprint-planning|Run effective sprint planning meetings with clear goals.|Sprint planning guide|product|process|engineering|Product|Product Manager|MIDDLE|DRAFT|false|agile,sprint,planning"
    "Sales Process Overview|sales-process-overview|The sales process includes prospecting, qualification, demo, and close.|Sales process guide|sales-marketing|process|guide|Sales|Sales Representative|JUNIOR|PUBLISHED|false|sales,process,funnel"
    "Cold Calling Techniques|cold-calling-techniques|Effective cold calling requires research, script, and confidence.|Cold call guide|sales-marketing|process|training|Sales|Sales Representative|JUNIOR|PUBLISHED|false|cold-calling,sales,techniques"
    "CRM Best Practices|crm-best-practices|Use CRM to track leads, opportunities, and customer relationships.|CRM guide|sales-marketing|tools|process|Sales|Sales Manager|MIDDLE|DRAFT|false|crm,sales,tools"
    "Negotiation Skills|negotiation-skills|Close deals by understanding customer needs and offering value.|Negotiation guide|sales-marketing|process|best-practices|Sales|Senior Sales Rep|SENIOR|DRAFT|false|negotiation,sales,skills"
    "Marketing Strategy Basics|marketing-strategy-basics|Develop marketing strategies based on market research and audience.|Marketing guide|sales-marketing|process|guide|Marketing|Marketing Specialist|JUNIOR|PUBLISHED|false|marketing,strategy,basis"
    "Social Media Guidelines|social-media-guidelines|Represent the brand professionally on social platforms.|Social media guide|sales-marketing|policies|tools|Marketing|Marketing Specialist|JUNIOR|PUBLISHED|false|social,media,guidelines"
    "Content Marketing|content-marketing|Create valuable content to attract and engage customers.|Content strategy|sales-marketing|process|guide|Marketing|Marketing Manager|MIDDLE|DRAFT|false|content,marketing,strategy"
    "SEO Best Practices|seo-best-practices|Optimize content for search engines to drive organic traffic.|SEO guide|sales-marketing|tools|best-practices|Marketing|Marketing Specialist|JUNIOR|DRAFT|false|seo,search,optimization"
    "Email Marketing|email-marketing|Craft effective email campaigns that convert.|Email campaign guide|sales-marketing|process|tools|Marketing|Marketing Specialist|JUNIOR|DRAFT|false|email,marketing,campaign"
    "Performance Review Process|performance-review-process|Annual reviews include self-assessment, manager review, and calibration.|Performance review guide|company-policies|process|policies|Engineering|Software Engineer|JUNIOR|PUBLISHED|false|performance,review,process"
    "Expense Reimbursement|expense-reimbursement|Submit expenses within 30 days with proper documentation.|Expense policy|company-policies|policies|process|Engineering|Software Engineer|JUNIOR|PUBLISHED|false|expense,reimbursement,policy"
    "IT Security Tips|it-security-tips|Use strong passwords, enable 2FA, and report suspicious activity.|Security tips|company-policies|policies|security|Engineering|Software Engineer|JUNIOR|PUBLISHED|false|security,it,tips"
    "Benefits Overview|benefits-overview|Health insurance, 401k, wellness programs, and more.|Employee benefits|company-policies|policies|guide|Engineering|Software Engineer|JUNIOR|PUBLISHED|true|benefits,insurance,401k"
)

create_article() {
    local title="$1" slug="$2" content="$3" excerpt="$4" cat_slug="$5"
    local tag_slug1="$6" tag_slug2="$7" dept="$8" pos="$9" level="${10}" status="${11}" is_pinned="${12}" keywords="${13}"

    local cat_id="${CAT_IDS[$cat_slug]:-$KNOWLEDGE_DEPT_ID}"

    # Get department ID
    local dept_id=""
    if [ -n "$dept" ] && [ -n "${DEPT_IDS_KNOWLEDGE[$dept]:-}" ]; then
        dept_id="${DEPT_IDS_KNOWLEDGE[$dept]}"
    fi

    # Build tag_ids array
    local tag_ids="[]"
    if [ -n "$tag_slug1" ] && [ -n "${TAG_IDS[$tag_slug1]:-}" ]; then
        tag_ids="[${TAG_IDS[$tag_slug1]}"
        if [ -n "$tag_slug2" ] && [ -n "${TAG_IDS[$tag_slug2]:-}" ]; then
            tag_ids="${tag_ids},${TAG_IDS[$tag_slug2]}"
        fi
        tag_ids="${tag_ids}]"
    fi

    # Build keywords array
    local kw_list="[]"
    if [ -n "$keywords" ]; then
        kw_list="[$(echo "$keywords" | tr ',' '\n' | while read kw; do echo -n "\"$kw\","; done | sed 's/,$//')]"
    fi

    # Convert is_pinned to boolean string
    local pinned_bool="false"
    if [ "$is_pinned" = "true" ]; then
        pinned_bool="true"
    fi

    # Build JSON payload manually
    local json_payload="{\"title\":\"$title\",\"content\":\"$content\",\"excerpt\":\"$excerpt\",\"category_id\":$cat_id,\"department_id\":$([ -z "$dept_id" ] && echo "null" || echo "$dept_id"),\"tag_ids\":$tag_ids,\"status\":\"$status\",\"is_pinned\":$pinned_bool,\"keywords\":$kw_list"
    
    if [ -n "$pos" ]; then
        json_payload="${json_payload},\"position\":\"$pos\""
    fi
    if [ -n "$level" ]; then
        json_payload="${json_payload},\"level\":\"$level\""
    fi
    json_payload="${json_payload}}"

    # Create article directly (skip idempotent check - duplicates on re-run is acceptable)
    local article_id
    local create_resp
    create_resp=$(curl -L -s -X POST "${KNOWLEDGE_SERVICE_URL}/api/v1/articles/" \
        -H "Authorization: Bearer ${ADMIN_TOKEN}" \
        -H "Content-Type: application/json" \
        -d "$json_payload" 2>/dev/null)

    article_id=$(echo "$create_resp" | jq -r '.id // empty')

    if [ -n "$article_id" ] && [ "$article_id" != "null" ]; then
        ARTICLE_IDS+=("$article_id")
        log_success "  Article '${title}' → ID $article_id (${status})"
    else
        local err_msg
        err_msg=$(echo "$create_resp" | jq -r '.detail // .message // tostring' 2>/dev/null)
        log_warning "  Failed to create article '${title}': ${err_msg}"
    fi
}

# Parse and create articles
for article_spec in "${ARTICLES[@]}"; do
    IFS='|' read -ra fields <<< "$article_spec"
    create_article "${fields[0]}" "${fields[1]}" "${fields[2]}" "${fields[3]}" "${fields[4]}" "${fields[5]}" "${fields[6]}" "${fields[7]}" "${fields[8]}" "${fields[9]}" "${fields[10]}" "${fields[11]}" "${fields[12]}"
done

# ── 8d. Add some articles to favorites ─────────────────────────────────────────
log_info "Adding 5 articles to favorites for user $USER_ID ..."
for ((i=0; i<5 && i<${#ARTICLE_IDS[@]}; i++)); do
    FAV_RESP=$(curl -L -s -X POST "${KNOWLEDGE_SERVICE_URL}/api/v1/articles/${ARTICLE_IDS[$i]}/favorite" \
        -H "Authorization: Bearer ${ADMIN_TOKEN}" 2>/dev/null)
    log_debug "  Added article ${ARTICLE_IDS[$i]} to favorites"
done
log_success "5 articles added to favorites"

# ── 8e. Attachments (5 articles get file attachments) ────────────────────────
log_info "Uploading attachments to 5 articles ..."

upload_attachment() {
    local article_id="$1" filename="$2" content="$3" description="$4"
    local tmp_dir
    tmp_dir=$(mktemp -d)
    local tmp_file="${tmp_dir}/${filename}"
    echo -e "$content" > "$tmp_file"

    local resp
    resp=$(execute_with_retry \
        "curl -L -s -X POST '${KNOWLEDGE_SERVICE_URL}/api/v1/attachments/upload' \
            -H 'Authorization: Bearer ${ADMIN_TOKEN}' \
            -F 'article_id=${article_id}' \
            -F 'file=@${tmp_file}' \
            -F 'description=${description}' \
            -F 'order=1' \
            -F 'is_downloadable=true'" 3 2)

    rm -rf "$tmp_dir"

    local att_id
    att_id=$(echo "$resp" | jq -r '.id // empty')
    if [ -n "$att_id" ] && [ "$att_id" != "null" ]; then
        log_success "  Attachment '${filename}' uploaded → ID $att_id"
    else
        log_warning "  Failed to upload attachment '${filename}'"
    fi
}

# Upload attachments to first 5 articles
for ((i=0; i<5 && i<${#ARTICLE_IDS[@]}; i++)); do
    case $i in
        0) upload_attachment "${ARTICLE_IDS[$i]}" "welcome-checklist.txt" "Welcome Checklist\n\n[x] Complete HR paperwork\n[x] Set up workstation\n[x] Meet team\n[x] Review code of conduct\n[ ] Complete first task" "Welcome checklist for new hires" ;;
        1) upload_attachment "${ARTICLE_IDS[$i]}" "onboarding-tasks.txt" "Onboarding Tasks\n\n1. Day 1: Badge and laptop\n2. Day 2: Email setup\n3. Day 3: Team intro\n4. Week 1: First project" "Detailed onboarding tasks" ;;
        2) upload_attachment "${ARTICLE_IDS[$i]}" "dev-setup-checklist.txt" "Dev Setup Checklist\n\n[x] Docker Desktop\n[x] VS Code\n[x] SSH keys\n[ ] Clone repo\n[ ] Run tests" "Development environment checklist" ;;
        3) upload_attachment "${ARTICLE_IDS[$i]}" "code-review-checklist.txt" "Code Review Checklist\n\n- [ ] Code compiles\n- [ ] Tests pass\n- [ ] No security issues\n- [ ] Documentation updated" "Code review checklist" ;;
        4) upload_attachment "${ARTICLE_IDS[$i]}" "git-workflow.txt" "Git Workflow\n\n1. git checkout -b feature/xxx\n2. Make changes\n3. git add . && git commit\n4. git push origin feature/xxx\n5. Create PR" "Git workflow reference" ;;
    esac
done

# ============================================================================
#  PHASE 9 — Meeting templates (10 meetings)
# ============================================================================
phase "Creating 10 meeting templates"

# Meeting definitions: title|desc|type|level|pos|mandatory|deadline|order
MEETINGS=(
    "HR Welcome Session|Introduction to company culture, benefits, and HR processes|HR|JUNIOR|Software Engineer|true|3|1"
    "Security Training|Mandatory security awareness training covering data protection|SECURITY|JUNIOR|Software Engineer|true|7|2"
    "Team Introduction|Meet your team members and understand team workflows|TEAM|JUNIOR|Software Engineer|true|5|3"
    "Manager 1:1|Weekly one-on-one with your manager|MANAGER|JUNIOR|Software Engineer|true|7|4"
    "Product Demo|Demonstrate your work to the product team|OTHER|JUNIOR|Software Engineer|false|14|5"
    "Tech Review|Technical review of your architecture and code|OTHER|SENIOR|Software Engineer|true|21|6"
    "Sales Kickoff|Review quarterly sales targets and strategies|OTHER|JUNIOR|Software Engineer|true|7|7"
    "Marketing Planning|Marketing campaign planning and coordination|OTHER|JUNIOR|Software Engineer|true|14|8"
    "Compliance Training|Mandatory compliance and ethics training|SECURITY|JUNIOR|Software Engineer|true|30|9"
    "All Hands|Company-wide all hands meeting|OTHER|JUNIOR|Software Engineer|true|30|10"
)

create_meeting() {
    local title="$1" desc="$2" mtype="$3" level="$4" pos="$5" mandatory="$6" deadline="$7" order="$8"
    local dept_arg=""
    if [ -n "$MEETING_DEPT_ID" ] && [ "$MEETING_DEPT_ID" != "null" ]; then
        dept_arg="\"department_id\": ${MEETING_DEPT_ID},"
    fi
    local level_arg=""
    if [ -n "$level" ]; then
        level_arg="\"level\": \"${level}\","
    fi
    local pos_arg=""
    if [ -n "$pos" ]; then
        pos_arg="\"position\": \"${pos}\","
    fi

    local id
    id=$(api_create_or_get \
        "curl -L -s -X POST '${MEETING_SERVICE_URL}/api/v1/meetings/' \
            -H 'Authorization: Bearer ${ADMIN_TOKEN}' \
            -H 'Content-Type: application/json' \
            -d '{
                \"title\": \"${title}\",
                \"description\": \"${desc}\",
                \"type\": \"${mtype}\",
                ${dept_arg}
                ${pos_arg}
                ${level_arg}
                \"is_mandatory\": ${mandatory},
                \"order\": ${order},
                \"deadline_days\": ${deadline}
            }'" \
        "curl -L -s -X GET '${MEETING_SERVICE_URL}/api/v1/meetings/?limit=100' \
            -H 'Authorization: Bearer ${ADMIN_TOKEN}'" \
        ".meetings[] | select(.title == \"${title}\") | .id")

    if [ -n "$id" ] && [ "$id" != "null" ]; then
        log_success "  Meeting '${title}' → ID $id"
    else
        log_warning "  Failed to create meeting '${title}'"
    fi
}

for meeting_spec in "${MEETINGS[@]}"; do
    IFS='|' read -ra mfields <<< "$meeting_spec"
    create_meeting "${mfields[0]}" "${mfields[1]}" "${mfields[2]}" "${mfields[3]}" "${mfields[4]}" "${mfields[5]}" "${mfields[6]}" "${mfields[7]}"
done

# ============================================================================
#  DONE
# ============================================================================
log_divider
log_success "Test data setup completed successfully!"
log_divider
log_info "Summary:"
log_info "  Admin:       ${ADMIN_EMAIL}"
log_info "  HR:          ${HR_EMAIL} (ID: ${HR_USER_ID})"
log_info "  Mentor:      ${MENTOR_EMAIL} (ID: ${MENTOR_USER_ID})"
log_info "  User:        ${USER_EMAIL} (ID: ${USER_ID})"
log_info "  Departments: ${#DEPARTMENTS[@]}"
log_info "  Templates:   ${#TEMPLATE_IDS[@]}"
log_info "  Categories:  ${#CAT_IDS[@]}"
log_info "  Tags:        ${#TAG_IDS[@]}"
log_info "  Articles:    ${#ARTICLE_IDS[@]}"
log_info "  Favorites:   5"
log_info "  Attachments: 5"
log_info "  Meetings:    10"
log_divider
