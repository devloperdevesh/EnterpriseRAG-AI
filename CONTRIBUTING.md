# Contributing to EnterpriseRAG-AI

Thank you for contributing to EnterpriseRAG-AI.

This project focuses on scalable backend systems, observability-first infrastructure, distributed architectures, async workflows, and production-oriented AI engineering.

Please review the following guidelines before contributing.

---

# Contribution Guidelines

* Keep pull requests focused, modular, and maintainable
* Follow the existing project structure and architecture patterns
* Avoid unnecessary formatting-only changes
* Write clean, readable, and production-oriented code
* Validate changes locally before submitting a pull request
* Add documentation/comments where necessary
* Prefer minimal and well-justified dependency additions
* Keep backend and frontend responsibilities cleanly separated

---

# Pull Request Expectations

* One feature/fix per pull request
* Link the related issue whenever applicable
* Clearly explain the implementation approach
* Include testing or validation details
* Keep implementations modular and architecture-aligned
* Avoid low-quality or unreviewed AI-generated code submissions

---

# Review Priorities

Pull requests are primarily reviewed based on:

* maintainability
* observability clarity
* runtime stability
* modular architecture
* async workflow consistency
* minimal performance overhead
* scalability alignment

---

# Local Development

## Docker Environment

```bash
docker compose up
```

## Backend Validation

```bash
pytest
```

## Frontend Development

```bash
npm run dev
```

---

# Tech Stack

* FastAPI
* Redis
* Kafka
* FAISS
* React
* TypeScript
* Docker
* Prometheus
* Grafana
* AsyncIO

---

# Engineering Philosophy

```txt
Build infrastructure that is scalable,
observable, maintainable,
and production-oriented.
```
