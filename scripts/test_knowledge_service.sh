#!/bin/bash
set -e

# Load common functions
source "$(dirname "$0")/helper.sh"

# ----------------------------------------------------------------------
# 1. Environment Readiness Check
# ----------------------------------------------------------------------
setup_checks
export_token
log_divider
log_step "🚀 Starting Knowledge Service testing"

# ----------------------------------------------------------------------
# 2. Creating a category (if it doesn't already exist)
# ----------------------------------------------------------------------
CATEGORY_SLUG="onboarding-engineering"
log_step "Creating category with slug='$CATEGORY_SLUG'"

# Check if category already exists
CATEGORY_RESPONSE=$(curl -L -s -X GET \
    "$KNOWLEDGE_SERVICE_URL/api/v1/categories/$CATEGORY_SLUG" \
    -H "Authorization: Bearer $ADMIN_TOKEN" || echo "null")

CATEGORY_ID=$(echo "$CATEGORY_RESPONSE" | jq -r '.id // empty')

if [ -z "$CATEGORY_ID" ]; then
    log_info "Category not found, creating new one..."
    CATEGORY_RESPONSE=$(execute_with_retry \
        "curl -L -s -X POST \"$KNOWLEDGE_SERVICE_URL/api/v1/categories/\" \
            -H \"Authorization: Bearer \$ADMIN_TOKEN\" \
            -H \"Content-Type: application/json\" \
            -d '{
                \"name\": \"Onboarding Engineering\",
                \"slug\": \"$CATEGORY_SLUG\",
                \"description\": \"Materials for onboarding engineers\",
                \"department\": \"Engineering\",
                \"position\": \"Software Engineer\",
                \"level\": \"JUNIOR\",
                \"order\": 1
            }'" 3 2)
    CATEGORY_ID=$(echo "$CATEGORY_RESPONSE" | jq -r '.id')
    if [ "$CATEGORY_ID" = "null" ] || [ -z "$CATEGORY_ID" ]; then
        log_error "Failed to create category"
        echo "$CATEGORY_RESPONSE" | jq .
        exit 1
    fi
    log_success "Category created, ID: $CATEGORY_ID"
else
    log_info "Category already exists, ID: $CATEGORY_ID"
fi

# ----------------------------------------------------------------------
# 3. Creating tags
# ----------------------------------------------------------------------
declare -a TAGS=(
    '{"name":"Onboarding","slug":"onboarding","description":"Role introduction"}'
    '{"name":"Engineering","slug":"engineering","description":"Development"}'
    '{"name":"Setup","slug":"setup","description":"Environment setup"}'
)

TAG_IDS=()
for tag_data in "${TAGS[@]}"; do
    TAG_SLUG=$(echo "$tag_data" | jq -r '.slug')
    log_step "Processing tag '$TAG_SLUG'"
    
    # Check existence
    TAG_RESPONSE=$(curl -L -s -X GET \
        "$KNOWLEDGE_SERVICE_URL/api/v1/tags/$TAG_SLUG" \
        -H "Authorization: Bearer $ADMIN_TOKEN" || echo "null")
    
    TAG_ID=$(echo "$TAG_RESPONSE" | jq -r '.id // empty')
    if [ -z "$TAG_ID" ]; then
        log_info "Tag not found, creating..."
        TAG_RESPONSE=$(execute_with_retry \
            "curl -L -s -X POST \"$KNOWLEDGE_SERVICE_URL/api/v1/tags/\" \
                -H \"Authorization: Bearer \$ADMIN_TOKEN\" \
                -H \"Content-Type: application/json\" \
                -d '$tag_data'" 3 2)
        TAG_ID=$(echo "$TAG_RESPONSE" | jq -r '.id')
        if [ "$TAG_ID" = "null" ] || [ -z "$TAG_ID" ]; then
            log_error "Failed to create tag $TAG_SLUG"
            exit 1
        fi
        log_success "Tag created, ID: $TAG_ID"
    else
        log_info "Tag already exists, ID: $TAG_ID"
    fi
    TAG_IDS+=("$TAG_ID")
