---
title: documentation-index
type: note
permalink: docs/00-overview/documentation-index
tags:
- '[''documentation-index'''
- '''overview'
- navigation'
- '''obsidian-compatible'']'
---

# MCP RAG Server Documentation

## Welcome to MCP RAG Server Documentation

This is the comprehensive documentation for the MCP RAG Server project. The documentation is organized to help you quickly find the information you need, whether you're setting up the system, developing new features, or troubleshooting issues.

## Quick Navigation

### 🚀 Getting Started

- **[[../02-installation/installation-guide|Installation and Setup Guide]]** - Complete setup instructions
- **[[../01-architecture/system-architecture|System Architecture]]** - Project overview and architecture

### 📚 Core Documentation

- **[[../03-api/api-reference|API Reference]]** - Complete API documentation
- **[[../04-development/development-phases|Development Phases]]** - Project development status and roadmap
- **[[../04-development/project-refactoring|Project Refactoring History]]** - Recent project structure improvements

### 🔧 Operations

- **[[../05-troubleshooting/troubleshooting-guide|Troubleshooting Guide]]** - Common issues and solutions

## Documentation Structure

### Overview and Architecture

- **[[../01-architecture/system-architecture|System Architecture]]** - Complete project overview with architecture details, technology stack, and use cases

### Setup and Installation

- **[[../02-installation/installation-guide|Installation and Setup Guide]]** - Step-by-step installation instructions, environment configuration, Docker setup, and verification procedures

### API and Development

- **[[../03-api/api-reference|API Reference]]** - Complete MCP tools and resources reference with examples and error handling
- **[[../04-development/development-phases|Development Phases]]** - Current development status, phase overview, and future roadmap

### Operations and Maintenance

- **[[../05-troubleshooting/troubleshooting-guide|Troubleshooting Guide]]** - Common issues, solutions, and recovery procedures
- **[[../04-development/project-refactoring|Project Refactoring History]]** - Recent project structure improvements and migration notes

## Project Status

### Current Phase: Phase 4 - Memory Integration (25% Complete)

- ✅ Basic mem0 service integration
- ✅ Memory storage infrastructure
- ✅ Basic memory CRUD operations
- 🔄 Memory-aware RAG queries (In Progress)
- ⏳ User session management (Pending)
- ⏳ Advanced memory context retrieval (Pending)

### Completed Phases

- ✅ Phase 1: Foundations
- ✅ Phase 2: RAG Core
- ✅ Phase 3: MCP Integration

## Quick Start

1. **Installation**: Follow the [[../02-installation/installation-guide|Installation and Setup Guide]]
2. **Configuration**: Set up environment variables and services
3. **Verification**: Run health checks and basic tests
4. **Usage**: Use the [[../03-api/api-reference|API Reference]] for development

## Technology Stack

- **Python 3.9+** - Main programming language
- **MCP (Model Context Protocol)** - Standardized AI application interface
- **FastMCP** - High-performance MCP server implementation
- **Google Gemini API** - Text generation and embedding creation
- **Qdrant** - Vector database for similarity search
- **Mem0** - Memory layer for conversation context
- **Pydantic** - Data validation and settings management

## Key Features

- **Vector Database Integration**: Efficient similarity search with Qdrant
- **Memory Management**: Personalized conversation context with Mem0
- **AI Generation**: Embeddings and text generation with Gemini API
- **MCP Protocol**: Standardized interface for LLM applications
- **Multi-user Support**: User-specific document storage and memory
- **Real-time Search**: Semantic search across documents

## Support and Contributing

### Getting Help

- Check the [[../05-troubleshooting/troubleshooting-guide|Troubleshooting Guide]] for common issues
- Review the [[../02-installation/installation-guide|Installation and Setup Guide]] for setup problems
- Examine logs and error messages for specific issues

### Development

- Follow the [[../04-development/development-phases|Development Phases]] for current priorities
- Use the [[../03-api/api-reference|API Reference]] for development
- Check the [[../04-development/project-refactoring|Project Refactoring History]] for recent changes

## Documentation Updates

This documentation is maintained using Basic Memory and is updated regularly to reflect the current state of the project. All documentation follows Obsidian-style formatting for optimal readability and cross-referencing.

---

*Last updated: July 2024*
*Project: MCP RAG Server*
*Version: Phase 4 (25% Complete)*