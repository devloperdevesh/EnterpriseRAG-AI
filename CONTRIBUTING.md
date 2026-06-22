# Contributing to EnterpriseRAG-AI

Thank you for contributing to EnterpriseRAG-AI.

This project focuses on scalable backend systems, observability-first infrastructure, distributed architectures, async workflows, and production-oriented AI engineering.

Please review the following guidelines before contributing.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Fork and Setup](#fork-and-setup)
- [Branch Naming](#branch-naming)
- [Development Workflow](#development-workflow)
- [Code Standards](#code-standards)
- [Testing](#testing)
- [Commit Messages](#commit-messages)
- [Pull Request Guidelines](#pull-request-guidelines)
- [GSSoC 2026 Contributors](#gssoc-2026-contributors)

---

## Prerequisites

Ensure you have the following installed:

- **Python 3.11+**
- **Docker** and **Docker Compose**
- **Git**
- **Node.js 18+** (for frontend changes)

---

## Fork and Setup

1. **Fork** this repository to your GitHub account.

2. **Clone** your fork:
   ```bash
   git clone https://github.com/<your-username>/EnterpriseRAG-AI.git
   cd EnterpriseRAG-AI
   ```

3. **Add the upstream remote:**
   ```bash
   git remote add upstream https://github.com/devloperdevesh/EnterpriseRAG-AI.git
   ```

4. **Create and activate a virtual environment:**
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS / Linux
   source .venv/bin/activate
   ```

5. **Install backend dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

6. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your values (DATABASE_URL, REDIS_URL, OPENAI_API_KEY, etc.)
   ```

7. **Start infrastructure services (PostgreSQL + Redis):**
   ```bash
   docker compose up -d
   ```

8. **Run the backend:**
   ```bash
   uvicorn app.main:app --reload
   ```

9. **Install and run the frontend (optional):**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

---

## Branch Naming

Use this format: `<type>/issue-<number>-<short-description>`

| Type | When to use |
|------|-------------|
| `feat/` | New feature |
| `fix/` | Bug fix |
| `docs/` | Documentation changes |
| `refactor/` | Code refactoring (no behaviour change) |
| `perf/` | Performance improvements |
| `test/` | Adding or fixing tests |
| `chore/` | Build process, config, or dependency updates |

Examples:

```
feat/issue-114-redis-request-coalescing
fix/issue-82-wrong-import-path-verify-token
docs/issue-87-expand-contributing-guide
```

---

## Development Workflow

1. **Sync your fork** before starting work:
   ```bash
   git fetch upstream
   git checkout main
   git merge upstream/main
   ```

2. **Create your feature branch:**
   ```bash
   git checkout -b feat/issue-<number>-<short-description>
   ```

3. **Make your changes**, following the code standards below.

4. **Run tests** to verify nothing is broken:
   ```bash
   pytest tests/ -v
   ```

5. **Commit** with a meaningful message (see [Commit Messages](#commit-messages)).

6. **Push** to your fork:
   ```bash
   git push origin feat/issue-<number>-<short-description>
   ```

7. **Open a Pull Request** against `devloperdevesh/EnterpriseRAG-AI:main`.

---

## Code Standards

### Python (Backend)

- Use **type hints** on all function signatures.
- Use **async/await** for all I/O-bound operations.
- Handle exceptions explicitly — never swallow errors silently.
- Use `from app.core.config import settings` for all configuration values.
- Avoid hardcoded secrets, URLs, or magic numbers.
- Prefer `logging` over `print()` in all non-test code.
- Follow the existing import order: stdlib → third-party → internal.

### TypeScript / React (Frontend)

- Use functional components with typed props.
- Avoid inline styles; prefer CSS modules or Tailwind utility classes.
- Name component files in PascalCase; utility files in camelCase.
- Keep components focused and composable.

---

## Testing

- All new backend features should include at least one corresponding test in `tests/`.
- Run the full suite before submitting a PR:
  ```bash
  pytest tests/ -v --tb=short
  ```
- Tests live under `tests/` and follow the pattern `test_<module>.py`.
- Use `conftest.py` for shared fixtures.
- For async tests, use `pytest-asyncio`.

---

## Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>(<scope>): <short summary>

[optional body]

[optional footer]
```

Examples:

```
feat(rag): add cosine similarity threshold for out-of-domain detection
fix(auth): remove duplicate create_access_token with hardcoded secret
docs(contributing): expand setup and branch naming guide
```

Types: `feat`, `fix`, `docs`, `refactor`, `perf`, `test`, `chore`

---

## Pull Request Guidelines

- Keep pull requests **focused** — one feature or fix per PR.
- Link the related issue in the PR body using `Closes #<issue-number>`.
- Fill out all sections of the PR template.
- Ensure CI checks pass before requesting review.
- Do not include unrelated changes or formatting-only diffs.
- Add documentation/comments where the code is non-obvious.
- Prefer minimal, well-justified dependency additions.

---

## GSSoC 2026 Contributors

If you are contributing as part of **GirlScript Summer of Code 2026**:

1. Only work on issues that have been **assigned to you** by a maintainer.
2. Comment on the issue requesting assignment before starting work.
3. Submit one PR per issue.
4. Do not submit duplicate PRs for issues already covered by open PRs.
5. PRs must follow all guidelines above to qualify for scoring.
6. Label application and scoring is handled by maintainers after review.

---

> For questions, open a Discussion or comment on the relevant issue. Please do not DM maintainers directly for contribution guidance.
