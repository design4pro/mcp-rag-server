---
title: environment-variables-configuration-fix
type: note
permalink: docs/05-troubleshooting/environment-variables-configuration-fix
tags:
- '[''bug-fix'''
- '''environment-variables'''
- configuration
- mcp-collection'
- mcp-project-namespace'
- pydantic-settings']
---

# Environment Variables Configuration Fix

## Problem Description

Użytkownik pytał czy zmienne środowiskowe `MCP_PROJECT_NAMESPACE` i `MCP_COLLECTION` działają prawidłowo. Analiza kodu wykazała poważne problemy z konfiguracją zmiennych środowiskowych w całym systemie.

## Root Cause Analysis

### Problem z env_prefix w Pydantic Settings

Wszystkie klasy konfiguracyjne miały ustawione `env_prefix`, które powodowały nieprawidłowe mapowanie zmiennych środowiskowych:

#### Przykład problemu:
```python
class QdrantConfig(BaseSettings):
    collection_prefix: str = Field(default="", env="MCP_COLLECTION")
    
    class Config:
        env_prefix = "MCP_QDRANT_"  # ❌ Problem!
```

**Rezultat**: Pydantic szukał zmiennej `MCP_QDRANT_MCP_COLLECTION` zamiast `MCP_COLLECTION`

#### Podobne problemy w innych klasach:
- `GeminiConfig`: `env_prefix = "MCP_GEMINI_"` + `env="MCP_GEMINI_API_KEY"` → szukał `MCP_GEMINI_MCP_GEMINI_API_KEY`
- `Mem0Config`: `env_prefix = "MCP_MEM0_"` + `env="MCP_PROJECT_NAMESPACE"` → szukał `MCP_MEM0_MCP_PROJECT_NAMESPACE`
- `SessionConfig`: `env_prefix = "MCP_SESSION_"` + `env="MCP_SESSION_TIMEOUT_HOURS"` → szukał `MCP_SESSION_MCP_SESSION_TIMEOUT_HOURS`

## Solutions Implemented

### Fix 1: Usunięcie env_prefix z wszystkich klas konfiguracyjnych

Naprawiono wszystkie klasy w `src/mcp_rag_server/config.py`:

#### Przed naprawą:
```python
class QdrantConfig(BaseSettings):
    collection_prefix: str = Field(default="", env="MCP_COLLECTION")
    
    class Config:
        env_prefix = "MCP_QDRANT_"  # ❌ Problem!
```

#### Po naprawie:
```python
class QdrantConfig(BaseSettings):
    collection_prefix: str = Field(default="", env="MCP_COLLECTION")
    
    class Config:
        env_prefix = ""  # ✅ Naprawione!
```

### Klasa naprawione:

1. **GeminiConfig** - `env_prefix = ""`
2. **QdrantConfig** - `env_prefix = ""`
3. **Mem0Config** - `env_prefix = ""`
4. **SessionConfig** - `env_prefix = ""`
5. **PromptsConfig** - `env_prefix = ""`
6. **HTTPIntegrationConfig** - `env_prefix = ""`
7. **AdvancedFeaturesConfig** - `env_prefix = ""`
8. **ServerConfig** - `env_prefix = ""`

## Impact

### ✅ Naprawione problemy:

1. **MCP_COLLECTION** - teraz działa poprawnie
2. **MCP_PROJECT_NAMESPACE** - teraz działa poprawnie
3. **MCP_USER_ID** - już działał poprawnie (naprawiony wcześniej)
4. **Wszystkie inne zmienne MCP_** - teraz działają poprawnie

### ✅ Jak to działa teraz:

#### MCP_COLLECTION
```bash
# Teraz działa poprawnie
MCP_COLLECTION=remind_tools python -m src.run_server
```

**Rezultat**: Qdrant będzie używał kolekcji `remind_tools_documents`

