#!/bin/bash
# Codebuff Agents Feature Development Demo
# This script demonstrates the complete workflow for building a feature

set -e

# Configuration
CONFIG_FILE="demo/codebuff-feature-demo.yaml"
FEATURE_NAME="User Profile Management"
REPO_URL="https://github.com/user/example-app"

echo "🚀 Starting Codebuff Agents Feature Development Demo"
echo "Feature: $FEATURE_NAME"
echo "================================================"

# Step 1: Set up the container environment
echo "📦 Step 1: Setting up container environment..."
CONTAINER=$(dagger call builder --config-file demo/codebuff-feature-demo.yaml build-test-environment \
    --source=. \
    --dockerfile-path="Dockerfile" \
    --open-router-api-key=env:OPENROUTER_API_KEY \
    --provider="openrouter")

echo "✅ Container ready: $CONTAINER"

# Step 2: Explore the codebase
echo "🔍 Step 2: Exploring codebase for user management..."
EXPLORATION_RESULT=$(dagger call codebuff explore-files \
    --container="$CONTAINER" \
    --focus-area="user management and profile features" \
    --openai-api-key=env:OPENAI_API_KEY)

echo "📋 Exploration Results:"
echo "$EXPLORATION_RESULT"
echo ""

# Step 3: Pick relevant files
echo "📂 Step 3: Picking relevant files for the feature..."
FILE_SELECTION=$(dagger call codebuff pick-files \
    --container="$CONTAINER" \
    --task-description="$FEATURE_NAME with avatar upload, bio editing, and privacy settings" \
    --openai-api-key=env:OPENAI_API_KEY)

echo "📝 Selected Files:"
echo "$FILE_SELECTION"
echo ""

# Step 4: Create implementation plan
echo "🧠 Step 4: Creating detailed implementation plan..."
IMPLEMENTATION_PLAN=$(dagger call codebuff create-plan \
    --container="$CONTAINER" \
    --task-description="$FEATURE_NAME with avatar upload, bio editing, and privacy settings" \
    --relevant-files="models/user.py,views/profile.py,templates/profile.html" \
    --openai-api-key=env:OPENAI_API_KEY)

echo "📋 Implementation Plan:"
echo "$IMPLEMENTATION_PLAN"
echo ""

# Step 5: Implement the feature
echo "⚡ Step 5: Implementing the feature..."
IMPLEMENTATION_RESULT=$(dagger call codebuff implement-plan \
    --container="$CONTAINER" \
    --plan="$IMPLEMENTATION_PLAN" \
    --openai-api-key=env:OPENAI_API_KEY)

echo "🔧 Implementation Results:"
echo "$IMPLEMENTATION_RESULT"
echo ""

# Step 6: Review the changes
echo "🔍 Step 6: Reviewing implemented changes..."
REVIEW_RESULT=$(dagger call codebuff review-changes \
    --container="$CONTAINER" \
    --changes-description="$FEATURE_NAME implementation" \
    --openai-api-key=env:OPENAI_API_KEY)

echo "📊 Review Results:"
echo "$REVIEW_RESULT"
echo ""

# Optional: Context pruning for large projects
if [ ${#IMPLEMENTATION_PLAN} -gt 10000 ]; then
    echo "✂️ Step 7: Pruning context for efficiency..."
    PRUNED_CONTEXT=$(dagger call codebuff prune-context \
        --container="$CONTAINER" \
        --context-data="$IMPLEMENTATION_PLAN" \
        --max-tokens=4000 \
        --strategy="smart" \
        --openai-api-key=env:OPENAI_API_KEY)
    
    echo "📝 Pruned Context:"
    echo "$PRUNED_CONTEXT"
fi

echo ""
echo "🎉 Feature Development Demo Complete!"
echo "================================================"
echo "Summary:"
echo "- Explored codebase structure"
echo "- Selected relevant files"
echo "- Created detailed implementation plan"
echo "- Implemented the feature"
echo "- Reviewed changes for quality"
echo ""
echo "Next steps:"
echo "1. Test the implemented feature"
echo "2. Create pull request"
echo "3. Deploy to staging environment"
echo ""
echo "💡 Tip: Use 'dagger call codebuff --help' to see all available commands"