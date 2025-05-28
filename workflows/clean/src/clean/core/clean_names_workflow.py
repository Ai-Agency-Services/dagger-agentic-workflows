import os
from typing import List, Optional

import dagger
from dagger import dag
from clean.models.config import YAMLConfig
from clean.core.meaningful_names_agent import (
    MeaningfulNamesAgentDependencies, create_meaningful_names_agent)
from clean.core.rag_naming_agent import (RagNamingAgentDependencies,
                                         RenameCandidate,
                                         create_rag_naming_agent)
from clean.utils.llm import create_llm_model, get_llm_credentials
from simple_chalk import green, red, yellow


async def clean_names_workflow(
    config: YAMLConfig,
    provider: str,
    repo_url: str,
    open_router_api_key: Optional[dagger.Secret],
    openai_api_key: Optional[dagger.Secret],
    github_access_token: dagger.Secret,
    branch: str,
    supabase_url: str,
    supabase_key: dagger.Secret,
    model_name: str = "gpt-4",
    max_files: int = 5
) -> dagger.Container:  # Changed return type to dagger.Container
    """
    Main workflow to identify and refactor code with poor naming.
    """
    # Initialize Dagger client
    # Setup container with the repository
    try:
        if openai_api_key:
            print(green("Setting OpenAI API key..."))
            os.environ["OPENAI_API_KEY"] = await openai_api_key.plaintext()
        source = (
            await dag.git(url=repo_url, keep_git_dir=True)
            .with_auth_token(github_access_token)  # Correct method name
            .branch(branch)
            .tree()
        )
    except Exception as e:
        print(red(f"Failed to clone repository: {e}"))
        raise

    container = (
        dag.container()
        .from_("python:3.10-slim")
        .with_directory("/src", source)
        .with_workdir("/src")
        .with_exec(["apt-get", "update"])
        .with_exec(["apt-get", "install", "-y", "git"])
    )

    # Configure Git identity for commits
    container = container.with_exec(
        ["git", "config", "--global", "user.email", "code-refactor-agent@example.com"])
    container = container.with_exec(
        ["git", "config", "--global", "user.name", "Code Refactor Agent"])

    # Create AI model
    try:
        llm_credentials = await get_llm_credentials(
            provider=provider,
            open_router_key=open_router_api_key,
            openai_key=openai_api_key,
        )
    except ValueError as e:
        print(red(f"LLM Configuration Error: {e}"))
        raise

    try:
        model = create_llm_model(
            api_key=llm_credentials.api_key,
            base_url=llm_credentials.base_url,
            model_name=model_name
        )
    except Exception as e:
        # The helper function already prints the error, just re-raise
        raise

    # Define file extensions to index
    file_extensions = [
        ".py", ".js", ".ts", ".jsx", ".tsx", ".java",
        ".c", ".cpp", ".hpp", ".h", ".go", ".rs",
        ".rb", ".php", ".swift", ".kt", ".cs"
    ]

    # Create RAG agent
    rag_agent = create_rag_naming_agent(model)

    # Create dependencies for RAG agent
    rag_deps = RagNamingAgentDependencies(
        container=container,
        config=config,  # Pass config to the agent dependencies
        supabase_url=supabase_url,
        supabase_key=supabase_key,
        openai_api_key=openai_api_key,
        results_limit=10,
        similarity_threshold=0.7
    )

    # Run RAG agent to find renaming candidates
    print(green("Identifying files with poor naming conventions..."))
    try:
        rename_candidates: List[RenameCandidate] = await rag_agent.run(
            prompt="""
            Find the top files in this codebase that could benefit from better naming conventions.
            Focus on variables, functions, and classes with non-descriptive names.
            Provide specific renaming suggestions based on the code's purpose and context.
            """,
            deps=rag_deps
        )
    except Exception as e:
        print(red(f"RAG agent failed: {e}"))
        raise

    # Check if we found any candidates
    if not rename_candidates:
        print(yellow(
            "No renaming candidates found. The code may already follow good naming conventions."))
        return container

    # Group candidates by file
    files_to_refactor = {}
    for candidate in rename_candidates:
        if candidate.filepath not in files_to_refactor:
            files_to_refactor[candidate.filepath] = []
        files_to_refactor[candidate.filepath].append(candidate)

    # Limit the number of files to refactor
    file_paths = list(files_to_refactor.keys())[:max_files]

    if not file_paths:
        print(yellow("No files to refactor after filtering."))
        return container

    # Create meaningful names agent
    names_agent = create_meaningful_names_agent(model)

    # Process each file
    for file_path in file_paths:
        print(green(f"Refactoring {file_path}..."))

        try:
            # Create dependencies for the meaningful names agent
            names_deps = MeaningfulNamesAgentDependencies(
                container=container,
                rename_candidates=files_to_refactor[file_path],
                file_path=file_path
            )

            # Run the meaningful names agent
            refactored_code = await names_agent.run(
                prompt=f"""
                Refactor the code in {file_path} to use more meaningful variable, function, and class names.
                Consider the renaming suggestions provided and ensure the refactored code maintains the same functionality.
                Explain your reasoning for each name change in comments.
                """,
                deps=names_deps
            )

            # Write the refactored code back to the file
            if refactored_code:
                try:
                    # Create a new branch for the changes
                    branch_name = f"refactor/improve-names-{os.path.basename(file_path)}"
                    container = container.with_exec(
                        ["git", "checkout", "-b", branch_name])

                    # Write the changes
                    container = container.with_new_file(
                        file_path, refactored_code)

                    # Commit the changes
                    container = container.with_exec(
                        ["git", "add", file_path])
                    container = container.with_exec([
                        "git",
                        "commit",
                        "-m",
                        f"Refactor: Improve naming conventions in {file_path}"
                    ])

                    print(green(f"Successfully refactored {file_path}"))
                except Exception as e:
                    print(
                        red(f"Failed to commit changes for {file_path}: {e}"))
            else:
                print(yellow(f"No changes made to {file_path}"))
        except Exception as e:
            print(red(f"Failed to refactor {file_path}: {e}"))
            continue

    print(green("Refactoring complete!"))
    return container  # Return the container for future operations
