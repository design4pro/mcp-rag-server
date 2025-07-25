---
title: documentation-preparation-workflow
type: note
permalink: project-management/documentation-preparation-workflow
tags:
- '[''documentation-workflow'
- basic-memory'
- '''obsidian-compatible'''
- '''project-management'']'
---

# Documentation Preparation Workflow

## Overview

This document outlines the standardized workflow for preparing project documentation using Basic Memory tools, following the successful restructuring of the MCP RAG Server documentation.

## Workflow Steps

### 1. Project Setup and Memory Management

#### Before Starting Documentation Work
- **Verify Memory Project**: Always ensure you're on the correct memory project for the current project
- **Set Default Project**: If needed, create and set the memory project as default
- **Check Project Status**: Use `get_current_project()` to confirm active project

#### Memory Project Commands
```bash
# List available projects
mcp_c-basic-memory_list_memory_projects()

# Switch to project
mcp_c-basic-memory_switch_project("project-name")

# Set as default
mcp_c-basic-memory_set_default_project("project-name")

# Create new project if needed
mcp_c-basic-memory_create_memory_project("project-name", "project-path", set_default=True)
```

### 2. Documentation Structure Planning

#### Folder Organization
Always organize documentation in logical subfolders:
```
docs/
├── 00-overview/           # Main documentation index and project overview
├── 01-architecture/       # System architecture and design
├── 02-installation/       # Setup and installation guides
├── 03-api/               # API documentation and references
├── 04-development/       # Development guides, phases, refactoring
└── 05-troubleshooting/   # Troubleshooting and debugging guides
```

#### Naming Conventions
- **Kebab-case**: All file names must use kebab-case format
  - ✅ `installation-guide.md`
  - ✅ `api-reference.md`
  - ✅ `troubleshooting-guide.md`
  - ❌ `installation_guide.md`
  - ❌ `InstallationGuide.md`

### 3. Content Generation Process

#### Using Basic Memory write_note Tool
Always use `mcp_c-basic-memory_write_note` for creating documentation:

```python
mcp_c-basic-memory_write_note(
    title="filename-without-extension",
    content="# Document Title\n\nContent here...",
    folder="docs/subfolder-name",
    tags=['relevant', 'tags', 'obsidian-compatible']
)
```

#### Content Requirements
- **Atomic Notes**: Each note should address a single concept
- **Obsidian Links**: Use proper Obsidian-style linking
  - `[[../folder/filename]]` for relative links
  - `[[filename|display text]]` for custom display text
- **English Language**: All content must be in English
- **Cross-references**: Include related documentation links

### 4. Link Management

#### Obsidian-Style Linking
- **Relative Paths**: Use `../` for parent directory navigation
- **Consistent Format**: Always use `[[../folder/filename]]` pattern
- **Display Text**: Use `[[../folder/filename|Display Text]]` for better readability

#### Example Link Structure
```markdown
## Related Documentation

- [[../01-architecture/system-architecture|System Architecture]]
- [[../02-installation/installation-guide|Installation Guide]]
- [[../03-api/api-reference|API Reference]]
- [[../04-development/development-phases|Development Phases]]
- [[../05-troubleshooting/troubleshooting-guide|Troubleshooting Guide]]
```

### 5. Quality Assurance

#### Before Finalizing
- **Check All Links**: Ensure all cross-references are correct
- **Verify Structure**: Confirm folder organization is logical
- **Test Obsidian Compatibility**: Verify links work in Obsidian
- **Review Content**: Ensure atomic note structure is maintained

#### Validation Checklist
- [ ] All files use kebab-case naming
- [ ] All links use proper Obsidian format
- [ ] Each note addresses single concept (atomic)
- [ ] Cross-references are comprehensive
- [ ] Content is in English
- [ ] Tags are relevant and descriptive

### 6. Project Integration

#### Update Main README
Always update the main project README.md with new documentation links:

```markdown
## Documentation

Comprehensive documentation is available in the `docs/` directory:

- **Documentation Index**: [[docs/00-overview/documentation-index.md]]
- **Project Overview**: [[docs/00-overview/project-overview.md]]
- **System Architecture**: [[docs/01-architecture/system-architecture.md]]
- **Installation Guide**: [[docs/02-installation/installation-guide.md]]
- **API Reference**: [[docs/03-api/api-reference.md]]
- **Development Phases**: [[docs/04-development/development-phases.md]]
- **Project Refactoring**: [[docs/04-development/project-refactoring.md]]
- **Troubleshooting**: [[docs/05-troubleshooting/troubleshooting-guide.md]]
```

## Best Practices

### Documentation Standards
1. **Consistency**: Follow established patterns and conventions
2. **Completeness**: Ensure comprehensive coverage of topics
3. **Clarity**: Write clear, concise, and well-organized content
4. **Maintainability**: Structure for easy updates and modifications

### Technical Requirements
1. **Basic Memory Integration**: Always use `write_note` for creation
2. **Obsidian Compatibility**: Ensure proper markdown and linking
3. **Version Control**: Commit documentation with related code changes
4. **Cross-Platform**: Ensure compatibility across different systems

### Workflow Efficiency
1. **Plan First**: Always create a plan before starting
2. **Batch Operations**: Group related documentation tasks
3. **Validation**: Verify each step before proceeding
4. **Documentation**: Document the documentation process itself

## Example Workflow

### For New Project Documentation
1. **Setup**: Verify/create memory project
2. **Plan**: Create documentation structure plan
3. **Create**: Generate atomic notes using `write_note`
4. **Link**: Establish cross-references
5. **Validate**: Check all links and structure
6. **Integrate**: Update main README and project files

### For Documentation Updates
1. **Backup**: Create backup of existing documentation
2. **Plan**: Identify what needs to be updated
3. **Execute**: Apply changes using `write_note`
4. **Test**: Verify all links and references
5. **Commit**: Update version control with changes

## Success Metrics

### Quality Indicators
- ✅ All files follow kebab-case naming
- ✅ All links use proper Obsidian format
- ✅ Atomic note structure maintained
- ✅ Comprehensive cross-referencing
- ✅ English language throughout
- ✅ Logical folder organization

### Efficiency Indicators
- ✅ Documentation created using Basic Memory tools
- ✅ Consistent workflow followed
- ✅ All validation steps completed
- ✅ Project integration successful

## Related Documentation

- [[../00-overview/documentation-index|Documentation Index]]
- [[../04-development/project-refactoring|Project Refactoring History]]
- [[../02-installation/installation-guide|Installation Guide]]