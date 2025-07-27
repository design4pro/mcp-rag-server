---
title: project-isolation-configuration
type: note
permalink: docs/02-installation/project-isolation-configuration
tags:
- '[]project-isolation'
- multi-tenant'
- configuration'
- '''docker'''
- '''environment-variables'']'
---

# Project Isolation Configuration in MCP RAG Server

## Overview

The MCP RAG Server now supports project isolation to prevent data mixing between different projects, clients, and technologies. This feature ensures that each project maintains its own separate memory and document storage.

## Why Project Isolation is Important

### Problems with Mixed Data
1. **Context Pollution**: Analysis may be based on irrelevant data from other projects
2. **False Associations**: System may connect concepts from different domains
3. **Reduced Precision**: Noise in data decreases response quality
4. **Privacy Issues**: Data from different clients gets mixed together
5. **Confusion in Analysis**: Sequential reasoning may use wrong context

### Benefits of Project Isolation
1. **Clean Context**: Each project has its own isolated data space
2. **Better Accuracy**: Analysis is based only on relevant project data
3. **Privacy Protection**: Client data remains separate
4. **Focused Reasoning**: Sequential analysis uses project-specific context
5. **Easier Management**: Clear separation of project resources

## Configuration Options

### 1. Qdrant Collection Prefix
**Environment Variable**: `QDRANT_COLLECTION_PREFIX`

**Purpose**: Creates separate collections for different projects
- **Format**: `{prefix}_{collection_name}`
- **Example**: `project_a_documents`, `client_b_documents`
- **Default**: Empty (uses default collection name)

**Usage**:
```bash
# For Project A
QDRANT_COLLECTION_PREFIX=project_a

# For Client B
QDRANT_COLLECTION_PREFIX=client_b

# For Technology X
QDRANT_COLLECTION_PREFIX=tech_x
```

### 2. Mem0 Project Namespace
**Environment Variable**: `MEM0_PROJECT_NAMESPACE`

**Purpose**: Separates memory storage by project
- **Format**: Creates subdirectories in memory storage
- **Example**: `./mem0_data/project_a/`, `./mem0_data/client_b/`
- **Default**: Empty (uses base storage path)

**Usage**:
```bash
# For Project A
MEM0_PROJECT_NAMESPACE=project_a

# For Client B
MEM0_PROJECT_NAMESPACE=client_b

# For Technology X
MEM0_PROJECT_NAMESPACE=tech_x
```

### 3. Default User ID
**Environment Variable**: `MEM0_DEFAULT_USER_ID`

**Purpose**: Sets the default user ID for the project
- **Format**: String identifier for the project
- **Example**: `project_a_user`, `client_b_team`
- **Default**: `default`

**Usage**:
```bash
# For Project A
MEM0_DEFAULT_USER_ID=project_a_user

# For Client B
MEM0_DEFAULT_USER_ID=client_b_team

# For Technology X
MEM0_DEFAULT_USER_ID=tech_x_dev
```

## Configuration Examples

### Example 1: Web Development Project
```bash
# .env file
GEMINI_API_KEY=your_api_key
QDRANT_COLLECTION_PREFIX=web_dev
MEM0_PROJECT_NAMESPACE=web_development
MEM0_DEFAULT_USER_ID=web_dev_team
```

**Result**:
- Qdrant collection: `web_dev_documents`
- Memory storage: `./mem0_data/web_development/`
- Default user: `web_dev_team`

### Example 2: Mobile App Project
```bash
# .env file
GEMINI_API_KEY=your_api_key
QDRANT_COLLECTION_PREFIX=mobile_app
MEM0_PROJECT_NAMESPACE=mobile_development
MEM0_DEFAULT_USER_ID=mobile_dev_team
```

**Result**:
- Qdrant collection: `mobile_app_documents`
- Memory storage: `./mem0_data/mobile_development/`
- Default user: `mobile_dev_team`

### Example 3: Client-Specific Configuration
```bash
# .env file
GEMINI_API_KEY=your_api_key
QDRANT_COLLECTION_PREFIX=client_acme
MEM0_PROJECT_NAMESPACE=acme_corp
MEM0_DEFAULT_USER_ID=acme_team
```

**Result**:
- Qdrant collection: `client_acme_documents`
- Memory storage: `./mem0_data/acme_corp/`
- Default user: `acme_team`

## Docker Configuration

### Docker Compose Setup
The Docker Compose configuration automatically supports project isolation:

```yaml
environment:
  - GEMINI_API_KEY=${GEMINI_API_KEY}
  - QDRANT_URL=http://qdrant:6333
  - QDRANT_COLLECTION_PREFIX=${QDRANT_COLLECTION_PREFIX:-}
  - MEM0_SELF_HOSTED=true
  - MEM0_LOCAL_STORAGE_PATH=/app/mem0_data
  - MEM0_PROJECT_NAMESPACE=${MEM0_PROJECT_NAMESPACE:-}
  - MEM0_DEFAULT_USER_ID=${MEM0_DEFAULT_USER_ID:-default}
```

### Running Multiple Projects
You can run multiple project instances with different configurations:

```bash
# Project A
QDRANT_COLLECTION_PREFIX=project_a MEM0_PROJECT_NAMESPACE=project_a docker-compose up

# Project B (in different directory)
QDRANT_COLLECTION_PREFIX=project_b MEM0_PROJECT_NAMESPACE=project_b docker-compose up
```

## Implementation Details

### Qdrant Service Changes
- **Collection Naming**: Uses prefix + collection name format
- **Isolation**: Each project gets its own collection
- **Backward Compatibility**: Works with existing collections

### Mem0 Service Changes
- **Storage Path**: Creates project-specific subdirectories
- **Memory Isolation**: Each project has separate memory storage
- **Namespace Support**: Full namespace isolation

### Validation Updates
- **Default User ID**: Configurable default user ID
- **Project Context**: All operations respect project isolation
- **Schema Updates**: Updated validation schemas

## Best Practices

### 1. Naming Conventions
- **Use Descriptive Names**: `client_acme`, `project_webapp`, `tech_react`
- **Avoid Special Characters**: Use underscores instead of spaces
- **Be Consistent**: Use same naming pattern across projects

### 2. Environment Management
- **Separate .env Files**: Create project-specific .env files
- **Version Control**: Don't commit sensitive data
- **Documentation**: Document project configurations

### 3. Data Management
- **Regular Backups**: Backup project-specific data
- **Cleanup**: Remove unused project data
- **Monitoring**: Monitor storage usage per project

### 4. Security Considerations
- **Access Control**: Limit access to project data
- **Encryption**: Consider encrypting sensitive project data
- **Audit Logs**: Track access to project resources

## Migration Guide

### From Single Project to Multi-Project
1. **Backup Existing Data**: Backup current collections and memory
2. **Set Project Configuration**: Configure isolation variables
3. **Test Isolation**: Verify data separation works correctly
4. **Update Documentation**: Document new project structure

### Data Migration
```bash
# Export existing data
docker exec mcp-rag-qdrant qdrant export --collection documents

# Import to new project collection
docker exec mcp-rag-qdrant qdrant import --collection project_a_documents
```

## Troubleshooting

### Common Issues
1. **Collection Not Found**: Check collection prefix configuration
2. **Memory Not Found**: Verify project namespace path
3. **User ID Issues**: Confirm default user ID setting

### Debug Commands
```bash
# Check Qdrant collections
curl http://localhost:6333/collections

# Check memory storage
ls -la ./mem0_data/

# Check environment variables
docker exec mcp-rag-server env | grep -E "(QDRANT|MEM0)"
```

## Future Enhancements

### Planned Features
1. **Project Templates**: Pre-configured project setups
2. **Cross-Project Search**: Controlled data sharing between projects
3. **Project Analytics**: Usage statistics per project
4. **Automated Cleanup**: Automatic cleanup of unused project data

### Integration Opportunities
1. **CI/CD Integration**: Automated project setup
2. **Monitoring Tools**: Project-specific monitoring
3. **Backup Solutions**: Automated project backups
4. **Access Management**: Role-based project access