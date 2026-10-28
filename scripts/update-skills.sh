#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
#
# Install the architecture-pattern skills and the two they need (model, markdown-deck) into a
# repository, or update an installation to the latest releases.
#
#   ./update-skills.sh [--check-only] [--skills pattern,use-case,...] [--yes]
#
# Run from the root of the repository to install into.
#
# With a .agents/skills.json (a workspace that declares its skills, as Architecture Continuum's
# installer does): moves every source it knows to its latest release tag (a skill from its own
# repository to <skill>--vX.Y.Z; the Architecture Continuum bundle to its latest release), adds
# any skill named in --skills that is not declared yet, then reinstalls with the workspace's own
# installer. Sources it does not know are left as they are.
#
# Without one: copies the skills from the latest release into .agents/skills, every skill the
# release ships (pattern, use-case, cross-reference, portfolio, draft, convert) unless --skills
# names some, with model and markdown-deck, backing up any installed copy first. A first install
# and an update are the same run.
#
# --check-only shows what would change and changes nothing. --yes skips the confirmation.
# Needs bash, git, Node 18 or later and Python 3.11 or later.

set -euo pipefail

REPO_PATTERN="https://github.com/dermot-obrien/architecture-pattern.git"
REPO_MODEL="https://github.com/dermot-obrien/diagram-model.git"
REPO_DECK="https://github.com/dermot-obrien/markdown-deck.git"
REPO_CONTINUUM="https://github.com/dermot-obrien/architecture-continuum.git"
SKILLS_DIR=".agents/skills"
DECLARATION=".agents/skills.json"

CHECK_ONLY=0; YES=0; SKILLS=""
while [ $# -gt 0 ]; do
  case "$1" in
    --check-only) CHECK_ONLY=1 ;;
    --yes) YES=1 ;;
    --skills) shift; SKILLS="${1:-}" ;;
    --skills=*) SKILLS="${1#--skills=}" ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
  shift
done
SKILLS="${SKILLS//,/ }"

latest_tag() {  # latest_tag <repo> <prefix>
  git ls-remote --tags "$1" 2>/dev/null \
    | sed -n "s#.*refs/tags/\($2[0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*\)\$#\1#p" \
    | sort -V | tail -1
}

