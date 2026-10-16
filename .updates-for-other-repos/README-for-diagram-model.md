# Updates needed for diagram-model repository

## Critical Issue

**The `model` skill version 0.9.0 exists in code but was never tagged!**

The main branch has:
- Version: 0.9.0 in SKILL.md
- The `contract` command implemented

But only these tags exist:
- `model--v0.8.2` (latest)
- `model--v0.8.1`
- `model--v0.8.0`

This breaks compatibility with `pattern--v0.11.0` which requires `model >= 0.9.0`.

## Immediate Action Required

1. Create and push the missing tag for v0.9.0:

```bash
cd diagram-model

# Find the commit where version became 0.9.0
git log --all --grep="0.9.0" --oneline
# OR
git log --all -p skills/model/SKILL.md | grep -B 5 "version.*0.9.0"

# Tag that commit
git tag -a model--v0.9.0 <commit-hash> -m "Release model v0.9.0

Adds contract command for template validation
Required by pattern v0.11.0+"

# Push the tag
git push origin model--v0.9.0

# Verify it's accessible
git ls-remote --tags origin | grep model--v0.9.0
```

2. If 0.9.0 is already in main/HEAD, tag the current commit:

```bash
cd diagram-model
git checkout main
git pull

# Verify version
grep 'version:' skills/model/SKILL.md

# Tag current HEAD
git tag -a model--v0.9.0 -m "Release model v0.9.0

Adds contract command for template validation
Required by pattern v0.11.0+"

git push origin model--v0.9.0
```

3. Add the RELEASING.md file from the template (see RELEASING-template-for-single-skill-repos.md)

4. Update README.md to reference the release guide

## Long-term Improvements

1. **Add release documentation** - Copy and customize the RELEASING-template-for-single-skill-repos.md

2. **Document version compatibility** - Add a compatibility matrix showing:
   - Which model versions work with which pattern versions
   - When breaking changes were introduced

3. **Add pre-commit checks** - Verify SKILL.md version matches latest tag + 1

4. **Add CI check** - Fail if SKILL.md version exists as a tag but code has changes

5. **Coordinate releases** - When adding features pattern needs, coordinate release timing
