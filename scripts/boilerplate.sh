#!/bin/bash
# Exit immediately if a command fails.
set -e

# Check if an API name is provided.
if [ -z "$1" ]; then
  echo "Usage: $0 <api-name>"
  exit 1
fi

API_NAME="$1"

echo "Starting boilerplate conversion for API: ${API_NAME}..."

# Remove sample files.
echo "Removing sample endpoints and test files..."
rm -rf src/api/v1/endpoints/hello.py src/services/hello.py \
       tests/unit/test_hello_endpoints.py \
       tests/contract/test_hello_contract.py \
       tests/integration/test_hello_integration.py \
       tests/e2e/test_hello_workflow.py

# Update README.md
if [ -f README.md ]; then
  echo "Updating README.md with API name..."
  sed -i "s/{{api-name}}/${API_NAME}/g" README.md
else
  echo "README.md not found. Creating README.md with seed content..."
  cat <<EOF > README.md
# ${API_NAME}

Welcome to the ${API_NAME} API.
This project is now set up and ready for development.
EOF
fi

# Update ./docs/api/endpoints.md
if [ -f ./docs/api/endpoints.md ]; then
  echo "Updating ./docs/api/endpoints.md with API name..."
  sed -i "s/{{api-name}}/${API_NAME}/g" ./docs/api/endpoints.md
else
  echo "File ./docs/api/endpoints.md not found. Skipping..."
fi

# Update ./docs/evolution_guide.md
if [ -f ./docs/evolution_guide.md ]; then
  echo "Updating ./docs/evolution_guide.md with API name..."
  sed -i "s/{{api-name}}/${API_NAME}/g" ./docs/evolution_guide.md
else
  echo "File ./docs/evolution_guide.md not found. Skipping..."
fi

# Update Docker Compose files.
DOCKER_FILES=(./docker/docker-compose.prod.yml ./docker/docker-compose.dev.yml)
for file in "${DOCKER_FILES[@]}"; do
  if [ -f "$file" ]; then
    echo "Updating $file with API name for POSTGRES_DB..."
    sed -i "s/{{api-name}}/${API_NAME}/g" "$file"
  else
    echo "File $file not found. Skipping..."
  fi
done

# Update .devcontainer/devcontainer.json
if [ -f .devcontainer/devcontainer.json ]; then
  echo "Updating .devcontainer/devcontainer.json with API name..."
  sed -i "s/{{ api-name }}/${API_NAME}/g" .devcontainer/devcontainer.json
else
  echo "File .devcontainer/devcontainer.json not found. Skipping..."
fi

# Remove existing git history.
if [ -d .git ]; then
  echo "Removing existing .git directory..."
  rm -rf .git
else
  echo "No existing .git directory found."
fi

# Initialize a new git repository.
echo "Initializing new git repository..."
git init

# Stage all files and make the initial commit.
git add .
git commit -m "Initial commit - boilerplate conversion for ${API_NAME}"

echo "Boilerplate conversion complete. Your repository is now set up with API name: ${API_NAME}"
