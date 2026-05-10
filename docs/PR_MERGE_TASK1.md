# Merge `task-1` into `main` via Pull Request

Goal: integrate Task 1 on `main` with review, **before** opening long-lived Task 2 work.

## On GitHub (recommended)

1. Push **`task-1`** if needed:  
   `git push -u origin task-1`
2. Open GitHub → **Pull requests → New pull request**  
   - **base:** `main`  
   - **compare:** `task-1`
3. Add a short description (EDA notebook, README, CI, sample data checks).
4. Merge after CI green (and optional review).

If the GitHub CLI is authenticated:

```bash
gh pr create --base main --head task-1 --title "Task 1: Financial news EDA" --body "EDA notebook, data docs, pytest smoke checks."
```

## Local fast-forward preview (does not replace a PR)

```bash
git fetch origin
git checkout main
git merge --no-ff task-1 -m "Merge task-1: EDA and documentation"
git push origin main
```

Use this only when a PR is impractical—teams usually still mirror the merge on GitHub for traceability.
