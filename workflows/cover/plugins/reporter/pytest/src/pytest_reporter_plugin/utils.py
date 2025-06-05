from typing import List, Tuple

import dagger
from bs4 import BeautifulSoup


async def find_index_html_files(
    container: dagger.Container, directory: str
) -> List[Tuple[str, str]]:
    """Find the index.html files in the test container and return a list of (dir_path, file_path) tuples."""
    print(f"Finding index.html files in {directory}")

    result = await container.with_exec(
        [
            "sh",
            "-c",
            f"""
                find "{directory}" -type f -name "index.html" | while read -r file_path; do
                dir_path=$(dirname "$file_path")
                echo "Directory: $dir_path, File Path: $file_path"
                done
            """,
        ]
    ).stdout()

    index_files: List[Tuple[str, str]] = []
    for line in result.strip().splitlines():
        parts = line.split(", ")
        dir_path = parts[0].replace("Directory: ", "").strip()
        file_path = parts[1].replace("File Path: ", "").strip()
        index_files.append((dir_path, file_path))

    return index_files


from bs4 import BeautifulSoup


def parse_code(html_content):
    """
    Extracts Python code lines from the HTML markup of a coverage report.

    Parameters:
        html_content (str): The HTML content of the coverage report.

    Returns:
        str: Extracted Python code as a single string.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    code_lines = []

    # Find all paragraphs (<p>) under the <main> tag
    main_content = soup.find("main", id="source")
    if not main_content:
        return ""

    for p_tag in main_content.find_all("p"):
        # Find the text within the <span class="t"> tag, which contains the code
        code_span = p_tag.find("span", class_="t")
        if code_span:
            # Append the text (code line) to the list
            code_lines.append(code_span.get_text())

    # Join all lines with newline characters to reconstruct the code
    return "\n".join(code_lines)
