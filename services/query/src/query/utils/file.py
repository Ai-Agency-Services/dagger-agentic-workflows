
import dagger


async def get_file_size(container: dagger.Container, filepath: str) -> int:
    """Get the size of a file inside a container."""
    try:
        # Run stat command inside the container, relative to its workdir
        size_str = await container.with_exec(
            ["stat", "-c", "%s", filepath]
        ).stdout()
        return int(size_str.strip())
    except Exception as e:
        print(f"Error getting size of {filepath}: {e}")
        return 0
