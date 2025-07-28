---
title: environment-variables-mapping-fix
type: note
permalink: docs/05-troubleshooting/environment-variables-mapping-fix
tags:
- '[''bug-fix'''
- '''environment-variables'''
- pydantic-settings'
- breaking-change'
- '''docker-configuration'']'
---

# Environment Variables Mapping Fix

## Problem Description

Po naprawie konfiguracji Pydantic Settings, zmienne środowiskowe mają inne nazwy niż wcześniej dokumentowane. To powoduje problemy z konfiguracją Docker i innych środowisk.

## Root Cause Analysis

### Problem z env_prefix i env parametrem

Wcześniej próbowałem naprawić problem z podwójnymi prefiksami ustawiając `env_prefix = ""`, ale to nie działało poprawnie z Pydantic Settings.

**Niepoprawne podejście:**
```python
class GeminiConfig(BaseSettings):
    api_key: str = Field(..., env="MCP_GEMINI_API_KEY")
    
    class Config:
        env_prefix = ""  # ❌ Nie działa!
```

**Poprawne podejście:**
```python
class GeminiConfig(BaseSettings):
    api_key: str = Field(...)  # Bez parametru env
    
    class Config:
        env_prefix = "MCP_GEMINI_"  # ✅ Działa!
```

## Solutions Implemented

### Fix: Przywrócenie env_prefix z odpowiednimi prefiksami

Naprawiono wszystkie klasy w `src/mcp_rag_server/config.py`:

#### Przed naprawą:
```python
class GeminiConfig(BaseSettings):
    api_key: str = Field(..., env="MCP_GEMINI_API_KEY")
    
    class Config:
        env_prefix = ""  # ❌ Problem!
```

#### Po naprawie:
```python
class GeminiConfig(BaseSettings):
    api_key: str = Field(...)  # Bez parametru env
    
    class Config:
        env_prefix = "MCP_GEMINI_"  # ✅ Naprawione!
```

### Mapowanie zmiennych środowiskowych

| Klasa | env_prefix | Zmienna w kodzie | Zmienna środowiskowa |
|-------|------------|------------------|---------------------|
| `GeminiConfig` | `MCP_GEMINI_` | `api_key` | `MCP_GEMINI_API_KEY` |
| `QdrantConfig` | `MCP_QDRANT_` | `collection_prefix` | `MCP_QDRANT_COLLECTION_PREFIX` |
| `Mem0Config` | `MCP_MEM0_` | `project_namespace` | `MCP_MEM0_PROJECT_NAMESPACE` |
| `Mem0Config` | `MCP_MEM0_` | `default_user_id` | `MCP_MEM0_DEFAULT_USER_ID` |
| `SessionConfig` | `MCP_SESSION_` | `timeout_hours` | `MCP_SESSION_TIMEOUT_HOURS` |
| `PromptsConfig` | `MCP_PROMPTS_` | `enabled` | `MCP_PROMPTS_ENABLED` |
| `HTTPIntegrationConfig` | `MCP_HTTP_` | `timeout_seconds` | `MCP_HTTP_TIMEOUT` |
| `AdvancedFeaturesConfig` | `MCP_ADVANCED_` | `default_batch_size` | `MCP_ADVANCED_DEFAULT_BATCH_SIZE` |
| `ServerConfig` | `MCP_` | `host` | `MCP_HOST` |

## Impact

### ✅ Naprawione problemy:

1. **Konfiguracja działa poprawnie** - wszystkie zmienne środowiskowe są mapowane poprawnie
2. **Brak podwójnych prefiksów** - każda klasa ma swój unikalny prefiks
3. **Spójność z Pydantic** - używamy standardowego podejścia Pydantic Settings

### ❌ Nowe problemy:

1. **Zmiana nazw zmiennych** - zmienne środowiskowe mają inne nazwy niż wcześniej dokumentowane
2. **Breaking change** - istniejące konfiguracje Docker i .env mogą nie działać

## Required Environment Variables

### Podstawowe zmienne (wymagane):

```bash
# Gemini API
MCP_GEMINI_API_KEY=your_gemini_api_key

# Qdrant Database
MCP_QDRANT_URL=http://localhost:6333
MCP_QDRANT_COLLECTION_PREFIX=your_project

# Mem0 Memory
MCP_MEM0_PROJECT_NAMESPACE=your_project
MCP_MEM0_DEFAULT_USER_ID=your_user_id
MCP_MEM0_STORAGE_PATH=/app/mem0_data

# Server
MCP_HOST=localhost
MCP_PORT=8000
MCP_LOG_LEVEL=INFO
```

### Przykład Docker Compose:

```yaml
environment:
  # Gemini API
  - MCP_GEMINI_API_KEY=your_gemini_api_key
  
  # Qdrant Database
  - MCP_QDRANT_URL=http://host.docker.internal:6333
  - MCP_QDRANT_COLLECTION_PREFIX=remindtools
  
  # Mem0 Memory
  - MCP_MEM0_PROJECT_NAMESPACE=remind_tools
  - MCP_MEM0_DEFAULT_USER_ID=remind_tools
  - MCP_MEM0_STORAGE_PATH=/app/mem0_data
  
  # Server
  - MCP_HOST=0.0.0.0
  - MCP_PORT=8000
  - MCP_LOG_LEVEL=INFO
```

### Przykład .env file:

```bash
# Gemini API
MCP_GEMINI_API_KEY=your_gemini_api_key

# Qdrant Database
MCP_QDRANT_URL=http://localhost:6333
MCP_QDRANT_COLLECTION_PREFIX=remindtools

# Mem0 Memory
MCP_MEM0_PROJECT_NAMESPACE=remind_tools
MCP_MEM0_DEFAULT_USER_ID=remind_tools
MCP_MEM0_STORAGE_PATH=./data/mem0_data

# Server
MCP_HOST=localhost
MCP_PORT=8000
MCP_LOG_LEVEL=INFO
```

## Migration Guide

### Z poprzednich nazw na nowe:

| Stara nazwa | Nowa nazwa |
|-------------|------------|
| `MCP_GEMINI_API_KEY` | `MCP_GEMINI_API_KEY` (bez zmian) |
| `MCP_COLLECTION` | `MCP_QDRANT_COLLECTION_PREFIX` |
| `MCP_PROJECT_NAMESPACE` | `MCP_MEM0_PROJECT_NAMESPACE` |
| `MCP_USER_ID` | `MCP_MEM0_DEFAULT_USER_ID` |
| `MCP_SERVER_HOST` | `MCP_HOST` |
| `MCP_SERVER_PORT` | `MCP_PORT` |
| `MCP_LOG_LEVEL` | `MCP_LOG_LEVEL` (bez zmian) |

### Przykład migracji Docker Compose:

```yaml
# Przed (nie działa):
environment:
  - MCP_COLLECTION=remindtools
  - MCP_PROJECT_NAMESPACE=remind_tools
  - MCP_USER_ID=remind_tools

# Po (działa):
environment:
  - MCP_QDRANT_COLLECTION_PREFIX=remindtools
  - MCP_MEM0_PROJECT_NAMESPACE=remind_tools
  - MCP_MEM0_DEFAULT_USER_ID=remind_tools
```

## Testing

### Test konfiguracji:

```bash
MCP_GEMINI_API_KEY=test_key \
MCP_QDRANT_COLLECTION_PREFIX=test_collection \
MCP_MEM0_PROJECT_NAMESPACE=test_namespace \
MCP_MEM0_DEFAULT_USER_ID=test_user \
python -c "
from src.mcp_rag_server.config import get_config
config = get_config()
print('✅ Config loaded successfully')
print(f'API Key: {config.gemini.api_key}')
print(f'Collection Prefix: {config.qdrant.collection_prefix}')
print(f'Project Namespace: {config.mem0.project_namespace}')
print(f'Default User ID: {config.mem0.default_user_id}')
"
```

## Related Issues

1. **Docker image outdated** - obraz `ghcr.io/design4pro/mcp-rag-server:latest` nie zawiera tych zmian
2. **Documentation outdated** - dokumentacja używa starych nazw zmiennych
3. **Breaking change** - istniejące konfiguracje mogą nie działać

## Next Steps

1. **Zbudować nowy obraz Docker** z naprawioną konfiguracją
2. **Zaktualizować dokumentację** z nowymi nazwami zmiennych
3. **Przetestować w środowisku produkcyjnym**
4. **Zaktualizować przykłady Docker Compose**

## Summary

Konfiguracja Pydantic Settings została naprawiona i działa poprawnie, ale wymaga zmiany nazw zmiennych środowiskowych. To jest breaking change, który wymaga aktualizacji dokumentacji i konfiguracji.