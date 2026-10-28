<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Releasing and Tagging

**IMPORTANT:** This repository contains multiple skills that must be tagged separately with coordinated versions. Always verify version compatibility across repositories before releasing.

## Branches

The repository follows Git Flow. Work merges into `develop` through pull requests, squash merged with the pull request's title as the subject. A release is a pull request from `develop` to `main`, titled `release: ...`, merged with a merge commit, never squashed; the tags go on that merge commit on `main`. `main` is protected: it takes changes only through pull requests.

## Version Dependencies

The skills in this repository depend on specific versions of skills in other repositories:

- **pattern** skill depends on:
  - `model` skill from [diagram-model](https://github.com/dermot-obrien/diagram-model) >= v0.9.0 (requires `contract` command)
  - `markdown-deck` skill from [markdown-deck](https://github.com/dermot-obrien/markdown-deck) >= v0.6.8

- **use-case** skill depends on:
  - `model` skill from [diagram-model](https://github.com/dermot-obrien/diagram-model) >= v0.9.0

- **cross-reference** skill depends on:
  - `model` skill from [diagram-model](https://github.com/dermot-obrien/diagram-model) >= v0.8.0

## Tag Naming Convention

Each skill in a repository gets its own tag series:

```
<skill-name>--v<major>.<minor>.<patch>
```

Examples:
- `pattern--v0.11.0`
- `use-case--v0.3.0`
- `cross-reference--v0.3.0`
- `model--v0.9.0`
- `markdown-deck--v0.6.8`

**Note the double-dash (`--`)** between skill name and version.

## Pre-Release Checklist

Before creating a release tag, verify:

### 1. Check version in SKILL.md

```bash
# For pattern skill
grep 'version:' skills/pattern/SKILL.md
```

The version field must match the tag you're about to create.

### 2. Verify dependency versions

Check that required dependency versions exist as tags:

```bash
# Check if model v0.9.0 tag exists
git ls-remote --tags https://github.com/dermot-obrien/diagram-model.git | grep 'model--v0.9.0'

# Check if markdown-deck v0.6.8 tag exists
git ls-remote --tags https://github.com/dermot-obrien/markdown-deck.git | grep 'markdown-deck--v0.6.8'
```

**If a required tag doesn't exist, you MUST release the dependency repository first.**

### 3. Update CHANGELOG

Document changes in the skill's CHANGELOG.md:
- What changed
- Breaking changes (if any)
- Minimum dependency versions (if changed)

### 4. Run tests

```bash
# Run CI checks
python skills/pattern/scripts/check.py
python skills/model/bin/model.py doctor --skill pattern

# Validate examples still work
python skills/pattern/scripts/publish.py skills/pattern/examples/composite --recursive
```

### 5. Update quick-start and documentation

If dependency versions changed, update:
- `docs/quick-start.md` - version tags in install commands
- `README.md` - version requirements
- `docs/updating.md` - if update process changed

## Creating a Release

### Step 1: Update version and documentation

```bash
# 1. Update version in skills/pattern/SKILL.md
# 2. Update CHANGELOG.md
# 3. Update docs/quick-start.md with new version tags (if changed)

# Run version sync check
bash scripts/check-version-sync.sh  # or .\scripts\check-version-sync.ps1

# If sync check passes, commit
git add -A
git commit -m "chore: prepare pattern 0.15.0"
```

This happens on a branch from `develop`, merged into `develop` by pull request. Then open the release pull request from `develop` to `main` and merge it with a merge commit.

**The version sync checker verifies:**
- SKILL.md versions match what's in quick-start.md
- Dependency versions in SKILL.md have corresponding tags
- Repository URLs in update scripts are correct
- Tags exist locally for current versions

### Step 2: Create and push the tag

Tag the release's merge commit on `main`, one tag for every skill whose version changed, all on the same commit:

```bash
git fetch origin
git tag pattern--v0.15.0 origin/main
git tag use-case--v0.4.1 origin/main
git push origin pattern--v0.15.0 use-case--v0.4.1
```

Nothing is pushed to `main` directly; the merge of the release pull request is the commit.

### Step 3: Verify tag is accessible

```bash
# Check the tag appears remotely
git ls-remote --tags origin | grep pattern--v0.12.0

# Test that clone works
cd /tmp
git clone --depth 1 --branch pattern--v0.12.0 \
  https://github.com/dermot-obrien/architecture-pattern.git test-clone
rm -rf test-clone
```

### Step 4: Update dependent documentation

If this is a new minimum required version, update:
- Other repositories that depend on this skill
- Update scripts that pin versions
- Team documentation or wikis

## Multi-Skill Release Workflow

When releasing multiple skills in this repository:

1. **Release in dependency order** (pattern depends on use-case and cross-reference, so release those first if needed)
2. **Tag each skill separately** with its own version
3. **Test each skill independently** before moving to the next

Example: a release that changes several skills tags each of them on the release's merge commit:

```bash
git fetch origin
for tag in pattern--v0.15.0 use-case--v0.4.1 portfolio--v0.1.0 draft--v0.1.0 convert--v0.1.0; do git tag "$tag" origin/main; done
git push origin pattern--v0.15.0 use-case--v0.4.1 portfolio--v0.1.0 draft--v0.1.0 convert--v0.1.0
```

The install script (`scripts/update-skills.ps1`, `.sh`) installs each skill at its newest `<skill>--v` tag, so a skill without a new tag stays at its last one.

## Cross-Repository Release Coordination

When changes require coordinated releases across multiple repositories:

### Scenario: Adding a new model command that pattern needs

1. **diagram-model repository:**
   - Implement the new command
   - Update model SKILL.md version to next minor/major
   - Update CHANGELOG.md
   - Commit, tag as `model--vX.Y.0`, push
   - **Verify tag is pushed and accessible**

2. **architecture-pattern repository:**
   - Update pattern to use the new command
   - Update pattern SKILL.md to document new model minimum version
   - Update quick-start.md and updating.md with new version tags
   - Commit, tag as `pattern--vX.Y.0`, push

### Scenario: Fixing a bug in markdown-deck

1. **markdown-deck repository:**
   - Fix the bug
   - Update SKILL.md version (patch bump)
   - Update CHANGELOG.md
   - Commit, tag as `markdown-deck--vX.Y.Z`, push

2. **architecture-pattern repository (if needed):**
   - Update docs to recommend new minimum version
   - Update update scripts if auto-fetching latest
   - Commit, tag if pattern version needs bump

## Verifying Version Compatibility

Use this script to check current installed versions against requirements:

```bash
# Check installed versions
python .agents/skills/pattern/scripts/check.py

# Check model version specifically
grep 'version:' .agents/skills/model/SKILL.md

# Check what commands model supports
python .agents/skills/model/bin/model.py --help | grep -A 20 "positional arguments"
```

## Common Mistakes to Avoid

1. ❌ **Forgetting to push tags**: `git push` doesn't push tags by default
   - ✅ Always: `git push origin <tag-name>`

2. ❌ **Using single dash in tag**: `pattern-v0.11.0`
   - ✅ Correct: `pattern--v0.11.0` (double dash)

3. ❌ **Tagging without updating SKILL.md version**
   - ✅ Version in SKILL.md must match the tag

4. ❌ **Releasing pattern before model when pattern needs new model features**
   - ✅ Release dependencies first, verify tags exist remotely

5. ❌ **Not testing that tags are clonable**
   - ✅ Test `git clone --depth 1 --branch <tag>` after pushing

6. ❌ **Forgetting to update quick-start.md with new version numbers**
   - ✅ Update all documentation that pins specific versions

7. ❌ **Creating release tag on wrong commit**
   - ✅ Verify `git log` shows the right commit before tagging

## Rollback a Bad Release

If you need to remove a bad tag:

```bash
# Delete local tag
git tag -d pattern--v0.12.0

# Delete remote tag
git push origin :refs/tags/pattern--v0.12.0
```

**Warning:** Only do this immediately after release. If anyone has already installed the tag, create a new patch version instead.

## Agent Instructions

When asked to create a release:

1. Check CHANGELOG for version number and changes
2. Verify version in SKILL.md matches
3. Check that all dependency versions exist as pushed tags
4. Run tests/checks (`check.py`, `doctor`, etc.)
5. **Run version sync checker:** `./scripts/check-version-sync.sh` or `check-version-sync.ps1`
6. Update documentation if versions changed (then rerun sync checker)
7. Create annotated tag with summary
8. Push tag AND commits
9. Verify tag is accessible remotely
10. Update any cross-repo documentation

When asked to check version compatibility:

1. List installed versions from SKILL.md files
2. Check available remote tags
3. Compare requirements documented in CHANGELOG/docs
4. Report any mismatches or missing tags
5. Recommend update order if needed