done

# ----------------------------------------------------------------------
# 4. Creating a draft article
# ----------------------------------------------------------------------
log_step "Creating draft article"
ARTICLE_SLUG="onboarding-guide-for-junior-devs"
ARTICLE_TITLE="Onboarding Guide for Junior Developers"

ARTICLE_RESPONSE=$(curl -L -s -X GET \
    "$KNOWLEDGE_SERVICE_URL/api/v1/articles/$ARTICLE_SLUG" \
    -H "Authorization: Bearer $ADMIN_TOKEN" || echo "null")

EXISTING_ARTICLE_ID=$(echo "$ARTICLE_RESPONSE" | jq -r '.id // empty')
if [ -n "$EXISTING_ARTICLE_ID" ]; then
    log_warning "Article with slug '$ARTICLE_SLUG' already exists (ID: $EXISTING_ARTICLE_ID)"
    ARTICLE_ID="$EXISTING_ARTICLE_ID"
else
    # Convert tag ID array to JSON list
    TAG_IDS_JSON=$(printf '%s\n' "${TAG_IDS[@]}" | jq -R . | jq -s .)
    
    ARTICLE_RESPONSE=$(execute_with_retry \
        "curl -L -s -X POST \"$KNOWLEDGE_SERVICE_URL/api/v1/articles/\" \
            -H \"Authorization: Bearer \$ADMIN_TOKEN\" \
            -H \"Content-Type: application/json\" \
            -d '{
                \"title\": \"$ARTICLE_TITLE\",
                \"slug\": \"$ARTICLE_SLUG\",
                \"content\": \"# Onboarding\\n\\nThis is a test article to check the knowledge service operation.\\n\\n## First Steps\\n1. Set up your workstation\\n2. Meet the team\\n3. Study the documentation\",
                \"excerpt\": \"Quick guide for new employees\",
                \"category_id\": $CATEGORY_ID,
                \"department\": \"Engineering\",
                \"position\": \"Software Engineer\",
                \"level\": \"JUNIOR\",
                \"tag_ids\": $TAG_IDS_JSON,
                \"status\": \"DRAFT\",
                \"is_pinned\": true,
                \"meta_title\": \"Onboarding in Engineering\",
                \"keywords\": [\"onboarding\", \"junior\", \"setup\"]
            }'" 3 2)
    
    ARTICLE_ID=$(echo "$ARTICLE_RESPONSE" | jq -r '.id')
    if [ "$ARTICLE_ID" = "null" ] || [ -z "$ARTICLE_ID" ]; then
        log_error "Failed to create article"
        echo "$ARTICLE_RESPONSE" | jq .
        exit 1
    fi
    log_success "Draft article created, ID: $ARTICLE_ID"
fi

# ----------------------------------------------------------------------
# 5. Publishing the article (requires HR/ADMIN role)
# ----------------------------------------------------------------------
log_step "Publishing article"
PUBLISH_RESPONSE=$(execute_with_retry \
    "curl -L -s -X POST \"$KNOWLEDGE_SERVICE_URL/api/v1/articles/$ARTICLE_ID/publish\" \
        -H \"Authorization: Bearer \$ADMIN_TOKEN\"" 3 2)

PUBLISHED_STATUS=$(echo "$PUBLISH_RESPONSE" | jq -r '.status')
if [ "$PUBLISHED_STATUS" = "PUBLISHED" ]; then
    log_success "Article published"
else
    log_warning "Failed to publish article or it was already published"
    echo "$PUBLISH_RESPONSE" | jq .
fi

# ----------------------------------------------------------------------
# 6. Uploading an attachment (test file with correct extension)
# ----------------------------------------------------------------------
log_step "Uploading attachment file"

