#!/bin/bash
# create_admin.sh

# Load helper functions
source "$(dirname "$0")/helper.sh"

# Configuration
POSTGRES_USER="roman"
POSTGRES_PASSWORD="test_password"
DATABASE="mentor_bot"

log_divider
log_step "Creating admin user in PostgreSQL database"

# Check if docker-compose is running
if ! docker compose ps postgres 2>/dev/null | grep -q "Up"; then
    log_error "PostgreSQL container is not running. Please start the services first."
    log_info "Run: docker compose up -d"
    exit 1
fi

# SQL query using docker-compose exec
SQL_QUERY="
DO \$\$
DECLARE
    user_exists boolean;
    user_id integer;
BEGIN
    -- Check if admin user already exists
    SELECT EXISTS (
        SELECT 1 FROM auth.users WHERE email = '$ADMIN_EMAIL'
    ) INTO user_exists;
    
    IF NOT user_exists THEN
        -- Insert admin user
        INSERT INTO auth.users (
            email, 
            first_name, 
            last_name, 
            employee_id, 
            password_hash, 
            role, 
            is_active, 
            is_verified,
            created_at
        ) VALUES (
            '$ADMIN_EMAIL', 
            'Admin', 
            'Adminov', 
            'admin001', 
            '\$2b\$12\$1hhh1fvR8Qm0s2t3qBHhfOBvMCnusOIVmPINCQzPodlQH9b42.pjy',
            'ADMIN', 
            true, 
            true, 
            NOW()
        )
        RETURNING id INTO user_id;
        
        RAISE NOTICE 'Admin user created successfully with ID: %', user_id;
    ELSE
        RAISE NOTICE 'Admin user already exists';
        
        -- Get existing admin ID
        SELECT id INTO user_id FROM auth.users WHERE email = '$ADMIN_EMAIL';
        RAISE NOTICE 'Admin user ID: %', user_id;
    END IF;
END
\$\$;
"

log_info "Executing SQL query to create admin user..."
log_info "Database: $DATABASE"
log_info "PostgreSQL User: $POSTGRES_USER"

# Execute using docker-compose with error handling
if docker compose exec -T postgres psql \
    -U "$POSTGRES_USER" \
    -d "$DATABASE" \
    -c "$SQL_QUERY"; then
    
    log_success "Admin user creation completed"
else
    log_error "Failed to create admin user"
    log_warning "Check if:"
    log_warning "1. PostgreSQL container is running"
    log_warning "2. Database '$DATABASE' exists"
    log_warning "3. User '$POSTGRES_USER' has proper permissions"
    exit 1
fi

log_divider
log_success "================================"
log_success "Admin credentials created:"
log_success "Email: $ADMIN_EMAIL"
log_success "Password: $ADMIN_PASSWORD"
log_success "================================"
log_divider

# Optional: Test the admin user by getting a token
log_step "Testing admin user authentication..."

# Wait a bit for the user to be available
sleep 2

# Try to get admin token (requires auth service to be running)
AUTH_SERVICE_URL="http://localhost:8001"
if curl -s -o /dev/null -w "%{http_code}" "$AUTH_SERVICE_URL/health" | grep -q "200"; then
    log_info "Auth service is running, testing login..."
    
    TOKEN_RESPONSE=$(curl -s -X POST "$AUTH_SERVICE_URL/api/v1/auth/login" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=$ADMIN_EMAIL&password=$ADMIN_PASSWORD&grant_type=password")
    
    if echo "$TOKEN_RESPONSE" | jq -e '.access_token' >/dev/null 2>&1; then
        log_success "Admin authentication successful!"
        ACCESS_TOKEN=$(echo "$TOKEN_RESPONSE" | jq -r '.access_token')
        log_info "Access token obtained (first 20 chars): ${ACCESS_TOKEN:0:20}..."
        
        # Save token to file
        echo "$ACCESS_TOKEN" > .admin_token
        chmod 600 .admin_token
        log_success "Admin token saved to .admin_token file"
    else
        log_warning "Admin authentication test failed"
        log_warning "Response: $TOKEN_RESPONSE"
    fi
else
    log_info "Auth service is not running yet"
    log_info "Start it with: docker compose up auth_service"
    log_info "Then test login with: ./scripts/helper.sh"
fi

log_divider