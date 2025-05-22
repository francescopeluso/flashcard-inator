"""
File:         obsidian_processor.py
Description:  Processes Obsidian Markdown files and extracts content for flashcard generation
Author:       Francesco Peluso (@francescopeluso)
Date:         2025-05-22
Version:      1.0
"""

import re
from pathlib import Path
from typing import List

from .config import Config


class ObsidianProcessor:
    """Handles processing of Obsidian Markdown files"""
    
    def __init__(self, vault_path: str, config: Config):
        """
        Initialize the Obsidian processor
        
        Args:
            vault_path: Path to the Obsidian vault
            config: Application configuration
        """
        self.vault_path = Path(vault_path)
        self.config = config
        
        # Validate vault path exists and is directory
        if not self.vault_path.exists():
            raise FileNotFoundError(f"Vault path not found: {vault_path}")
        
        if not self.vault_path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {vault_path}")
    
    def get_markdown_files(self) -> List[Path]:
        """
        Get all Markdown files from the vault
        
        Returns:
            List of Path objects for .md files
        """
        # Recursively find all .md files in vault
        return list(self.vault_path.rglob("*.md"))
    
    def read_file_content(self, file_path: Path) -> str:
        """
        Read and clean Markdown file content
        
        Args:
            file_path: Path to the Markdown file
            
        Returns:
            Cleaned content string
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remove YAML frontmatter
            content = re.sub(r'^---\n.*?\n---\n', '', content, flags=re.DOTALL)
            
            # Remove Obsidian internal links [[link]]
            content = re.sub(r'\[\[([^\]]+)\]\]', r'\1', content)
            
            # Remove tags #tag
            content = re.sub(r'#\w+', '', content)
            
            # Remove HTML comments
            content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
            
            # Replace LaTeX blocks with simplified placeholders to avoid parsing issues
            # Inline LaTeX
            content = re.sub(r'\$([^\$]+)\$', r'LATEX_EXPRESSION: \1', content)
            # Block LaTeX
            content = re.sub(r'\$\$(.*?)\$\$', r'LATEX_BLOCK: \1', content, flags=re.DOTALL)
            
            # Replace code blocks with simplified versions
            content = re.sub(r'```[a-zA-Z]*\n(.*?)```', r'CODE_BLOCK: \1', content, flags=re.DOTALL)
            content = re.sub(r'`([^`]+)`', r'CODE: \1', content)
            
            # Clean extra whitespace
            content = re.sub(r'\n\s*\n', '\n\n', content)
            content = re.sub(r'[ \t]+', ' ', content)
            
            return content.strip()
        
        except Exception as e:
            if self.config.verbose:
                print(f"Error reading file {file_path}: {e}")
            return ""
    
    def should_process_file(self, file_path: Path, content: str) -> bool:
        """
        Determine if a file should be processed for flashcard generation
        
        Args:
            file_path: Path to the file
            content: File content
            
        Returns:
            True if file should be processed
        """
        # Skip files that are too short
        if len(content.strip()) < 100:
            if self.config.verbose:
                print(f"  ⏭️ Skipped: Content too short ({len(content.strip())} chars)")
            return False
        
        # Skip template or configuration files
        ignore_patterns = [
            '.obsidian', 
            'template', 
            'Template',
            '.trash',
            'Trash'
        ]
        
        file_str = str(file_path).lower()
        if any(pattern.lower() in file_str for pattern in ignore_patterns):
            if self.config.verbose:
                print(f"  ⏭️ Skipped: System or template file")
            return False
        
        # Extract meaningful content (not just code blocks or special characters)
        # Count meaningful text content
        text_content = re.sub(r'LATEX_EXPRESSION: .*|LATEX_BLOCK: .*|CODE_BLOCK: .*|CODE: .*', '', content)
        text_content = re.sub(r'[^\w\s.,:;?!()]', '', text_content)
        text_content = re.sub(r'\s+', ' ', text_content).strip()
        
        # If after removing special content, remaining text is too short, skip
        if len(text_content) < 100:
            if self.config.verbose:
                print(f"  ⏭️ Skipped: Insufficient meaningful content ({len(text_content)} chars)")
            return False
        
        # Process the file
        return True