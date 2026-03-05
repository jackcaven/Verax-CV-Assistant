# GitHub Actions Workflows

This directory contains CI/CD workflows for the Verax CV Assistant project.

## Workflows

### 1. `build-and-test.yml` — Build & Test

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

**What it does:**
1. **Test Phase** (runs on Linux, 3 Python versions: 3.9, 3.11, 3.12)
   - Installs dependencies
   - Runs linting with `ruff`
   - Runs type checking with `mypy`
   - Runs unit & integration tests with `pytest`
   - Uploads coverage report to Codecov

2. **Build Phase** (only if tests pass, runs on Windows, macOS, Linux)
   - Builds executable using the packaging scripts:
     - `packaging/build_windows.sh` → `Verax.exe`
     - `packaging/build_macos.sh` → `Verax.app`
     - `packaging/build_linux.sh` → `Verax`
   - Uploads artifacts (retained for 30 days)
   - Generates per-platform build reports

3. **Summary Phase**
   - Produces workflow summary with test & build status
   - Links to downloadable artifacts

**Artifacts:**
- `Verax-Windows` — Windows executable directory
- `Verax-macOS` — macOS app bundle directory
- `Verax-Linux` — Linux executable directory

### 2. `release.yml` — Release

**Triggers:**
- Pushing a git tag: `git tag v1.0.0 && git push origin v1.0.0`

**What it does:**
1. **Test Phase** — Runs full test suite before release
2. **Build Phase** — Builds on all 3 platforms
3. **Package Phase** — Creates platform-specific archives:
   - Windows: `.zip` file
   - macOS: `.dmg` (disk image)
   - Linux: `.tar.gz` (gzip archive)
4. **Release Phase** — Creates GitHub Release with:
   - Automated release notes
   - All platform-specific artifacts attached
   - Tag as release (not pre-release)

**Creating a Release:**
```bash
# Update version in pyproject.toml
git add pyproject.toml
git commit -m "Bump version to 1.0.0"

# Create and push tag
git tag v1.0.0
git push origin main --tags
```

The workflow will automatically build and publish the release.

## Build Reports

Each workflow run produces a summary in the **Workflow Summary** tab showing:
- ✅ Test results (by Python version)
- ✅ Build status (by platform)
- ✅ Build artifact sizes
- ✅ Overall status

## Downloading Artifacts

**For development builds (main/develop branches):**
1. Go to Actions → Build & Test
2. Click the latest successful run
3. Scroll down to "Artifacts" section
4. Download the artifact for your platform

**For releases:**
1. Go to Releases
2. Click on the release version
3. Download the `.zip`, `.dmg`, or `.tar.gz` file

## Troubleshooting

### Build fails with "LibreOffice not found"
**Cause:** PDF output requires LibreOffice headless installation
**Fix:** Workflows install LibreOffice automatically. If it fails, check the build logs.

### Tests fail locally but pass in CI
**Cause:** Python version mismatch (CI tests 3.9, 3.11, 3.12)
**Fix:** Make sure you're testing on a compatible Python version

### Build artifacts are too large
**Cause:** PyInstaller bundles Python + all dependencies
**Normal sizes:**
- Windows: ~75-100 MB
- macOS: ~100-150 MB
- Linux: ~80-120 MB

### Release artifacts not created
**Cause:** Tag must match `v*` pattern (e.g., `v1.0.0`)
**Fix:** Use semantic versioning for tags

## Dependencies

The workflows assume:
- `pyproject.toml` with `[project.optional-dependencies] dev = [...]`
- Packaging scripts at `packaging/build_*.sh`
- Tests in `tests/` directory
- Source code in `src/verax/`

## Environment Variables

No special environment variables needed. GitHub Actions automatically provides:
- `GITHUB_TOKEN` — for releasing to GitHub
- `GITHUB_REF_NAME` — for version tagging
- `GITHUB_STEP_SUMMARY` — for workflow summaries

## Cost

GitHub Actions provides **free monthly limits**:
- 2,000 minutes/month for private repos
- Unlimited for public repos

Verax workflows typically use:
- ~30 minutes per push (test + build on 3 platforms)
- ~20 minutes per release

---

For more info, see:
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Verax Contributing Guide](../CONTRIBUTING.md) (if available)
