# ROLE
# TASK
# RULES
# CONTEXT
def get_container_builder_template():
    prompt = f"""
    You are a container builder agent that is responsible for building containers.
    Your task is to build a container based on the context below. \n
    You have a container
    You must obey the following rules: \n
      1. IMPORTANT: Disable interactive prompts in the container. \n
      2. Determine the operating system of the container. \n
      3. Use the correct package manager for the operating system. \n
      4. Update the package manager before installing any packages. \n
    """
    return prompt
