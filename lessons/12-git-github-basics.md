# Lesson 12 · Git and GitHub basics (for complete beginners)

> **Goal:** save versions of your bot safely, undo mistakes, and put your capstone on GitHub so recruiters can see it.

## First, what are they?

- **Git** is a program on your PC that takes **snapshots** of a folder. Each snapshot (a *commit*) has a message like "Add retries". You can see what changed, and go back to any snapshot. Think of it as *version history* for your whole project, like SharePoint versions but for code and much more powerful.
- **GitHub** is a website that stores a copy of your Git project online: a backup, a portfolio, and a way to work with others. Git works fine without GitHub; GitHub needs Git.

## PAD / Power Platform → Git mapping

| What you know | Git / GitHub |
|---|---|
| Saving a new version of a flow | `git commit -m "message"` |
| Flow version history | `git log --oneline` |
| Comparing two versions | `git diff` |
| Solutions / exporting a flow to share | `git push` to GitHub |
| Importing a flow on another PC | `git clone <url>` |
| Copy of a flow to try something risky ("Flow - test") | a **branch**: `git switch -c try-new-idea` |
| Merging the test copy back | `git merge try-new-idea` |
| Files you never export (connections, secrets) | `.gitignore` |

## 1. Install and introduce yourself (once)

1. Download Git for Windows from <https://git-scm.com/download/win> and install with the default options.
2. Open a new terminal:

```bat
git --version
git config --global user.name "Harshal Lihitkar"
git config --global user.email "you@example.com"
git config --global init.defaultBranch main
```

Use the same email as your GitHub account (GitHub can hide it: *Settings → Emails → Keep my email private* gives you a `...@users.noreply.github.com` address).

## 2. The everyday loop: status → add → commit

```bat
cd capstone
git init                      # once per project: start tracking this folder
git status                    # what's changed?  (run this ALL the time)
git add .                     # put all changes in the "next snapshot" basket
git commit -m "First version of license checker"
```

Then, every time you finish a small piece of work:

```bat
git status
git diff                      # see exactly which lines changed
git add .
git commit -m "Add retry with back-off"
git log --oneline             # your history
```

Good commit messages say **what and why** in a few words: *"Retry lookups on 503 errors"*, not *"changes"*.

## 3. `.gitignore`: what must never go in

Create a file named `.gitignore` in the project folder:

```
.venv/
__pycache__/
output/
*.log
auth_state.json
```

- `.venv/` is huge and can be rebuilt with `pip install -r requirements.txt`.
- `output/`, logs and screenshots are results, not code. In real work they may contain **patient/provider data (PHI/PII)**.
- `auth_state.json` is a logged-in session: as good as a password.
- **Never commit real passwords, OTP secrets or client data.** If you do by accident, change the password; deleting the file later doesn't remove it from history.

## 4. Undo buttons

| Situation | Command |
|---|---|
| Throw away changes to one file since the last commit | `git restore license_checker.py` |
| I ran `git add` on the wrong file | `git restore --staged secrets.txt` |
| Fix the message of the last commit (not pushed yet) | `git commit --amend -m "Better message"` |
| Undo a commit that's already on GitHub, safely | `git revert <commit-id>` (adds a new "undo" commit) |

## 5. Branches: try ideas safely

```bat
git switch -c feature/excel-report     # new branch, switch to it
...edit, add, commit...
git switch main                        # back to the safe version
git merge feature/excel-report         # bring the work in
```

## 6. Put the capstone on GitHub (when you're ready)

> Don't publish until you've reviewed everything (see the checklist below).

1. Create a free account at <https://github.com> and turn on two-factor authentication.
2. Click **New repository**, name it `license-lookup-checker`, keep it **empty** (no README; you already have one), click *Create*.
3. GitHub shows commands; they look like:

```bat
git remote add origin https://github.com/<your-username>/license-lookup-checker.git
git push -u origin main
```

The first push opens a browser window to sign in (Git Credential Manager handles it on Windows). After that, publishing new work is just `git push`.

### Bonus: host the practice portal on GitHub Pages

Push `practice-portal/` as its own repo, then *Settings → Pages → Deploy from branch → main / (root)*. A minute later it's live at `https://<you>.github.io/<repo>/`, and every script works against it with `set BASE_URL=https://<you>.github.io/<repo>`.

### Pre-publish checklist

- [ ] `git status` is clean and `git ls-files` shows no `output/`, `.venv/`, `.log` or `auth_state.json`
- [ ] No real names, NPIs, passwords or company portal URLs anywhere (search: `git grep -i password`)
- [ ] README explains the problem, how to run it, and shows sample output
- [ ] `pip install -r requirements.txt` + the run command works in a fresh folder

## Exercises

1. In a practice folder: `git init`, create a script and a `.gitignore` that ignores `output/`, commit, and prove with `git ls-files` that `output/` isn't tracked.
2. Change the script, look at `git diff`, commit again, and see 2 commits in `git log --oneline`.
3. Create a branch, add a file, commit, switch back to `main`, merge, and view `git log --oneline --graph`.

Solution: [`solutions/12_git_basics.py`](../solutions/12_git_basics.py) runs all three exercises automatically in a throw-away temp folder (nothing is uploaded), printing each command so you can follow along. Then type them yourself. Muscle memory matters.
