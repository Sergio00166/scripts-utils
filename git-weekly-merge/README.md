Here’s a polished **README.md** draft for your tool, based on the description you provided:

---

# 🗂️ Git Weekly Merge

A Python utility to clean up messy commit histories by **merging commits per ISO week** into a new branch.  
Each weekly commit is labeled with its week (`YYYY-Www`) and contains a deduplicated list of commit titles from that week.

---

## ✨ Features
- Creates a new branch with commits grouped by ISO week.
- Weekly commit subject: `YYYY-Www` (e.g., `2025-W47`).
- Weekly commit body: unique first-line commit messages, deduplicated.
- Supports merging from a single branch or all branches.
- Timezone options: UTC or local.

---

## 📦 Installation
Clone the repository and ensure you have Python 3 installed:

```bash
git clone https://github.com/yourusername/git-weekly-merge.git
cd git-weekly-merge
```

---

## 🚀 Usage

```bash
python3 weekly_merge.py [--branch BRANCH | --all] [--out OUT_BRANCH] [--tz {utc,local}]
```

### Options
| Option | Description | Default |
|--------|-------------|---------|
| `--branch BRANCH` | Source branch to merge commits from | Current HEAD |
| `--all` | Merge commits from all branches | – |
| `--out OUT_BRANCH` | Output branch name | `weekly-merged` |
| `--tz {utc,local}` | Timezone for week calculation | `utc` |

---

## 🧑‍💻 Examples

- Merge commits from the current branch into weekly bundles:
  ```bash
  python3 weekly_merge.py
  ```

- Merge commits from a specific branch:
  ```bash
  python3 weekly_merge.py --branch develop --out weekly-develop
  ```

- Merge commits from all branches, using local timezone:
  ```bash
  python3 weekly_merge.py --all --tz local
  ```

---

## 📖 Why?
When your repo has **too many small commits** (e.g., 40 commits with minimal changes), this tool helps you:
- Simplify history
- Improve readability
- Create clean weekly summaries

