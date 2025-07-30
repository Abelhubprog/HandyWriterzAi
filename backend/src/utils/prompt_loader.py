"""
Prompt loading utilities for HandyWriterz EvidenceGuard system.

This module provides functionality to load and format system prompts
with proper parameter substitution and validation.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any
from string import Template

logger = logging.getLogger(__name__)


class PromptLoader:
    """Utility class for loading and formatting system prompts."""
    
    def __init__(self):
        self.prompts_dir = Path(__file__).resolve().parent.parent / "prompts"
        self._prompt_cache = {}
    
    def load_prompt(self, name: str) -> str:
        """
        Load a prompt file from the prompts directory.
        
        Args:
            name: Name of the prompt file (with or without .txt extension)
            
        Returns:
            Raw prompt content as string
            
        Raises:
            FileNotFoundError: If prompt file doesn't exist
        """
        if not name.endswith('.txt'):
            name += '.txt'
        
        # Check cache first
        if name in self._prompt_cache:
            return self._prompt_cache[name]
        
        prompt_path = self.prompts_dir / name
        
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
        
        try:
            content = prompt_path.read_text(encoding="utf-8")
            # Preprocess content: remove specific lines that are not part of the format string
            cleaned_lines = []
            in_json_block = False
            for line in content.splitlines():
                stripped_line = line.strip()
                
                if stripped_line == '```json':
                    in_json_block = True
                    cleaned_lines.append(line)
                    continue
                elif stripped_line == '```' and in_json_block:
                    in_json_block = False
                    cleaned_lines.append(line)
                    continue

                if in_json_block:
                    # Escape curly braces within the JSON block
                    line = line.replace('{', '{{').replace('}', '}}')

                # Remove lines that are just separators or comments
                if stripped_line.startswith('###') or \
                   stripped_line == '────────────────────────────────────────────────────────' or \
                   stripped_line == '---' or \
                   stripped_line.startswith('#'):
                    continue
                cleaned_lines.append(line) # Keep original indentation for formatting
            processed_content = "\n".join(cleaned_lines)

            self._prompt_cache[name] = processed_content
            logger.info(f"Loaded and processed prompt: {name}")
            return processed_content
        except Exception as e:
            logger.error(f"Failed to load prompt {name}: {str(e)}")
            raise
    
    def format_prompt(self, name: str, **kwargs) -> str:
        """
        Load and format a prompt with parameter substitution.
        
        Args:
            name: Name of the prompt file
            **kwargs: Parameters to substitute in the prompt
            
        Returns:
            Formatted prompt with parameters substituted
            
        Raises:
            KeyError: If required parameters are missing
        """
        prompt_template = self.load_prompt(name)
        
        try:
            # Use Template for safe substitution
            template = Template(prompt_template)
            formatted_prompt = template.substitute(**kwargs)
            
            logger.debug(f"Formatted prompt {name} with parameters: {list(kwargs.keys())}")
            return formatted_prompt
            
        except KeyError as e:
            missing_param = str(e).strip("'")
            logger.error(f"Missing required parameter '{missing_param}' for prompt '{name}'")
            raise KeyError(f"Missing required parameter '{missing_param}' for prompt '{name}'")
    
    def validate_prompt_parameters(self, name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and sanitize prompt parameters.
        
        Args:
            name: Name of the prompt file
            parameters: Parameters to validate
            
        Returns:
            Validated and sanitized parameters
        """
        validated = {}
        
        # Required parameters for evidence_guard_v1
        if name == "evidence_guard_v1.txt":
            required_params = [
                "topic", "design", "year_from", "year_to", "region", 
                "min_sources", "word_count", "allowed_sources"
            ]
            
            for param in required_params:
                if param not in parameters:
                    raise ValueError(f"Missing required parameter: {param}")
            
            # Validate specific parameter types and ranges
            validated["topic"] = str(parameters["topic"]).strip()
            validated["design"] = str(parameters["design"]).strip()
            validated["year_from"] = max(1900, int(parameters["year_from"]))
            validated["year_to"] = min(2030, int(parameters["year_to"]))
            validated["region"] = str(parameters["region"]).strip().upper()
            validated["min_sources"] = max(1, int(parameters["min_sources"]))
            validated["word_count"] = max(100, int(parameters["word_count"]))
            
            # Validate and format allowed_sources
            if isinstance(parameters["allowed_sources"], str):
                validated["allowed_sources"] = parameters["allowed_sources"]
            else:
                validated["allowed_sources"] = json.dumps(
                    parameters["allowed_sources"], 
                    ensure_ascii=False, 
                    indent=2
                )
            
            # Validate year range logic
            if validated["year_from"] > validated["year_to"]:
                raise ValueError("year_from must be <= year_to")
                
        else:
            # For other prompts, pass through with basic validation
            validated = {k: str(v) for k, v in parameters.items()}
        
        return validated
    
    def get_available_prompts(self) -> list[str]:
        """
        Get list of available prompt files.
        
        Returns:
            List of prompt file names
        """
        if not self.prompts_dir.exists():
            return []
        
        return [f.name for f in self.prompts_dir.glob("*.txt")]


# Global instance for easy access
prompt_loader = PromptLoader()


def load_prompt(name: str) -> str:
    """Convenience function to load a prompt."""
    return prompt_loader.load_prompt(name)


def format_prompt(name: str, **kwargs) -> str:
    """Convenience function to load and format a prompt."""
    return prompt_loader.format_prompt(name, **kwargs)


def validate_evidence_guard_params(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function to validate EvidenceGuard parameters."""
    return prompt_loader.validate_prompt_parameters("evidence_guard_v1.txt", parameters)