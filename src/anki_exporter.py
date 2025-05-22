"""
File:         anki_exporter.py
Description:  Exports flashcards to Anki-compatible CSV format
Author:       Francesco Peluso (@francescopeluso)
Date:         2025-05-22
Version:      1.0
"""

import csv
from typing import List, Dict
from pathlib import Path

from .config import Config


class AnkiExporter:
    """Handles exporting flashcards to Anki-compatible formats"""
    
    def __init__(self, config: Config):
        """
        Initialize Anki exporter
        
        Args:
            config: Application configuration
        """
        self.config = config
    
    def export_to_csv(self, flashcards: List[Dict], output_file: str) -> None:
        """
        Export flashcards to CSV format compatible with Anki
        
        Args:
            flashcards: List of flashcard dictionaries
            output_file: Output file path
        """
        if not flashcards:
            raise ValueError("No flashcards to export")
        
        # Create output directory if needed
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write CSV with semicolon delimiter (Anki standard)
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            
            # Write each flashcard as CSV row
            for card in flashcards:
                question = self._clean_text_for_anki(card.get('question', ''))
                answer = self._clean_text_for_anki(card.get('answer', ''))
                tags = card.get('tags', '')
                
                if question and answer:  # Only write valid cards
                    writer.writerow([question, answer, tags])
        
        if self.config.verbose:
            print(f"📄 Exported {len(flashcards)} flashcards to {output_path}")
    
    def _clean_text_for_anki(self, text: str) -> str:
        """
        Clean text for Anki compatibility
        
        Args:
            text: Text to clean
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Convert newlines to HTML line breaks
        text = text.replace('\n', '<br>')
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        # Escape HTML characters but preserve line breaks
        text = text.replace('<', '&lt;').replace('>', '&gt;')
        text = text.replace('<br>', '<br>')  # But keep line breaks
        
        return text.strip()