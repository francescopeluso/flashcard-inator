# 🧠 Flashcard-inator [![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![Made for Anki](https://img.shields.io/badge/Made%20with%20%E2%9D%A4%EF%B8%8F%20for-Anki-green.svg)](https://apps.ankiweb.net/) [![Version](https://img.shields.io/badge/Version-1.0-orange.svg)](https://github.com/francescopeluso/flashcard-inator)

> 🚀 **Automatically transform your Obsidian notes into Anki flashcards using local language models!**

A cool Python script that automatically generates Anki flashcards from your Obsidian Markdown notes, using local language models (Ollama or LM Studio) without using and being rate limited by online third party services.

## ✨ Key Features

- 🤖 **Multi-provider LLM Support**: Works with Ollama and LM Studio
- 🌍 **Language Detection**: Automatically detects content language and generates flashcards in the same language (Italian by default)
- 🧹 **Intelligent Processing**: Cleans Obsidian-specific syntax and metadata
- 📤 **Anki-ready Export**: Generates CSV files directly importable into Anki
- ⚙️ **Configurable Processing**: Control which files to process
- 🔍 **Detailed Logging**: Optional detailed output for debugging
- 📊 **Smart Chunking**: Automatically handles large files by dividing them into manageable pieces
- ✨ **Unlimited Flashcards**: Generates as many flashcards as possible from your content

## 📋 Prerequisites

- Python 3.8 or higher
- Obsidian with a vault containing Markdown notes
- Access to Ollama or LM Studio for local inference

## 🔧 Installation

1. Clone or download the project files:
   ```bash
   git clone https://github.com/francescopeluso/flashcard-inator.git
   cd flashcard-inator
   ```

2. Create and activate a Python virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 🛠️ Configuration

### For Ollama (Default)
1. Install and start Ollama:
   ```bash
   ollama serve
   ```
2. Download a model (e.g. Gemma 3):
   ```bash
   ollama pull gemma3
   ```

### For LM Studio
1. Install and start LM Studio
2. Load a model in the application
3. Enable the local server (usually on `http://localhost:1234`)

## 📚 Usage

### Basic Usage (with default settings)
```bash
python main.py "/path/to/your/obsidian/vault"
```

### Advanced Usage
```bash
python main.py "/path/to/vault" \
  --provider lmstudio \
  --model "your-model-name" \
  --output "my_flashcards.csv" \
  --max-files 20 \
  --verbose
```

### Command Line Options

| Option | Short Format | Description | Default |
|---------|---------------|-------------|---------|
| `vault_path` | - | Path to your Obsidian vault (required) | - |
| `--output` | `-o` | Name of the output CSV file | `flashcards_anki.csv` |
| `--provider` | `-p` | LLM provider ('ollama' or 'lmstudio') | `ollama` |
| `--model` | `-m` | Model name to use | `gemma3` (Ollama) or `local-model` (LM Studio) |
| `--url` | `-u` | Custom base URL for the LLM server | `http://localhost:11434` (Ollama) or `http://localhost:1234` (LM Studio) |
| `--max-files` | - | Limit the number of files to process | All files |
| `--verbose` | `-v` | Enable detailed output | `false` |

Please note that the script, starting from the given path, will recursively check for any Obsidian Markdown files stored in subdirectories.

### Usage Examples

**Processing with Ollama using Gemma 3:**
```bash
python main.py "/Users/me/Documents/MyVault" --model gemma3
```

**Processing with LM Studio:**
```bash
python main.py "/Users/me/Documents/MyVault" --provider lmstudio --model "local-model"
```

**Testing with a limited number of files:**
```bash
python main.py "/Users/me/Documents/MyVault" --max-files 5 --verbose
```

## 📲 Importing into Anki

1. Open Anki
2. Go to **File > Import**
3. Select the generated CSV file
4. Set the field separator to **semicolon (;)**
5. Map the fields: Front → Front, Back → Back, Tags → Tags
6. Click Import


## ⚙️ Automatic Configuration

The tool configures itself automatically based on the chosen provider:

- **Ollama**: Default URL `http://localhost:11434`, model `gemma3`
- **LM Studio**: Default URL `http://localhost:1234`, model `local-model`

You can override these default values using command line arguments.

## 🔍 Troubleshooting

### Common Issues

1. **Connection refused**: Make sure your LLM server is running
2. **No flashcards generated**: Verify your notes have enough content (minimum 100 characters)
3. **Import issues in Anki**: Verify that the field separator is set to semicolon (;)
4. **Long files not processed**: Very long files are now automatically divided into smaller pieces
5. **Too many flashcards**: The tool now generates as many flashcards as possible from your content - you can manually filter them in Anki if needed

### Verbose Mode

Use the `--verbose` flag to get detailed information about:
- File processing status
- Communication with the LLM
- Error details
- Generation statistics
- Chunking of long files

## 📈 Performance

Performance depends on the LLM model used and the size of the input files. Generally:

- Small files (<2000 characters): Fast processing
- Medium files (2000-6000 characters): Normal processing
- Large files (>6000 characters): Automatic chunking for efficient processing

The number of flashcards generated depends entirely on the content of your notes - the tool will extract as many high-quality flashcards as possible from each file, with no artificial limits.

Note that a faster computer will significantly improve flashcard generation speed, especially for larger files.

## 📄 License

This project is distributed under the MIT license. You are free to use, modify, and distribute it according to the terms of the license.

## 🤝 Contributions

Contributions are welcome! Feel free to:
1. Fork the repository
2. Create a branch for your feature
3. Submit a pull request

## 📧 Contact

Francesco Peluso - [@francescopeluso](https://github.com/francescopeluso) ([website](https://francescopeluso.xyz/))