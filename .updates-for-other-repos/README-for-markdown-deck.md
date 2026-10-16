# Updates needed for markdown-deck repository

## Add Release Documentation

1. Copy RELEASING-template-for-single-skill-repos.md as `docs/RELEASING.md`

2. Customize for markdown-deck:
   - Replace `[SKILL-NAME]` with `markdown-deck`
   - Replace `[REPO-NAME]` with `markdown-deck`
   - Add markdown-deck specific test commands

3. Update README.md to link to docs/RELEASING.md under a "For Maintainers" section

## Verify Current Tagging

Check that all versions in SKILL.md history have corresponding tags:

```bash
cd markdown-deck

# Check current version
grep 'version:' skills/markdown-deck/SKILL.md

# List existing tags
git tag -l 'markdown-deck--*'

# Check if current version is tagged
CURRENT_VERSION=$(grep 'version:' skills/markdown-deck/SKILL.md | sed 's/.*"\(.*\)".*/\1/')
git tag -l "markdown-deck--v${CURRENT_VERSION}"
```

If current version is not tagged and code is stable, create the tag.

## Document Dependencies

Add a section to README.md documenting:

1. What repositories depend on markdown-deck:
   - architecture-pattern (pattern skill)

2. Version compatibility:
   - Which Node versions are supported
   - Which Playwright versions are used
   - Any breaking changes in recent versions

## Add Version Compatibility Matrix

In SKILL.md or README.md, document:

```markdown
## Version Compatibility

| markdown-deck | Node  | Playwright | Used by pattern |
|---------------|-------|------------|-----------------|
| v0.6.8        | 18+   | 1.40       | v0.11.0+        |
| v0.6.7        | 18+   | 1.38       | v0.10.0+        |
```
