1. Add new workflow file `.github/workflows/smell-graph.yml` (do not modify existing ci.yml):

name: Smell Graph Report

on:
  workflow_dispatch:
    inputs:
      target_repo_url:
        description: "Repository URL to analyze (not this repo)"
        required: true
      target_branch:
        description: "Branch to analyze"
        required: true
        default: "main"
      post_comment:
        description: "Post PR comment when running on pull_request"
        required: false
        default: "true"
  pull_request:
    types: [opened, synchronize, reopened]

permissions:
  contents: read
  pull-requests: write

jobs:
  smell-graph:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout this repository (workflow sources)
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Install uv (python env manager)
        run: |
          curl -LsSf https://astral.sh/uv/install.sh | sh
          echo "$HOME/.local/bin" >> $GITHUB_PATH

      - name: Install Dagger CLI
        run: |
          curl -L https://dl.dagger.io/dagger/install.sh | DAGGER_VERSION=v0.18.18 sh
          echo "$PWD/bin" >> $GITHUB_PATH

      - name: Verify tools
        run: |
          dagger version
          uv --version

      # Build graph against external repo via repository_url/branch
      - name: Build Graph for target repository
        env:
          GH_PAT: ${{ secrets.GH_PAT || github.token }}
          NEO4J_PASSWORD: ${{ secrets.NEO4J_PASSWORD }}
          NEO4J_AUTH: ${{ secrets.NEO4J_AUTH }}
          OPENROUTER_API_KEY: ${{ secrets.OPENROUTER_API_KEY }}
        run: |
          dagger call graph build-graph-for-repository \
            --config-file=workflows/graph/demo/agencyservices.yaml \
            --github-access-token=env:GH_PAT \
            --repository-url="${{ inputs.target_repo_url || github.event.pull_request.head.repo.clone_url }}" \
            --branch="${{ inputs.target_branch || github.event.pull_request.head.ref }}" \
            --neo-password=env:NEO4J_PASSWORD \
            --neo-auth=env:NEO4J_AUTH \
            --open-router-api-key=env:OPENROUTER_API_KEY

      # Run smell analysis using the same Neo4j cache volume
      - name: Analyze Smells (verbose with links)
        id: smell
        env:
          # Ensure config.git has repo_url/branch for link generation (optional if already in YAML)
          GITHUB_REPO_URL: ${{ inputs.target_repo_url || github.event.pull_request.head.repo.html_url }}
          GITHUB_BRANCH: ${{ inputs.target_branch || github.event.pull_request.head.ref }}
        run: |
          # Optionally: inject repo_url/branch into smell config file prior to run if desired
          # yq -iy \
          #   '.git.repo_url = env(GITHUB_REPO_URL) | .git.branch = env(GITHUB_BRANCH)' \
          #   workflows/smell/demo/agencyservices.yaml

          dagger call smell analyze-codebase \
            --config-file=workflows/smell/demo/agencyservices.yaml \
            --neo-data=cache:neo4j-data \
            > smell_report.txt

          echo "report<<__EOF__" >> $GITHUB_OUTPUT
          cat smell_report.txt >> $GITHUB_OUTPUT
          echo "__EOF__" >> $GITHUB_OUTPUT

      - name: Upload Smell Report Artifact
        uses: actions/upload-artifact@v4
        with:
          name: smell-report
          path: smell_report.txt

      - name: Comment on PR with Smell Report (optional)
        if: ${{ github.event_name == 'pull_request' && inputs.post_comment == 'true' }}
        uses: actions/github-script@v7
        with:
          script: |
            const body = `### Code Smell Report\n\n<details>\n<summary>Click to expand</summary>\n\n\n${{ steps.smell.outputs.report }}\n\n</details>`;
            github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              body,
            });

2. Secrets required in the repository running the workflow:
- GH_PAT (optional) or rely on GITHUB_TOKEN: repo read access to clone target repo
- NEO4J_PASSWORD and NEO4J_AUTH: the auth string (e.g., "neo4j/yourpassword") used by Neo4j container
- OPENROUTER_API_KEY or OPENAI_API_KEY: for builder environment/model bootstrap (optional but recommended)

3. Link generation in reports
- Ensure the smell YAML has:

```yaml
git:
  repo_url: https://github.com/your-org/your-repo
  branch: main
```

- Or uncomment the yq step to inject env(GITHUB_REPO_URL)/env(GITHUB_BRANCH) into workflows/smell/demo/agencyservices.yaml on-the-fly.

4. Notes on modes
- Remote clone mode (recommended): already supported, just pass repository_url/branch as shown.
- Attached directory mode: if you must mount an already-checked-out repo, we can add a new Graph function `build_graph_for_directory(local_path)` that uses the local workspace as the Dagger source instead of `dag.git`. This is an optional enhancement and not required for the remote mode above.

5. Validation
- Run locally first (requires Dagger installed):

```bash
dagger call graph build-graph-for-repository \
  --config-file=workflows/graph/demo/agencyservices.yaml \
  --github-access-token=env:GH_PAT \
  --repository-url="https://github.com/your-org/other-repo" \
  --branch=main \
  --neo-password=env:NEO4J_PASSWORD \
  --neo-auth=env:NEO4J_AUTH \
  --open-router-api-key=env:OPENROUTER_API_KEY

dagger call smell analyze-codebase \
  --config-file=workflows/smell/demo/agencyservices.yaml \
  --neo-data=cache:neo4j-data
```

6. Optional follow-ups
- Add a threshold input (e.g., minimum severity to comment)
- Add matrix to run multiple branches
- Save graph DB dumps as artifacts if needed