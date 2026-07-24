# Mavis Team Mode Skill — Makefile
# Common development tasks. Use `make help` to see all targets.
#
# This Makefile wraps the scripts/ directory. Prefer running scripts directly
# in CI; this is for human convenience.

# ---- Config ----
PYTHON ?= python3
SHELL := /bin/bash
SKILL_DIR := $(shell pwd)
ZCODE_SKILLS_DIR := $(HOME)/.zcode/skills
ZCODE_LINK := $(ZCODE_SKILLS_DIR)/mavis-team-mode
INSTALL_DIR := $(HOME)/mavis-team-mode-skill
REPO_URL ?= https://github.com/Qqapple1/Mavis-team-mode-skill.git
GIT_REF ?=

# ---- Help target ----
.PHONY: help
help: ## Show this help message
	@echo "Mavis Team Mode Skill — make targets:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
	  awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Environment:"
	@echo "  REPO_URL  Git URL (default: $(REPO_URL))"
	@echo "  GIT_REF   Git ref to pin (optional)"

# ---- Install / uninstall ----
.PHONY: install
install: ## Install skill to Zcode (~/.zcode/skills/mavis-team-mode)
	REPO_URL=$(REPO_URL) GIT_REF=$(GIT_REF) bash scripts/install.sh

.PHONY: uninstall
uninstall: ## Remove skill from Zcode and delete clone
	bash scripts/install.sh --uninstall

.PHONY: reinstall
reinstall: uninstall install ## Uninstall and reinstall

.PHONY: doctor
doctor: ## Diagnose current install state (no changes)
	bash scripts/install.sh --doctor

# ---- Validation ----
.PHONY: validate
validate: ## Run all skill format checks (23 checks)
	bash scripts/validate.sh

.PHONY: validate-yaml
validate-yaml: ## Run YAML frontmatter validation (15 files)
	$(PYTHON) scripts/validate_yaml.py

.PHONY: validate-all
validate-all: validate validate-yaml ## Run all validators

# ---- Lint ----
.PHONY: lint
lint: ## Run shellcheck + python -m py_compile on all files
	@command -v shellcheck >/dev/null || { echo "shellcheck not installed. Install: apt install shellcheck / brew install shellcheck"; exit 1; }
	shellcheck scripts/install.sh scripts/validate.sh scripts/package.sh
	@for f in $(shell find . -name "*.py" -not -path "./.git/*" -not -path "*/__pycache__/*"); do \
	  $(PYTHON) -m py_compile "$$f" || { echo "SYNTAX: $$f"; exit 1; }; \
	done
	@echo "Lint OK"

.PHONY: syntax
syntax: ## Check bash + python syntax only
	@for f in $(shell find . -name "*.sh" -not -path "./.git/*"); do \
	  bash -n "$$f" || { echo "SYNTAX: $$f"; exit 1; }; \
	done
	@for f in $(shell find . -name "*.py" -not -path "./.git/*"); do \
	  $(PYTHON) -m py_compile "$$f" || { echo "SYNTAX: $$f"; exit 1; }; \
	done
	@echo "Syntax OK"

# ---- Test ----
.PHONY: test
test: test-e2e ## Run end-to-end tests (requires prototype server)

.PHONY: test-e2e
test-e2e: ## Run 20 base e2e tests (requires server running)
	@if ! lsof -i :8765 >/dev/null 2>&1; then \
	  echo "Starting prototype server..."; \
	  cd examples/prototype-todo-app && $(PYTHON) server/server.py & echo $$! > /tmp/test-server.pid; \
	  sleep 2; \
	fi
	cd examples/prototype-todo-app && $(PYTHON) test_e2e.py
	@if [ -f /tmp/test-server.pid ]; then \
	  kill $$(cat /tmp/test-server.pid) 2>/dev/null || true; \
	  rm /tmp/test-server.pid; \
	fi

.PHONY: test-e2e-extended
test-e2e-extended: ## Run 23 extended e2e tests
	@if ! lsof -i :8765 >/dev/null 2>&1; then \
	  echo "Starting prototype server..."; \
	  cd examples/prototype-todo-app && $(PYTHON) server/server.py & echo $$! > /tmp/test-server.pid; \
	  sleep 2; \
	fi
	cd examples/prototype-todo-app && $(PYTHON) test_e2e_extended.py
	@if [ -f /tmp/test-server.pid ]; then \
	  kill $$(cat /tmp/test-server.pid) 2>/dev/null || true; \
	  rm /tmp/test-server.pid; \
	fi

