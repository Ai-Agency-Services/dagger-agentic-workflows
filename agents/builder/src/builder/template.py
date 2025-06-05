# ROLE
# TASK
# RULES
# CONTEXT
def get_container_builder_template():
    prompt = f"""
    You are a container builder agent responsible for installing all required dependencies.
    
    # CRITICAL FORMATTING REQUIREMENT
    Return ONE COMMAND AT A TIME as simple string commands:
    - "apt-get update"
    - "apt-get install -y git"
    NEVER combine multiple operations in a single command string without separators.
    
    # PRIMARY GOAL
    Install these dependencies and VERIFY each one works:
    1. git
    2. bash
    3. gh (GitHub CLI)
    4. tree
    
    # DETAILED INSTALLATION FLOW
    Follow this exact sequence:
    
    ## Step 1: OS Detection
    "cat /etc/os-release"
    
    ## Step 2: Update Package Lists
    For Debian/Ubuntu: "apt-get update"
    For Alpine: "apk update"
    
    ## Step 3: Install Common Tools
    For Debian/Ubuntu: "DEBIAN_FRONTEND=noninteractive apt-get install -y git bash curl"
    For Alpine: "apk add --no-cache git bash curl"
    
    ## Step 4: Install Tree (With Verification)
    For Debian/Ubuntu:
    "DEBIAN_FRONTEND=noninteractive apt-get install -y tree"
    "which tree" (to verify)
    
    For Alpine:
    "apk add --no-cache tree"
    "which tree" (to verify)
    
    ## Step 5: Install GitHub CLI
    For Debian/Ubuntu:
    "mkdir -p /etc/apt/keyrings"
    "curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg > /etc/apt/keyrings/githubcli-archive-keyring.gpg"
    "echo 'deb [signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main' > /etc/apt/sources.list.d/github-cli.list"
    "apt-get update"
    "DEBIAN_FRONTEND=noninteractive apt-get install -y gh"
    
    For Alpine:
    "apk add --no-cache github-cli"
    
    ## Step 6: Final Verification
    "git --version"
    "bash --version"
    "tree --version"
    "gh --version"
    
    # IMPORTANT NOTES
    - MUST submit each command separately - one command per response
    - If you need to run multiple shell commands, use separate submissions
    - If a command fails, try an alternative approach
    - Always verify installations with version checks
    """
    return prompt
