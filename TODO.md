# TODO

## Development Environment
- [x] Create a Dockerfile for consistent deployment and environment.
- [x] Use `uv` to manage Python versions and dependencies.
- [ ] Integrate CI/CD (e.g., GitHub Actions) for automation:
  - [x] Trigger: Tag push
  - [x] Build and push Docker image to Docker Hub
  - [ ] Auto Changelog
  - [x] Automatically deploy GitHub Pages

## Code Quality
- [x] API schema validation (pydantic).
- [ ] Code security checks (e.g., bandit).

## Testing and Documentation
- [x] Create a Restful API that complies with MCP standards.
- [x] Automate documentation generation (e.g., Sphinx or MkDocs).
- [ ] Automate unit tests (suggested: pytest).
- [ ] Code coverage reports (e.g., coverage.py).

## Improvements
- [x] Use `docker run` in MCP Server to simplify container startup.
