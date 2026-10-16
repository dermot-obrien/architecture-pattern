# Action Needed in Other Repositories

## Critical: diagram-model Repository

### Immediate Issue

**Version 0.9.0 is not tagged but is required by pattern v0.11.0**

The main branch has:
- `skills/model/SKILL.md` version: "0.9.0"
- The `contract` command implemented in code

But git tags show:
- Latest: `model--v0.8.2` 
- No `model--v0.9.0` tag exists

**Impact:** 
- Update scripts can only install v0.8.2
- Users get `model: error: argument cmd: invalid choice: 'contract'`
- Pattern v0.11.0's `check.py` fails because it requires `contract` command

### Required Actions

1. **Tag v0.9.0 immediately:**
   ```bash
   cd diagram-model
   git checkout main
   git pull
   
   # Verify version in SKILL.md
   grep 'version:' skills/model/SKILL.md
   
   # Tag the current HEAD (or appropriate commit)
   git tag -a model--v0.9.0 -m "Release model v0.9.0
   
   - Add contract command for template validation
   - Required by pattern v0.11.0+"
   
   git push origin model--v0.9.0
   
   # Verify it's accessible
   git ls-remote --tags origin | grep model--v0.9.0
   ```

2. **Add release documentation:**
   - Copy `RELEASING-template-for-single-skill-repos.md` to `docs/RELEASING.md`
   - Customize for model skill (replace placeholders)
   - Link from README.md

3. **Check for other missing tags:**
   - Look at git history for version bumps without corresponding tags
   - Tag any stable versions that are missing tags

4. **Document version compatibility:**
   - Add a compatibility matrix showing which pattern versions need which model versions
   - Document in README or SKILL.md

See `README-for-diagram-model.md` for detailed instructions.

## markdown-deck Repository

### Required Actions

1. **Verify all versions are tagged:**
   ```bash
   cd markdown-deck
   grep 'version:' skills/markdown-deck/SKILL.md
   git tag -l 'markdown-deck--*'
   ```

2. **Add release documentation:**
   - Copy `RELEASING-template-for-single-skill-repos.md` to `docs/RELEASING.md`
   - Customize for markdown-deck skill
   - Link from README.md

3. **Document dependencies:**
   - Which pattern versions depend on which markdown-deck versions
   - Node and Playwright version requirements

See `README-for-markdown-deck.md` for detailed instructions.

## Files Provided

In `.updates-for-other-repos/`:

1. **RELEASING-template-for-single-skill-repos.md**
   - Complete release guide template
   - Copy to diagram-model and markdown-deck as `docs/RELEASING.md`
   - Customize by replacing `[SKILL-NAME]`, `[REPO-NAME]` placeholders

2. **README-for-diagram-model.md**
   - Specific instructions for diagram-model
   - Includes commands to fix the missing v0.9.0 tag

3. **README-for-markdown-deck.md**
   - Specific instructions for markdown-deck
   - Verification and documentation steps

## Testing Version Compatibility

After tagging, test the update scripts work:

```bash
# In a test directory
cd /tmp
mkdir test-install && cd test-install

# Download update script
curl -o update-skills.sh https://raw.githubusercontent.com/dermot-obrien/architecture-pattern/main/scripts/update-skills.sh
chmod +x update-skills.sh

# Run it
./update-skills.sh

# Verify versions installed
grep 'version:' .agents/skills/model/SKILL.md
grep 'version:' .agents/skills/pattern/SKILL.md

# Test contract command exists
python .agents/skills/model/bin/model.py --help | grep contract
```

## Root Cause Summary

This issue occurred because:

1. **No release process documentation** - maintainers didn't know the tagging convention
2. **No cross-repo version tracking** - pattern was released without verifying model tag existed
3. **No pre-release checks** - no script to verify dependency tags exist before releasing
4. **Documentation had wrong versions** - quick-start.md referenced `model--v0.9.0` that didn't exist

The new `docs/RELEASING.md` prevents this by:
- Documenting the tagging convention (`skill--vX.Y.Z`)
- Requiring dependency version verification before release
- Providing agent-readable instructions
- Including test commands to verify releases

## Next Steps

1. Tag `model--v0.9.0` in diagram-model (highest priority)
2. Add RELEASING.md to diagram-model
3. Add RELEASING.md to markdown-deck
4. Verify all skills have matching version/tag pairs
5. Test update scripts work end-to-end
