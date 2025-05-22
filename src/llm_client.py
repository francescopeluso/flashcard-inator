"""
File:         llm_client.py
Description:  Client for communicating with local LLM providers (Ollama, LM Studio)
Author:       Francesco Peluso (@francescopeluso)
Date:         2025-05-22
Version:      1.0
"""

import json
import re
import requests
from typing import List, Dict

from .config import Config


class LLMClient:
    """Client for communicating with local LLM services"""
    
    def __init__(self, config: Config):
        """
        Initialize LLM client
        
        Args:
            config: Application configuration
        """
        self.config = config
        # Set up HTTP session with timeout for API calls
        self.session = requests.Session()
        self.session.timeout = 120  # 2 minutes timeout
        # Add retry configuration
        self.max_retries = 3
        self.retry_delay = 2  # seconds
    
    def generate_flashcards(self, content: str, filename: str, language: str = 'it') -> List[Dict[str, str]]:
        """
        Generate flashcards from content using LLM
        
        Args:
            content: Content to process
            filename: Source filename
            language: Content language code
            
        Returns:
            List of flashcard dictionaries
        """
        # Check content length and chunk if necessary
        content_length = len(content)
        
        # If content is very large, chunk it
        if content_length > 6000:
            if self.config.verbose:
                print(f"  📏 Content is large ({content_length} chars), splitting into chunks")
            
            # Divide content into manageable chunks
            chunks = self._chunk_content(content)
            all_flashcards = []
            
            # Process each chunk separately
            for i, chunk in enumerate(chunks, 1):
                if self.config.verbose:
                    print(f"  📄 Processing chunk {i}/{len(chunks)} ({len(chunk)} chars)")
                
                # Build prompt with chunk content
                chunk_filename = f"{filename} (part {i}/{len(chunks)})"
                chunk_flashcards = self._generate_flashcards_from_chunk(chunk, chunk_filename, language)
                
                # Add flashcards from this chunk
                if chunk_flashcards:
                    all_flashcards.extend(chunk_flashcards)
            
            if all_flashcards:
                return all_flashcards
            else:
                return []
        else:
            # Content is small enough, process normally
            return self._generate_flashcards_from_chunk(content, filename, language)
    
    def _generate_flashcards_from_chunk(self, content: str, filename: str, language: str) -> List[Dict[str, str]]:
        """
        Generate flashcards from a single content chunk
        
        Args:
            content: Content chunk to process
            filename: Source filename
            language: Content language code
            
        Returns:
            List of flashcard dictionaries
        """
        # Build prompt with content and language-specific instructions
        prompt = self._create_prompt(content, filename, language)
        
        # Track retry attempts
        attempt = 0
        max_attempts = self.max_retries
        
        while attempt < max_attempts:
            try:
                # Call appropriate LLM provider based on configuration
                if self.config.provider == "ollama":
                    response = self._call_ollama(prompt)
                else:
                    response = self._call_lmstudio(prompt)
                
                # Parse response to extract valid flashcards
                flashcards = self._extract_flashcards_from_response(response)
                
                # If we got valid flashcards, return them
                if flashcards and len(flashcards) > 0:
                    return flashcards
                
                # No flashcards generated, increment attempt counter
                attempt += 1
                
                if self.config.verbose:
                    print(f"  ⚠️ Attempt {attempt}/{max_attempts}: No valid flashcards generated, retrying...")
                
                # Wait before retry with exponential backoff
                if attempt < max_attempts:
                    import time
                    time.sleep(self.retry_delay * (2 ** (attempt - 1)))  # Exponential backoff
                    
                    # Adjust prompt slightly to encourage different response
                    if attempt == 1:
                        prompt += "\n\nPLEASE ENSURE TO GENERATE VALID FLASHCARDS IN THE SPECIFIED JSON FORMAT."
                    
            except Exception as e:
                if self.config.verbose:
                    print(f"  ❌ Error generating flashcards for {filename} (attempt {attempt+1}/{max_attempts}): {e}")
                    
                # Increment attempt and retry
                attempt += 1
                
                # Wait before retry with exponential backoff
                if attempt < max_attempts:
                    import time
                    time.sleep(self.retry_delay * (2 ** (attempt - 1)))
        
        # If we've exhausted all attempts, log and return empty list
        if self.config.verbose:
            print(f"  ❌ Failed to generate flashcards for {filename} after {max_attempts} attempts")
        
        return []
    
    def _create_prompt(self, content: str, filename: str, language: str) -> str:
        """Create the prompt for flashcard generation"""
        
        # Set language-specific instructions for flashcard generation
        if language == 'it':
            lang_instruction = """
Crea delle flashcards in ITALIANO per lo studio.
Le domande e risposte devono essere in italiano.
"""
        else:
            lang_instruction = f"""
Create flashcards in the same language as the content ({language.upper()}).
Questions and answers should be in {language}.
"""
        
        # Build complete prompt with rules and formatting instructions
        prompt = f"""
Analyze the following content from file "{filename}" and create study flashcards.
{lang_instruction}

RULES:
1. Create as many high-quality flashcards as you can extract from the content
2. Questions must be clear and specific, but can also by tricky (to test real knowledge)
3. Answers must not be too concise, but they have to explain the concept in detail
4. Avoid questions that are too obvious or too vague
5. Focus on key concepts, definitions, important examples
6. Use the same language as the source content
7. Of course, fix any grammar or spelling mistakes in the content
8. If you see LaTeX expressions or code blocks, incorporate their concepts but without using LaTeX syntax
9. Always respond with flashcards even if the content contains complex formulas or code

OUTPUT FORMAT:
You MUST return ONLY a valid JSON with this format. No markdown formatting, no backticks, just the raw JSON:
{{
  "flashcards": [
    {{"question": "Question 1?", "answer": "Answer 1"}},
    {{"question": "Question 2?", "answer": "Answer 2"}}
  ]
}}

IMPORTANT: Your entire response must be valid JSON that can be parsed with JSON.parse() or json.loads()

CONTENT TO ANALYZE:
{content}
"""
        return prompt
    
    def _call_ollama(self, prompt: str) -> str:
        """Call Ollama API"""
        # Prepare request payload for Ollama API
        data = {
            "model": self.config.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9
            }
        }
        
        # Send POST request and extract response
        response = self.session.post(self.config.endpoint, json=data)
        response.raise_for_status()
        
        return response.json()["response"]
    
    def _call_lmstudio(self, prompt: str) -> str:
        """Call LM Studio API"""
        # Prepare request payload for LM Studio API (OpenAI-compatible format)
        data = {
            "model": self.config.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1500
        }
        
        # Send POST request and extract response content
        response = self.session.post(self.config.endpoint, json=data)
        response.raise_for_status()
        
        return response.json()["choices"][0]["message"]["content"]
    
    def _extract_flashcards_from_response(self, response: str) -> List[Dict[str, str]]:
        """Extract flashcards from LLM response"""
        try:
            # Try to extract JSON from response using regex
            # This pattern finds any JSON-like structure in the response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                data = json.loads(json_str)
                flashcards = data.get("flashcards", [])
                
                # Filter out invalid flashcards (must have both question and answer)
                valid_flashcards = []
                for card in flashcards:
                    if isinstance(card, dict) and "question" in card and "answer" in card:
                        if card["question"].strip() and card["answer"].strip():
                            valid_flashcards.append(card)
                
                return valid_flashcards
            else:
                # If JSON extraction fails, use Q&A format parser as fallback
                return self._parse_qa_format(response)
        except Exception as e:
            if self.config.verbose:
                print(f"Error parsing response: {e}")
                # Print a sample of the response for debugging
                print(f"Response sample: {response[:200]}...")
            # On any parsing error, fallback to Q&A format parser
            return self._parse_qa_format(response)
    
    def _parse_qa_format(self, response: str) -> List[Dict[str, str]]:
        """Parse question-answer format as fallback"""
        flashcards = []
        lines = response.split('\n')
        current_q = None
        current_a = []
        
        for line in lines:
            line = line.strip()
            
            # Detect question lines by common patterns
            if any(line.startswith(pattern) for pattern in ['Q:', 'Domanda:', '**Q:', 'Question:']):
                # Save previous Q&A pair if exists
                if current_q and current_a:
                    flashcards.append({
                        "question": current_q,
                        "answer": ' '.join(current_a).strip()
                    })
                
                # Extract question text by removing prefix patterns
                current_q = re.sub(r'^[Q\*:Domanda\s]+', '', line).strip()
                current_a = []
            
            # Detect answer lines by common patterns
            elif any(line.startswith(pattern) for pattern in ['A:', 'Risposta:', '**A:', 'Answer:']):
                # Extract answer text by removing prefix patterns
                answer = re.sub(r'^[A\*:Risposta\s]+', '', line).strip()
                current_a = [answer] if answer else []
            
            # Continue collecting answer text from subsequent lines
            elif current_q and line and not line.startswith(('-', '*', '+')):
                current_a.append(line)
        
        # Don't forget to add the last Q&A pair
        if current_q and current_a:
            flashcards.append({
                "question": current_q,
                "answer": ' '.join(current_a).strip()
            })
        
        return flashcards
    
    def _chunk_content(self, content: str, max_chars: int = 6000) -> List[str]:
        """
        Divide content into smaller chunks for better LLM processing.

        Added this because I noticed that for some longer fiiles, the LLM would not return any flashcards
        (even tho no error was raised and no messages were printed on stdout)
        
        Args:
            content: The content to chunk
            max_chars: Maximum characters per chunk
            
        Returns:
            List of content chunks
        """
        # If content is small enough, return as is
        if len(content) <= max_chars:
            return [content]
        
        # Split by paragraphs
        paragraphs = re.split(r'\n\s*\n', content)
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            # If adding this paragraph would make the chunk too large, 
            # save current chunk and start a new one
            if len(current_chunk) + len(para) > max_chars and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = para
            else:
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para
        
        # Don't forget the last chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
            
        # If we ended up with no chunks (unlikely), just force split the content
        if not chunks:
            chunks = [content[i:i+max_chars] for i in range(0, len(content), max_chars)]
            
        return chunks
