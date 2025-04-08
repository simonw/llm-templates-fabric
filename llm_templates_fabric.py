from llm import Template, hookimpl
import httpx
from pathlib import Path


@hookimpl
def register_template_loaders(register):
    register("fabric", fabric_template_loader)


def fabric_template_loader(template_path: str) -> Template:
    """
    Load a template from the Fabric repository patterns folder

    Format: NAME_OF_TEMPLATE - loads from patterns/NAME_OF_TEMPLATE/
    """
    template_name = template_path.strip()

    # Build URLs for system and user prompts
    system_url = f"https://raw.githubusercontent.com/danielmiessler/fabric/main/patterns/{template_name}/system.md"
    user_url = f"https://raw.githubusercontent.com/danielmiessler/fabric/main/patterns/{template_name}/user.md"

    system_content = None
    user_content = None

    # Try to fetch system prompt
    try:
        system_response = httpx.get(system_url)
        if system_response.status_code == 200:
            system_content = system_response.text
    except httpx.HTTPError:
        pass

    # Try to fetch user prompt
    try:
        user_response = httpx.get(user_url)
        if user_response.status_code == 200:
            user_content = user_response.text
    except httpx.HTTPError:
        pass

    # If neither prompt was found, raise an error
    if not system_content and not user_content:
        raise ValueError(
            f"Template '{template_name}' not found in Fabric repository (checked patterns/{template_name}/)"
        )

    # Create the template with available content
    template_args = {"name": template_path}

    if system_content:
        template_args["system"] = system_content

    if user_content:
        template_args["prompt"] = user_content

    return Template(**template_args)
