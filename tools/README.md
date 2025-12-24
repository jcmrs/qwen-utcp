# UTCP Knowledge Base Toolbelt

This toolbelt contains basic tools for extracting, processing, and optimizing knowledge from UTCP repositories. These tools are designed to work with minimal dependencies and provide functional implementations that can be extended later.

## Tools Included

### 1. basic_utcp_extractor.py
Extracts raw content from UTCP repositories without complex NLP dependencies.

**Features:**
- Scans repositories for relevant files
- Extracts basic content information
- Identifies titles, summaries, and key terms
- Works with standard file types (.py, .ts, .js, .go, .rs, .ex, .md, .json, .yaml, etc.)

**Usage:**
```bash
python basic_utcp_extractor.py --repo python-utcp --repo typescript-utcp
```

### 2. basic_utcp_processor.py
Processes raw extractions into structured knowledge.

**Features:**
- Converts raw content into concepts and relationships
- Creates summaries of extracted knowledge
- Identifies potential principles and patterns
- No external dependencies beyond Python standard library

**Usage:**
```bash
python basic_utcp_processor.py
```

### 3. basic_utcp_ai_optimizer.py
Optimizes knowledge for basic AI consumption.

**Features:**
- Creates simple search indexes
- Generates basic "embeddings" using hash functions
- Creates AI-optimized summaries
- No external AI dependencies

**Usage:**
```bash
python basic_utcp_ai_optimizer.py
```

### 4. basic_utcp_system.py
Main orchestration system for running the full pipeline.

**Features:**
- Runs the complete extraction, processing, and optimization pipeline
- Supports selective repository processing
- Generates reports about the knowledge base
- Simple command-line interface

**Usage:**
```bash
python basic_utcp_system.py full
python basic_utcp_system.py extract --repo python-utcp
python basic_utcp_system.py report
```

## Setup

1. Ensure you have Python 3.8+ installed
2. Make sure the UPSTREAM directory contains the UTCP repositories
3. The .utcp-kb directory will be created automatically to store the knowledge base

## Dependencies

These basic tools only require Python standard library. For enhanced functionality, see requirements.txt.

## Extending the Tools

These basic tools provide a foundation that can be extended with:
- More sophisticated NLP processing
- Advanced embedding techniques
- Better relationship extraction
- Enhanced search capabilities
- Integration with UTCP protocols

## Output Structure

The tools create the following knowledge base structure:
```
.utcp-kb/
├── raw-extractions/          # Raw extracted content
├── processed-knowledge/      # Structured concepts and relationships
│   ├── all_concepts.json
│   ├── all_relationships.json
│   ├── concepts_summary.json
│   └── relationships_summary.json
├── ai-optimized/             # AI-ready knowledge
│   ├── embeddings/
│   ├── indexes/
│   └── summaries/
└── wisdom/                   # Extracted principles and patterns
    ├── principles/
    └── patterns/
```