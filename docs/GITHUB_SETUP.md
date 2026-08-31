# GitHub Setup

The local repository is deliberately prepared without a remote. Creating a
GitHub repository changes an external account, so Charlie keeps that final
choice.

Before the first push, inspect the commit identity that Git will publish:

```sh
git show -s --format='%an <%ae>' HEAD
```

If you prefer GitHub's private no-reply address, configure it for this
repository and amend the still-unpublished initial commit before adding the
remote. Then recreate the local baseline tag at the amended commit. GitHub
documents the exact no-reply address for each account under email settings.

## Recommended first remote

Create an **empty private repository** on GitHub:

1. Choose a repository name such as `district-zero`.
2. Select **Private**.
3. Do not initialize it with a README, `.gitignore`, or license; this local
   repository already has those decisions recorded.
4. Copy the SSH or HTTPS Git URL shown by GitHub.

From this repository root:

```sh
git remote add origin git@github.com:YOUR_ACCOUNT/district-zero.git
git push -u origin main
git push origin r7-owner-review-github-baseline
```

Never put a personal access token in the URL or a checked-in file. Use
GitHub's credential manager, GitHub Desktop, or SSH authentication.

The largest source file is about 32.5 MiB. It is allowed in ordinary Git but
larger than GitHub's browser-upload limit, so do not upload this tree by
dragging files into the website.

## GitHub Desktop alternative

1. Choose **File → Add Local Repository**.
2. Select this repository folder.
3. Use **Publish repository**.
4. Keep **Private** selected.

GitHub Desktop should publish the existing commit and tag. It should not
generate or replace repository files.

## On another machine

```sh
git clone YOUR_GIT_URL district-zero
cd district-zero
python3 tools/verify_repo.py
GODOT_BIN=/path/to/exact/godot python3 tools/launch.py --prepare-only
GODOT_BIN=/path/to/exact/godot python3 tools/launch.py --smoke-frames 180
```

Then open `game/project.godot` or run `python3 tools/launch.py`.

On Windows PowerShell, use the same repository with native path syntax:

```powershell
$env:GODOT_BIN = "C:\Path\To\Godot_v4.7.1-stable_win64.exe"
py -3 tools\verify_repo.py
py -3 tools\launch.py --prepare-only
py -3 tools\launch.py --smoke-frames 180
```

Godot's imported cache is regenerated in `game/.godot/`; `git status --short`
should remain empty afterward.

## Before making the repository public

- Choose an actual software/content license. No license is currently granted.
- Decide whether historical owner-name and `/Users/cmish/...` provenance hints
  should be public.
- Decide whether the AI-generated concept sheet and its provenance metadata
  belong in the public design archive.
- Re-run `python3 tools/verify_repo.py --require-clean`.
- Review GitHub's secret scan and repository visibility before changing it.
- Do not call the build `P1A PASS`, `P1B PASS`, or shipping-ready.

If public presentation should omit the full historical packet, build a
separate, versioned public-source derivative from the documented runtime
closure. Do not scrub or delete evidence in this verified private baseline.

## Routine workflow

```sh
git switch -c feature/short-description
# work and test
python3 tools/verify_repo.py
git diff --check
git add --all
git commit -m "Describe the bounded change"
git push -u origin feature/short-description
```

GitHub is excellent cross-machine source control, but releases and exported
game builds should remain separate artifacts rather than committed archives.