continuum_release() {  # the latest published release, which a stray tag cannot outrank
  local tag
  tag=$(node -e '
    fetch("https://api.github.com/repos/dermot-obrien/architecture-continuum/releases/latest",
          { headers: { "User-Agent": "update-skills" } })
      .then(r => r.ok ? r.json() : {}).then(j => console.log(j.tag_name || ""))
      .catch(() => console.log(""));' 2>/dev/null || true)
  [ -n "$tag" ] && { echo "$tag"; return; }
  latest_tag "$REPO_CONTINUUM" v
}

skill_version() {
  sed -n 's/^ *version: *"\([^"]*\)".*/\1/p' "$1/SKILL.md" 2>/dev/null | head -1 | grep . || echo "not installed"
}

confirm() {
  [ "$YES" = 1 ] && return 0
  read -r -p "$1 (y/N) " answer
  [ "$answer" = "y" ] || [ "$answer" = "Y" ]
}

for tool in git node; do
  command -v "$tool" >/dev/null || { echo "$tool is not on the PATH." >&2; exit 2; }
done
if [ ! -d .git ]; then
  echo "WARNING: no .git here. Skills go into $PWD/$SKILLS_DIR."
  confirm "Continue anyway?" || { echo "Cancelled."; exit 0; }
fi

if [ -f "$DECLARATION" ]; then
  echo "Reading $DECLARATION and finding the latest releases..."
  plan=$(node -e '
    const d = JSON.parse(require("fs").readFileSync(process.argv[1], "utf8"));
    d.sources.forEach((s, i) => {
      if (s.bundle && /dermot-obrien\/(architecture-continuum|ai-assisted-architecture)(\.git)?$/.test(s.bundle))
        console.log([i, "continuum", s.bundle, "-", s.ref].join(" "));
      else if (s.repo && s.name)
        console.log([i, "skill", s.repo, s.name, s.ref].join(" "));
    });' "$DECLARATION")
  updates=""
  while read -r index kind repo name ref; do
    [ -n "$index" ] || continue
    if [ "$kind" = continuum ]; then
      tag=$(continuum_release)
      if [ -n "$tag" ] && { [ "$ref" != "$tag" ] || [ "$repo" != "$REPO_CONTINUUM" ]; }; then
        printf '  %-24s %s -> %s\n' architecture-continuum "$ref" "$tag"; updates="$updates $index=bundle:$tag"
      fi
    else
      tag=$(latest_tag "$repo" "$name--v")
      if [ -n "$tag" ] && [ "$ref" != "$tag" ]; then
        printf '  %-24s %s -> %s\n' "$name" "$ref" "$tag"; updates="$updates $index=repo:$tag"
      fi
    fi
  done <<< "$plan"
  for name in $SKILLS; do
    if ! printf '%s\n' "$plan" | awk '{print $4}' | grep -qx "$name"; then
      tag=$(latest_tag "$REPO_PATTERN" "$name--v")
      [ -n "$tag" ] || { echo "architecture-pattern has no release of a skill called $name." >&2; exit 2; }
      printf '  %-24s added at %s\n' "$name" "$tag"; updates="$updates add=$name:$tag"
    fi
  done
  [ -n "$updates" ] || echo "Every source this script knows is at its latest release."
  [ "$CHECK_ONLY" = 1 ] && { echo "Check only: nothing changed."; exit 0; }
  if [ -n "$updates" ]; then
    confirm "Change these and reinstall?" || { echo "Cancelled."; exit 0; }
    REPO_CONTINUUM="$REPO_CONTINUUM" REPO_PATTERN="$REPO_PATTERN" node -e '
      const fs = require("fs"); const file = process.argv[1];
      const d = JSON.parse(fs.readFileSync(file, "utf8"));
      for (const u of process.argv.slice(2)) {
        const [key, rest] = u.split("="); const [what, tag] = rest.split(":");
        if (key === "add") { d.sources.push({ repo: process.env.REPO_PATTERN, ref: tag, path: "skills/" + what, name: what }); continue; }
        const s = d.sources[Number(key)];
        if (what === "bundle") s.bundle = process.env.REPO_CONTINUUM;
        s.ref = tag;
      }
      fs.writeFileSync(file, JSON.stringify(d, null, 2) + "\n");' "$DECLARATION" $updates
    echo "Updated $DECLARATION."
  fi
  status=0
  if [ -f scripts/architecture.mjs ]; then node scripts/architecture.mjs reinit || status=$?
  elif [ -f scripts/skills.mjs ]; then node scripts/skills.mjs sync --copy || status=$?
  else
    echo "This workspace declares its skills but has no installer: copy AI-Assisted Work's bin/skills.mjs to scripts/skills.mjs, or run Architecture Continuum's update-skills script." >&2
    exit 2
  fi
  [ "$status" = 0 ] || { echo "The reinstall stopped (exit $status); its output says why." >&2; exit "$status"; }
  [ -f scripts/skills.mjs ] && node scripts/skills.mjs check
  echo
  echo "Done. Read each release's changelog for anything a workspace must change, then commit .agents/skills.json and .agents/skills.lock.json."
  exit 0
fi

echo "Finding the latest releases..."
LATEST_PATTERN=$(latest_tag "$REPO_PATTERN" "pattern--v")
LATEST_MODEL=$(latest_tag "$REPO_MODEL" "model--v")
LATEST_DECK=$(latest_tag "$REPO_DECK" "markdown-deck--v")
if [ -z "$LATEST_PATTERN" ] || [ -z "$LATEST_MODEL" ] || [ -z "$LATEST_DECK" ]; then
  echo "Could not read the release tags from GitHub. Check the network and try again." >&2; exit 1
fi

timestamp=$(date +%Y%m%d-%H%M%S)
TEMP_DIR=".skill-update-temp-$timestamp"
trap 'rm -rf "$TEMP_DIR"' EXIT
mkdir -p "$TEMP_DIR"
git -c advice.detachedHead=false clone --quiet --depth 1 --branch "$LATEST_PATTERN" "$REPO_PATTERN" "$TEMP_DIR/architecture-pattern" 2>/dev/null
git -c advice.detachedHead=false clone --quiet --depth 1 --branch "$LATEST_MODEL" "$REPO_MODEL" "$TEMP_DIR/diagram-model" 2>/dev/null
git -c advice.detachedHead=false clone --quiet --depth 1 --branch "$LATEST_DECK" "$REPO_DECK" "$TEMP_DIR/markdown-deck" 2>/dev/null

# The release's skills, as "name path version check-command...", from its bundle.json.
release=$(node -e '
  const b = JSON.parse(require("fs").readFileSync(process.argv[1], "utf8"));
  for (const s of b.skills) console.log([s.name, s.path, s.version, ...((s.check || {}).command || [])].join(" "));' \
  "$TEMP_DIR/architecture-pattern/bundle.json")
released=$(printf '%s\n' "$release" | awk '{print $1}' | tr '\n' ' ')
wanted="${SKILLS:-$released}"
for name in $wanted; do
  printf '%s\n' $released | grep -qx "$name" || { echo "Release $LATEST_PATTERN has no skill called $name; it has $released" >&2; exit 2; }
done

echo
printf '  %-18s %-16s %s\n' skill installed release
while read -r name path version _; do
  case " $wanted " in *" $name "*) printf '  %-18s %-16s %s\n' "$name" "$(skill_version "$SKILLS_DIR/$name")" "$version" ;; esac
done <<< "$release"
printf '  %-18s %-16s %s\n' model "$(skill_version "$SKILLS_DIR/model")" "${LATEST_MODEL##*--v}"
printf '  %-18s %-16s %s\n' markdown-deck "$(skill_version "$SKILLS_DIR/markdown-deck")" "${LATEST_DECK##*--v}"

[ "$CHECK_ONLY" = 1 ] && { echo; echo "Check only: nothing changed."; exit 0; }
confirm "Install these into $SKILLS_DIR?" || { echo "Cancelled."; exit 0; }

BACKUP_DIR=".skill-backups/$timestamp"
for name in $wanted model markdown-deck; do
  if [ -d "$SKILLS_DIR/$name" ]; then
    mkdir -p "$BACKUP_DIR"
    (cd "$SKILLS_DIR" && tar --exclude=node_modules -cf - "$name") | (cd "$BACKUP_DIR" && tar -xf -)
    rm -rf "${SKILLS_DIR:?}/$name"
  fi
done
[ -d "$BACKUP_DIR" ] && echo "Backed up the old copies to $BACKUP_DIR (node_modules left out)."

mkdir -p "$SKILLS_DIR"
while read -r name path version _; do
  case " $wanted " in *" $name "*) cp -r "$TEMP_DIR/architecture-pattern/$path" "$SKILLS_DIR/"; echo "  installed $name $version" ;; esac
done <<< "$release"
cp -r "$TEMP_DIR/diagram-model/skills/model" "$SKILLS_DIR/"; echo "  installed model ${LATEST_MODEL##*--v}"
cp -r "$TEMP_DIR/markdown-deck/skills/markdown-deck" "$SKILLS_DIR/"; echo "  installed markdown-deck ${LATEST_DECK##*--v}"
case " $wanted " in *" pattern "*)
  for helper in list-patterns.sh list-patterns.ps1; do
    [ -f "$TEMP_DIR/architecture-pattern/scripts/$helper" ] && cp "$TEMP_DIR/architecture-pattern/scripts/$helper" "$SKILLS_DIR/pattern/scripts/"
  done ;;
esac

rm -rf "$TEMP_DIR"

echo
echo "Installing markdown-deck's npm packages..."
npm install --prefix "$SKILLS_DIR/markdown-deck" --no-audit --no-fund >/dev/null 2>&1 \
  || echo "  npm install failed: run npm install --prefix $SKILLS_DIR/markdown-deck"

echo
echo "Running each skill's post-install check (binding warnings are normal before .agents/skill-bindings.toml exists)..."
while read -r name path version runtime script rest; do
  case " $wanted " in *" $name "*) ;; *) continue ;; esac
  [ -n "${script:-}" ] || continue
  echo "$name:"
  $runtime "$SKILLS_DIR/$name/$script" $rest 2>&1 | head -8 | sed 's/^/  /' || true
done <<< "$release"

echo
echo "Done. Add .agents/skills/ to .gitignore if it is not there. Next:"
echo "  1. Bind the skills: .agents/skill-bindings.toml (docs/quick-start.md, step 3)"
echo "  2. Check the bindings: python $SKILLS_DIR/model/bin/model.py doctor --skill pattern"
echo "  3. Re-validate existing documents: python $SKILLS_DIR/model/bin/model.py scan <folder> --recursive"
