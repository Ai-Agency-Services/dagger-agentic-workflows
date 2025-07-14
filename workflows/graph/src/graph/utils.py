import json
from typing import List

import dagger


def dagger_json_file_to_pydantic(json_file: dagger.File, pydantic_model: type) -> List:
    """
    Convert a Dagger JSON file to a list of Pydantic models.

    Args:
    json_file (dagger.File): The Dagger JSON file to convert.
    pydantic_model (type): The Pydantic model class to use for conversion.

    Returns:
    List: A list of Pydantic models.
    """

    async def convert():
        # Read the contents of the JSON file
        json_content = await json_file.contents()

        # Deserialize JSON content into a list of dictionaries
        data_list = json.loads(json_content)

        # Convert dictionaries back into Pydantic models
        return [pydantic_model.model_validate(item) for item in data_list]

    return convert()
