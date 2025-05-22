"""
File:         main.py
Description:  Main entry point for Obsidian to Anki flashcards generation tool
Author:       Francesco Peluso (@francescopeluso)
Date:         2025-05-22
Version:      1.0
"""

import argparse
import sys
from pathlib import Path

from src.obsidian_processor import ObsidianProcessor
from src.llm_client import LLMClient
from src.anki_exporter import AnkiExporter
from src.config import Config


def parse_arguments():
    """Parse command line arguments"""
    # Create argument parser with description
    parser = argparse.ArgumentParser(
        description="Generate Anki flashcards from Obsidian Markdown files using local LLM"
    )
    # Add required vault path argument
    parser.add_argument(
        "vault_path", 
        help="Path to Obsidian vault directory"
    )
    # Add optional output file argument
    parser.add_argument(
        "-o", "--output", 
        default="flashcards_anki.csv",
        help="Output CSV file path (default: flashcards_anki.csv)"
    )
    # Add LLM provider selection
    parser.add_argument(
        "-p", "--provider",
        choices=["ollama", "lmstudio"],
        default="ollama",
        help="LLM provider (default: ollama)"
    )
    # Add model name override
    parser.add_argument(
        "-m", "--model",
        help="Model name (default: llama2 for Ollama, local-model for LM Studio)"
    )
    # Add custom server URL
    parser.add_argument(
        "-u", "--url",
        help="Custom base URL for LLM server"
    )
    # Add file processing limit for testing
    parser.add_argument(
        "--max-files",
        type=int,
        help="Maximum number of files to process (for testing)"
    )
    # Add verbose output flag
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    return parser.parse_args()


def main():
    """Main application entry point"""
    # Parse command line arguments
    args = parse_arguments()
    
    try:
        # Initialize configuration with user arguments
        config = Config(
            provider=args.provider,
            base_url=args.url,
            model=args.model,
            verbose=args.verbose
        )
        
        if config.verbose:
            print(f"🚀 Starting flashcard generation with provider: {config.provider}")
        
        # Initialize processing components
        llm_client = LLMClient(config)
        obsidian_processor = ObsidianProcessor(args.vault_path, config)
        anki_exporter = AnkiExporter(config)
        
        # Discover Markdown files in vault
        md_files = obsidian_processor.get_markdown_files()
        print(f"📁 Found {len(md_files)} Markdown files")
        
        # Limit files for testing if specified
        if args.max_files:
            md_files = md_files[:args.max_files]
            print(f"🔍 Processing only first {args.max_files} files")
        
        all_flashcards = []
        processed_count = 0
        
        # Process each Markdown file
        for i, file_path in enumerate(md_files, 1):
            print(f"[{i}/{len(md_files)}] Processing: {file_path.name}")
            
            # Read and clean file content
            content = obsidian_processor.read_file_content(file_path)
            
            # Check if file should be processed
            if not obsidian_processor.should_process_file(file_path, content):
                if config.verbose:
                    print(f"  ⏭️  Skipped (insufficient content)")
                continue
            
            # Generate flashcards using LLM
            flashcards = llm_client.generate_flashcards(content, file_path.name)
            
            if flashcards:
                # Add tags with filename for organization
                for card in flashcards:
                    card['tags'] = f"obsidian {file_path.stem.replace(' ', '_')}"
                
                all_flashcards.extend(flashcards)
                processed_count += 1
                print(f"  ✅ Generated {len(flashcards)} flashcards")
            else:
                if config.verbose:
                    print(f"  ⚠️  No flashcards generated")
        
        # Export flashcards to Anki CSV format
        if all_flashcards:
            anki_exporter.export_to_csv(all_flashcards, args.output)
            print(f"\n🎉 Successfully exported {len(all_flashcards)} flashcards to {args.output}")
            print(f"📚 Import the file in Anki using 'File > Import'")
            print(f"🔧 Make sure to set field separator to ';' in Anki")
            print(f"📊 Processed {processed_count} out of {len(md_files)} files")
        else:
            print("\n❌ No flashcards were generated")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())