.PHONY: test-e2e-advanced
test-e2e-advanced: ## Run 5 advanced e2e tests (slow client, idempotency, tags sort, health ISO ts, max length)
	@if ! lsof -i :8765 >/dev/null 2>&1; then \
	  echo "Starting prototype server..."; \
	  cd examples/prototype-todo-app && $(PYTHON) server/server.py & echo $$! > /tmp/test-server.pid; \
	  sleep 2; \
	fi
	cd examples/prototype-todo-app && $(PYTHON) test_e2e_advanced.py
	@if [ -f /tmp/test-server.pid ]; then \
	  kill $$(cat /tmp/test-server.pid) 2>/dev/null || true; \
	  rm /tmp/test-server.pid; \
	fi

.PHONY: test-all
test-all: validate-all syntax test-e2e test-e2e-extended test-e2e-advanced ## Run EVERYTHING

# ---- Prototype ----
.PHONY: prototype
prototype: ## Start the prototype server (foreground)
	cd examples/prototype-todo-app && $(PYTHON) server/server.py

.PHONY: prototype-bg
prototype-bg: ## Start the prototype server in background
	cd examples/prototype-todo-app && nohup $(PYTHON) server/server.py > /tmp/prototype-server.log 2>&1 &
	@echo "PID: $$!"
	@echo "Log: /tmp/prototype-server.log"
	@echo "Stop: pkill -f 'python3 server/server.py'"

.PHONY: prototype-stop
prototype-stop: ## Stop the prototype server
	-pkill -f "python3 server/server.py"
	@echo "Stopped"

# ---- Clean ----
.PHONY: clean-all
clean-all: clean prototype-stop uninstall clean-dist ## Clean everything (incl. install + server + dist)

# ---- Info ----
.PHONY: info
info: ## Show skill metadata
	@echo "Skill: mavis-team-mode"
	@echo "Version: $$(grep '^version:' SKILL.md | head -1 | awk '{print $$2}')"
	@echo "License: MIT"
	@echo "Files:   $$(find . -type f -not -path './.git/*' -not -path './dist/*' -not -path '*/__pycache__/*' -not -name '*.pyc' | wc -l | tr -d ' ')"
	@echo "Lines:   $$(find . -type f \( -name '*.md' -o -name '*.py' -o -name '*.sh' -o -name '*.html' -o -name '*.yml' \) -not -path './.git/*' -not -path './dist/*' -not -path '*/__pycache__/*' -not -name '*.pyc' -exec cat {} + | wc -l | tr -d ' ')"

.PHONY: stats
stats: ## Show file count by type
	@echo "Markdown: $$(find . -name '*.md' -not -path './.git/*' -not -path './dist/*' | wc -l | tr -d ' ')"
	@echo "Python:   $$(find . -name '*.py' -not -path './.git/*' -not -path '*/__pycache__/*' | wc -l | tr -d ' ')"
	@echo "Bash:     $$(find . -name '*.sh' -not -path './.git/*' | wc -l | tr -d ' ')"
	@echo "PowerShell: $$(find . -name '*.ps1' -not -path './.git/*' | wc -l | tr -d ' ')"
	@echo "YAML:     $$(find . -name '*.yml' -not -path './.git/*' | wc -l | tr -d ' ')"
	@echo "HTML:     $$(find . -name '*.html' -not -path './.git/*' | wc -l | tr -d ' ')"
	@echo "Other:    $$(find . -type f -not -path './.git/*' -not -path './dist/*' -not -path '*/__pycache__/*' -not -name '*.pyc' \( ! -name '*.md' -a ! -name '*.py' -a ! -name '*.sh' -a ! -name '*.ps1' -a ! -name '*.yml' -a ! -name '*.html' \) | wc -l | tr -d ' ')"

.PHONY: benchmark
benchmark: ## Run token cost benchmark (human-readable output)
	$(PYTHON) scripts/benchmark_tokens.py

.PHONY: benchmark-json
benchmark-json: ## Run token cost benchmark (JSON output)
	$(PYTHON) scripts/benchmark_tokens.py --json

# ---- Packaging ----
.PHONY: package
package: ## Build platform-specific archives to dist/
	bash scripts/package.sh

.PHONY: package-dry-run
package-dry-run: ## Show which files would go into each package (no write)
	bash scripts/package.sh --dry-run

.PHONY: clean-dist
clean-dist: ## Remove dist/ directory
	rm -rf dist/

.PHONY: clean
clean: ## Remove __pycache__ and other build artifacts
	find . -name "__pycache__" -type d -not -path "./.git/*" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -not -path "./.git/*" -delete 2>/dev/null || true
	find . -name "*.pyo" -not -path "./.git/*" -delete 2>/dev/null || true
	@echo "Cleaned"

# ---- Default ----
.DEFAULT_GOAL := help
