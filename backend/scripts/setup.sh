#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Helper Functions ---
function print_info {
  echo -e "\033[34m[INFO]\033[0m $1"
}

function print_success {
  echo -e "\033[32m[SUCCESS]\033[0m $1"
}

function print_warning {
  echo -e "\033[33m[WARNING]\033[0m $1"
}

function print_error {
  echo -e "\033[31m[ERROR]\033[0m $1"
}

# --- Environment Setup ---
print_info "Setting up Python virtual environment..."
python3 -m venv .venv
source .venv/bin/activate
print_success "Virtual environment created and activated."

print_info "Installing dependencies from requirements.txt..."
pip install -r requirements.txt
print_success "Dependencies installed."

# --- Database Setup ---
print_info "Setting up PostgreSQL database..."
# This assumes PostgreSQL is already installed.
# A more robust script would check for this and provide instructions.
if ! command -v psql &> /dev/null
then
    print_warning "psql command not found. Please ensure PostgreSQL is installed and in your PATH."
else
    # Create the database if it doesn't exist
    if ! psql -lqt | cut -d \| -f 1 | grep -qw handywriterz; then
        createdb handywriterz
        print_success "Database 'handywriterz' created."
    else
        print_info "Database 'handywriterz' already exists."
    fi
    # Enable the pgvector extension
    psql -d handywriterz -c "CREATE EXTENSION IF NOT EXISTS vector;"
    print_success "pgvector extension enabled."
fi

# --- Redis Setup ---
print_info "Setting up Redis..."
# This assumes Redis is already installed.
if ! command -v redis-server &> /dev/null
then
    print_warning "redis-server command not found. Please ensure Redis is installed and in your PATH."
else
    # Start Redis if it's not already running
    if ! redis-cli ping &> /dev/null; then
        redis-server --daemonize yes
        print_success "Redis server started."
    else
        print_info "Redis server is already running."
    fi
fi

# --- Environment Validation ---
print_info "Validating environment..."
if [ ! -f .env ]; then
    print_warning ".env file not found. Copying from .env.example."
    cp .env.example .env
    print_warning "Please fill in the required values in the .env file."
else
    print_info ".env file found."
fi

# --- Migrations ---
print_info "Running database migrations..."
alembic upgrade head
print_success "Database migrations applied."

print_success "Setup complete! You can now start the application."