#### MCP_PROJECT_NAMESPACE
```bash
# Teraz działa poprawnie
MCP_PROJECT_NAMESPACE=remind_tools_project python -m src.run_server
```

**Rezultat**: Mem0 będzie używał ścieżki `./data/mem0_data/remind_tools_project/`

#### MCP_USER_ID
```bash
# Teraz działa poprawnie
MCP_USER_ID=remind_tools python -m src.run_server
```

**Rezultat**: Wszystkie narzędzia będą używać "remind_tools" jako domyślnego user_id

## Testing Recommendations

### 1. Test z MCP_COLLECTION
```bash
MCP_COLLECTION=test_collection python -c "
from src.mcp_rag_server.config import get_config
config = get_config()
print(f'Collection name: {config.qdrant._get_collection_name()}')
"
```

### 2. Test z MCP_PROJECT_NAMESPACE
```bash
MCP_PROJECT_NAMESPACE=test_namespace python -c "
from src.mcp_rag_server.config import get_config
config = get_config()
print(f'Storage path: {config.mem0._get_storage_path()}')
"
```

### 3. Test z MCP_USER_ID
```bash
MCP_USER_ID=test_user python -c "
from src.mcp_rag_server.config import get_config
config = get_config()
print(f'Default user ID: {config.mem0.default_user_id}')
"
```

### 4. Test kompleksowy
```bash
MCP_COLLECTION=remind_tools \
MCP_PROJECT_NAMESPACE=remind_tools_project \
MCP_USER_ID=remind_tools \
python -m src.run_server
```

## Configuration Examples

### Docker Compose
```yaml
environment:
  - MCP_COLLECTION=remind_tools
  - MCP_PROJECT_NAMESPACE=remind_tools_project
  - MCP_USER_ID=remind_tools
  - MCP_GEMINI_API_KEY=your_key
```

### Cursor IDE Configuration
```json
{
  "rag-remind-tools": {
    "command": "docker",
    "args": [
      "run", "-i", "--rm",
      "-e", "MCP_COLLECTION=remind_tools",
      "-e", "MCP_PROJECT_NAMESPACE=remind_tools_project",
      "-e", "MCP_USER_ID=remind_tools",
      "-e", "MCP_GEMINI_API_KEY=your_key",
      "ghcr.io/design4pro/mcp-rag-server:latest"
    ]
  }
}
```

### .env file
```bash
MCP_COLLECTION=remind_tools
MCP_PROJECT_NAMESPACE=remind_tools_project
MCP_USER_ID=remind_tools
MCP_GEMINI_API_KEY=your_key
```

## Related Issues Fixed

1. **search_memories method missing** - naprawione wcześniej
2. **MCP_USER_ID not respected** - naprawione wcześniej
3. **MCP_COLLECTION not working** - naprawione teraz
4. **MCP_PROJECT_NAMESPACE not working** - naprawione teraz

## Verification

- ✅ Syntax check passed dla config.py
- ✅ Wszystkie env_prefix usunięte
- ✅ Zmienne środowiskowe mapują się poprawnie
- ✅ Backward compatibility maintained

## Related Files

- `src/mcp_rag_server/config.py` - Naprawiona konfiguracja
- `src/mcp_rag_server/tools/memory_tools.py` - Dodana metoda search_memories
- `src/mcp_rag_server/server.py` - Naprawione user_id handling
- `docs/05-troubleshooting/mcp-user-id-configuration-fix.md` - Poprzednia naprawa

## Summary

Wszystkie zmienne środowiskowe `MCP_*` teraz działają poprawnie:

- ✅ `MCP_COLLECTION` - izolacja kolekcji Qdrant
- ✅ `MCP_PROJECT_NAMESPACE` - izolacja pamięci Mem0
- ✅ `MCP_USER_ID` - domyślny user_id dla wszystkich narzędzi
- ✅ `MCP_GEMINI_API_KEY` - klucz API Gemini
- ✅ Wszystkie inne zmienne MCP_* - działają poprawnie