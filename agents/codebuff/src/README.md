# Codebuff-Equivalent Agents

This module provides agents that replicate the core functionality of Codebuff's internal agent system, built using the dagger-agents technology stack.

## Overview

Codebuff uses a sophisticated multi-agent architecture where specialized agents collaborate to understand, plan, and execute complex coding tasks. This implementation recreates those capabilities using your existing tech stack.

## Agents Implemented

### 1. File Explorer Agent
**Equivalent to:** Codebuff's "Dora the File Explorer"
- Maps project structure and architecture
- Identifies key files and directories
- Provides comprehensive codebase context

### 2. File Picker Agent
**Equivalent to:** Codebuff's File Picker
- Selects most relevant files for a given task
- Filters out irrelevant files
- Prioritizes files based on task relevance

### 3. Thinker/Planner Agent
**Equivalent to:** Codebuff's Strategic Planner
- Analyzes task complexity and requirements
- Creates detailed execution plans
- Identifies risks and dependencies

## Usage

```python
from dagger import dag

# Initialize
equivalents = await dag.codebuff_equivalents().create(config_file)

# Explore codebase
exploration = await equivalents.explore_files(container, "API endpoints")

# Pick relevant files
file_selection = await equivalents.pick_files(container, "Add rate limiting")

# Create execution plan
plan = await equivalents.create_plan(container, "Add rate limiting")
```

## Installation

```bash
dagger call codebuff-equivalents --help
```