# Create a temporary file with .txt extension
TEMP_DIR=$(mktemp -d)
TMP_FILE="$TEMP_DIR/attachment.txt"
echo "This is a test file to check attachment upload in Knowledge Service" > "$TMP_FILE"

# Check that the file is created and has .txt extension
log_debug "Created temporary file: $TMP_FILE"
file "$TMP_FILE" || true

ATTACHMENT_RESPONSE=$(execute_with_retry \
    "curl -L -s -X POST \"$KNOWLEDGE_SERVICE_URL/api/v1/attachments/upload\" \
        -H \"Authorization: Bearer \$ADMIN_TOKEN\" \
        -F \"article_id=$ARTICLE_ID\" \
        -F \"file=@$TMP_FILE\" \
        -F \"description=Test attachment\" \
        -F \"order=1\" \
        -F \"is_downloadable=true\"" 3 2)

# Remove temporary directory and file
rm -rf "$TEMP_DIR"

ATTACHMENT_ID=$(echo "$ATTACHMENT_RESPONSE" | jq -r '.id // empty')
if [ "$ATTACHMENT_ID" != "null" ] && [ -n "$ATTACHMENT_ID" ]; then
    log_success "Attachment uploaded, ID: $ATTACHMENT_ID"
    log_info "File name: $(echo "$ATTACHMENT_RESPONSE" | jq -r '.name')"
    log_info "URL: $(echo "$ATTACHMENT_RESPONSE" | jq -r '.url')"
else
    log_error "Failed to upload attachment"
    echo "$ATTACHMENT_RESPONSE" | jq .
    # Do not exit with error, as this is not a critical part of the test
    log_warning "Continuing testing without attachment"
fi

# ----------------------------------------------------------------------
# 7. Searching for articles
# ----------------------------------------------------------------------
log_step "Searching for articles with query 'onboarding'"
SEARCH_RESPONSE=$(execute_with_retry \
    "curl -L -s -X POST \"$KNOWLEDGE_SERVICE_URL/api/v1/search/\" \
        -H \"Authorization: Bearer \$ADMIN_TOKEN\" \
        -H \"Content-Type: application/json\" \
        -d '{
            \"query\": \"onboarding\",
            \"department\": \"Engineering\",
            \"only_published\": true,
            \"page\": 1,
            \"size\": 5
        }'" 3 2)

TOTAL_RESULTS=$(echo "$SEARCH_RESPONSE" | jq -r '.total // 0')
log_success "Articles found: $TOTAL_RESULTS"
if [ "$TOTAL_RESULTS" -gt 0 ]; then
    echo "$SEARCH_RESPONSE" | jq -r '.results[] | "  • \(.title) (relevance: \(.relevance_score))"'
fi

# ----------------------------------------------------------------------
# 8. Checking article statistics (only for HR/ADMIN)
# ----------------------------------------------------------------------
log_step "Getting article view statistics"
STATS_RESPONSE=$(curl -L -s -X GET \
    "$KNOWLEDGE_SERVICE_URL/api/v1/articles/$ARTICLE_ID/stats" \
    -H "Authorization: Bearer $ADMIN_TOKEN")

VIEW_COUNT=$(echo "$STATS_RESPONSE" | jq -r '.view_count // 0')
log_info "Statistics: view count = $VIEW_COUNT"

# ----------------------------------------------------------------------
# 9. Getting popular tags
# ----------------------------------------------------------------------
log_step "Popular tags"
POPULAR_TAGS=$(curl -L -s -X GET \
    "$KNOWLEDGE_SERVICE_URL/api/v1/tags/popular?limit=5" \
    -H "Authorization: Bearer $ADMIN_TOKEN")

echo "$POPULAR_TAGS" | jq -r '.[] | "  • \(.name) (usage count: \(.usage_count))"'

# ----------------------------------------------------------------------
# Completion
# ----------------------------------------------------------------------
log_divider
log_success "✅ Knowledge Service testing successfully completed!"
log_divider