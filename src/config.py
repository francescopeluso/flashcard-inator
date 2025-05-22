"""
File:         config.py
Description:  Configuration management for the Obsidian to Anki flashcards generator
Author:       Francesco Peluso (@francescopeluso)
Date:         2025-05-22
Version:      1.0
"""

from dataclasses import dataclass
from typing import Optional

@dataclass
class Config:
    """Configuration class for the application"""
    
    provider: str = "ollama"
    base_url: Optional[str] = None
    model: Optional[str] = None
    verbose: bool = False
    
    def __post_init__(self):
        """Validate and set default values after initialization"""
        # Normalize provider name to lowercase
        self.provider = self.provider.lower()
        
        # Validate provider choice
        if self.provider not in ["ollama", "lmstudio"]:
            raise ValueError("Provider must be 'ollama' or 'lmstudio'")
        
        # Set default URLs based on provider
        if self.base_url is None:
            if self.provider == "ollama":
                self.base_url = "http://localhost:11434"
            else:  # lmstudio
                self.base_url = "http://localhost:1234"
        
        # Set default model names based on provider
        if self.model is None:
            if self.provider == "ollama":
                self.model = "gemma3"
            else:  # lmstudio
                self.model = "local-model"
    
    @property
    def endpoint(self) -> str:
        """Get the appropriate API endpoint based on provider"""
        # Build endpoint URL based on provider
        if self.provider == "ollama":
            return f"{self.base_url}/api/generate"
        else:  # lmstudio
            return f"{self.base_url}/v1/chat/completions"