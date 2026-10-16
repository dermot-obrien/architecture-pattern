<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Releasing and Tagging

**Template for diagram-model and markdown-deck repositories**

This repository provides the `[SKILL-NAME]` skill used by other repositories. Proper tagging and version management ensures compatibility across the ecosystem.

## Tag Naming Convention

Tags must follow this format:

```
[SKILL-NAME]--v<major>.<minor>.<patch>
```

Examples:
- `model--v0.9.0`
- `markdown-deck--v0.6.8`

**Note the double-dash (`--`)** between skill name and version.

## Dependent Repositories

The following repositories depend on this skill:

- [architecture-pattern](https://github.com/dermot-obrien/architecture-pattern)
  - pattern skill requires >= vX.Y.Z
  - use-case skill requires >= vX.Y.Z
  - cross-reference skill requires >= vX.Y.Z

**Before releasing a breaking change, coordinate with these repositories.**

## Pre-Release Checklist

### 1. Check version in SKILL.md

```bash
grep 'version:' skills/[SKILL-NAME]/SKILL.md
```

The version field must match the tag you're about to create.

### 2. Update CHANGELOG

Document changes in CHANGELOG.md:
- What changed
- Breaking changes (if any)
- New commands or features
- Minimum dependency versions (if any)

### 3. Run tests

```bash
# Run repository tests
pytest

# Run doctests if applicable
python skills/[SKILL-NAME]/bin/[SKILL-NAME].py --version

# Test with example patterns
[Add repo-specific test commands]
```

### 4. Update documentation

If breaking changes or new features:
- Update SKILL.md usage examples
- Update README.md if install process changed
- Document new commands in help text

## Creating a Release

### Step 1: Update version and commit

```bash
# Edit skills/[SKILL-NAME]/SKILL.md to increment version
# Edit CHANGELOG.md to document changes

git add -A
git commit -m "chore: prepare [SKILL-NAME] v0.10.0 release"
```

### Step 2: Create and push the tag

```bash
# Create annotated tag
git tag -a [SKILL-NAME]--v0.10.0 -m "Release [SKILL-NAME] v0.10.0

- Feature X added
- Bug Y fixed
- Breaking: Z changed"

# Push the tag
git push origin [SKILL-NAME]--v0.10.0

# Push the commit
git push origin main
```

### Step 3: Verify tag is accessible

```bash
# Check the tag appears remotely
git ls-remote --tags origin | grep [SKILL-NAME]--v0.10.0

# Test that clone works
cd /tmp
git clone --depth 1 --branch [SKILL-NAME]--v0.10.0 \
  https://github.com/dermot-obrien/[REPO-NAME].git test-clone
rm -rf test-clone
```

### Step 4: Notify dependent repositories

If this release includes:
- New minimum version requirements
- Breaking changes
- New features that other repos should adopt

Open an issue or PR in dependent repositories to:
- Update their documentation
- Update their update scripts
- Update version pins in quick-start guides

## Cross-Repository Release Coordination

### Scenario: Adding a new command that pattern needs

1. **This repository ([SKILL-NAME]):**
   - Implement the new command/feature
   - Update SKILL.md version to next minor/major
   - Update CHANGELOG.md
   - Run all tests
   - Commit, tag as `[SKILL-NAME]--vX.Y.0`, push
   - **Verify tag is pushed and accessible**

2. **Dependent repositories:**
   - Wait for tag to be pushed and verified
   - Update to use the new feature
   - Update their minimum version requirements
   - Update their documentation
   - Create their own releases

### Scenario: Bug fix release

1. Fix the bug in this repository
2. Increment patch version (e.g., v0.9.0 → v0.9.1)
3. Tag and push
4. Update documentation in dependent repos to recommend new version (optional for patch fixes)

## Version Compatibility Checking

Dependent repositories should verify installed versions:

```bash
# They can check version with:
grep 'version:' .agents/skills/[SKILL-NAME]/SKILL.md

# Or test command availability:
python .agents/skills/[SKILL-NAME]/bin/[SKILL-NAME].py --help
```

## Common Mistakes to Avoid

1. ❌ **Forgetting to push tags**: `git push` doesn't push tags by default
   - ✅ Always: `git push origin <tag-name>`

2. ❌ **Using single dash in tag**: `model-v0.9.0`
   - ✅ Correct: `model--v0.9.0` (double dash)

3. ❌ **Tagging without updating SKILL.md version**
   - ✅ Version in SKILL.md must match the tag

4. ❌ **Not testing that tags are clonable**
   - ✅ Test `git clone --depth 1 --branch <tag>` after pushing

5. ❌ **Pushing breaking changes in patch versions**
   - ✅ Use semantic versioning: patch for fixes, minor for features, major for breaking changes

6. ❌ **Creating tag on wrong commit**
   - ✅ Verify `git log` shows the right commit before tagging

## Rollback a Bad Release

If you need to remove a bad tag:

```bash
# Delete local tag
git tag -d [SKILL-NAME]--v0.10.0

# Delete remote tag
git push origin :refs/tags/[SKILL-NAME]--v0.10.0
```

**Warning:** Only do this immediately after release. If anyone has already installed the tag, create a new patch version instead.

## Agent Instructions

When asked to create a release:

1. Check CHANGELOG for version number and changes
2. Verify version in SKILL.md matches
3. Run tests/checks
4. Update documentation if needed
5. Create annotated tag with summary
6. Push tag AND commits
7. Verify tag is accessible remotely
8. Check if dependent repositories need notification

When asked to check version:

1. Report version from SKILL.md
2. List recent tags
3. Check if tag exists for current version
4. Report any version mismatches

When asked about breaking changes:

1. Increment major version (or minor if pre-1.0)
2. Document in CHANGELOG with "Breaking:" prefix
3. Update SKILL.md with migration guide
4. Notify maintainers of dependent repositories BEFORE releasing
