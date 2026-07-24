# Security Policy

## Supported versions

| Version | Supported           |
|---------|---------------------|
| 1.3.x   | ✅ Active           |
| 1.2.x   | ✅ Active           |
| 1.1.x   | ⚠️ Critical fixes only |
| 1.0.x   | ❌ No longer supported |
| < 1.0   | ❌ No longer supported |

## Reporting a vulnerability

**Please do NOT file a public issue for security vulnerabilities.**

Use GitHub Security Advisories (private disclosure):
https://github.com/Qqapple1/Mavis-team-mode-skill/security/advisories/new

Include:
- Description of the vulnerability
- Steps to reproduce
- Affected version(s)
- Impact assessment
- Any known mitigations

We will:
- Acknowledge within 48 hours
- Provide an initial assessment within 7 days
- Issue a fix or mitigation plan within 30 days
- Credit you in the security advisory (unless you prefer anonymity)

## Threat model

This skill consists of:
1. **Markdown files** containing instructions for an AI agent
2. **A runnable Python prototype** that demonstrates the workflow
3. **Bash scripts** for installation/validation

### What this skill CAN do
- Instruct an AI agent to dispatch sub-agents
- Run a local HTTP server on 127.0.0.1 (mock Todo API)
- Clone a Git repository and create symlinks in $HOME

### What this skill CANNOT do
- Modify files outside the skill directory
- Make network requests without user consent
- Persist beyond a single session
- Access credentials or secrets (none are stored)

## Known limitations

The skill is a "best effort" recreation. Limitations:

- **No supply chain guarantees**: the skill instructs the LLM to dispatch
  sub-agents. If the LLM is manipulated via prompt injection, it could
  cause unexpected behavior. Use within a trusted environment.
- **No sandboxing**: the prototype server runs with your user's permissions.
  Don't run on shared systems.
- **No signing**: skills are not cryptographically signed. Verify sources
  before installing.

## Best practices for users

1. **Review the skill before installing**:
   ```bash
   git clone https://github.com/Qqapple1/Mavis-team-mode-skill
   less mavis-team-mode-skill/SKILL.md
   less mavis-team-mode-skill/agents/leader.md
   ```

2. **Pin to a specific version**:
   ```bash
   MAVIS_TEAM_REF=v1.3.8 bash scripts/install.sh
   ```

3. **Run with no network** when possible:
   ```bash
   # The prototype server defaults to 127.0.0.1 (no network exposure)
   cd examples/prototype-todo-app
   HOST=127.0.0.1 python3 server/server.py
   # Check: netstat -an | grep 8765 should show only 127.0.0.1, not 0.0.0.0
   ```

4. **Audit sub-agent outputs**: when a Worker sub-agent reports a result,
   spot-check before integrating into your final deliverable.

5. **Use a separate API key** for the skill (don't reuse your primary
   key for an experimental workflow).

## Reporting issues with the skill itself

For non-security bugs, use the standard GitHub issue tracker:
https://github.com/Qqapple1/Mavis-team-mode-skill/issues
