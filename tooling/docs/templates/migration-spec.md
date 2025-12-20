# Migration Specification: [MIGRATION-ID]

**Priority**: [Critical/High/Medium/Low]
**Status**: Planned
**Created**: YYYY-MM-DD
**Target Date**: YYYY-MM-DD

## Overview

[Brief description of what is being migrated]

## Motivation

[Why this migration is necessary]

- [Reason 1]
- [Reason 2]

## Current State

| Component | Current Version | Target Version |
|-----------|-----------------|----------------|
| [Dependency/Framework] | [current] | [target] |

## Migration Steps

### Pre-Migration

- [ ] Backup current state
- [ ] Review breaking changes
- [ ] Update test environment
- [ ] Notify stakeholders

### Migration

1. **Step 1**: [Description]
   - Files affected: `path/to/file`
   - Commands: `npm install xyz@latest`

2. **Step 2**: [Description]
   - Files affected: `path/to/file`
   - Changes needed: [describe]

3. **Step 3**: [Description]
   - Files affected: `path/to/file`
   - Changes needed: [describe]

### Post-Migration

- [ ] Run full test suite
- [ ] Manual testing of critical paths
- [ ] Update documentation
- [ ] Monitor for issues

## Breaking Changes

| Change | Impact | Resolution |
|--------|--------|------------|
| [Change 1] | [What breaks] | [How to fix] |
| [Change 2] | [What breaks] | [How to fix] |

## Rollback Plan

### Trigger Conditions
- [When to rollback]

### Rollback Steps
1. [Step 1]
2. [Step 2]
3. [Step 3]

## Testing Plan

- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] E2E tests pass
- [ ] Performance benchmarks acceptable
- [ ] Manual testing complete

## Dependencies

- [Dependency 1]: [status]
- [Dependency 2]: [status]

## Notes

[Additional context, links to documentation, etc.]

---

**To run this migration:**
```bash
./run-story.sh [MIGRATION-ID] --migrate
```
