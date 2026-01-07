from llm import Template, hookimpl
import httpx
from pathlib import Path
import os


@hookimpl
def register_template_loaders(register):
    register("fabric", fabric_template_loader)


def fabric_template_loader(template_path: str) -> Template:
    """
    Load a template from local Fabric patterns or fallback to GitHub repository
    
    Searches in this order:
    1. ~/.config/fabric/custom_patterns/NAME_OF_TEMPLATE/
    2. ~/.config/fabric/patterns/NAME_OF_TEMPLATE/
    3. https://github.com/danielmiessler/Fabric/data/patterns/NAME_OF_TEMPLATE/
    
    Format: NAME_OF_TEMPLATE
    
    Language support:
    Set LLM_OUTPUT_LANGUAGE environment variable to specify output language.
    Example: export LLM_OUTPUT_LANGUAGE=fr
    Supported codes: fr, en, es, de, it, pt, zh, ja, etc.
    """
    template_name = template_path.strip()
    
    # Get language from environment variable
    output_language = os.environ.get('LLM_OUTPUT_LANGUAGE', '').strip()
    
    # Define local pattern directories (in order of priority)
    fabric_config = Path.home() / ".config" / "fabric"
    local_dirs = [
        fabric_config / "custom_patterns" / template_name,
        fabric_config / "patterns" / template_name,
    ]
    
    system_content = None
    user_content = None
    source = None
    
    # Try to load from local filesystem (custom_patterns first, then patterns)
    for local_pattern_dir in local_dirs:
        if local_pattern_dir.exists() and local_pattern_dir.is_dir():
            local_system = local_pattern_dir / "system.md"
            local_user = local_pattern_dir / "user.md"
            
            if local_system.exists():
                try:
                    system_content = local_system.read_text(encoding='utf-8')
                    source = f"local ({local_pattern_dir.parent.name})"
                except Exception:
                    pass
            
            if local_user.exists():
                try:
                    user_content = local_user.read_text(encoding='utf-8')
                    source = f"local ({local_pattern_dir.parent.name})"
                except Exception:
                    pass
            
            # If we found content in this directory, stop searching
            if system_content or user_content:
                break
    
    # If not found locally, fallback to GitHub
    if not system_content and not user_content:
        # Build URLs for system and user prompts
        system_url = f"https://raw.githubusercontent.com/danielmiessler/Fabric/refs/heads/main/data/patterns/{template_name}/system.md"
        user_url = f"https://raw.githubusercontent.com/danielmiessler/Fabric/refs/heads/main/data/patterns/{template_name}/user.md"
        
        # Try to fetch system prompt
        try:
            system_response = httpx.get(system_url)
            if system_response.status_code == 200:
                system_content = system_response.text
                source = "remote"
        except httpx.HTTPError:
            pass
        
        # Try to fetch user prompt
        try:
            user_response = httpx.get(user_url)
            if user_response.status_code == 200:
                user_content = user_response.text
                source = "remote"
        except httpx.HTTPError:
            pass
    
    # If neither prompt was found locally or remotely, raise an error
    if not system_content and not user_content:
        local_paths = " or ".join([str(d) for d in local_dirs])
        raise ValueError(
            f"Template '{template_name}' not found locally in {local_paths} "
            f"or in Fabric repository (checked data/patterns/{template_name}/)"
        )
    
    # Add language instruction to system prompt if language is specified
    if output_language:
        language_map = {
            'fr': 'French',
            'en': 'English',
            'es': 'Spanish',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'zh': 'Chinese',
            'ja': 'Japanese',
            'ko': 'Korean',
            'ru': 'Russian',
            'ar': 'Arabic',
            'nl': 'Dutch',
            'pl': 'Polish',
            'sv': 'Swedish',
            'tr': 'Turkish',
        }
        
        language_name = language_map.get(output_language.lower(), output_language)
        language_instruction = f"\n\n# OUTPUT LANGUAGE\n\nProvide all output in {language_name}. Response sections titles will be translate too"
        
        # Add language instruction to system content (preferred location)
        if system_content:
            system_content += language_instruction
        # If no system content, add to user content
        elif user_content:
            user_content += language_instruction
    
    # Create the template with available content
    template_args = {"name": template_path}
    
    if system_content:
        template_args["system"] = system_content
    
    if user_content:
        template_args["prompt"] = user_content
    
    return Template(**template_args)