# Install, Debug and Validate an MCP Server (GitHub MCP Registry + VS Code)

This guide installs the **GitHub MCP server** from the GitHub MCP Registry into VS Code, shows how to
read and debug `mcp.json`, and how to confirm the server works.

Verified against official docs on 2026-10-15 (VS Code 1.141.0, Linux):

- [Add and manage MCP servers in VS Code](https://code.visualstudio.com/docs/agent-customization/mcp-servers)
- [MCP configuration reference](https://code.visualstudio.com/docs/agents/reference/mcp-configuration)
- [GitHub Docs: Setting up the GitHub MCP Server](https://docs.github.com/en/copilot/how-tos/provide-context/use-mcp/set-up-the-github-mcp-server)
- [github/github-mcp-server](https://github.com/github/github-mcp-server) and its
  [remote server docs](https://github.com/github/github-mcp-server/blob/main/docs/remote-server.md)
- [GitHub MCP Registry](https://github.com/mcp)

> Security: never hardcode tokens in `mcp.json`. Use `${input:...}` variables. Do not commit tokens or read `.env` files for this.

---

## 1. Prerequisites

| Requirement | Notes |
| --- | --- |
| VS Code 1.101 or later | Needed for remote MCP and OAuth. Check with `code --version`. |
| GitHub account signed in to VS Code | Required for OAuth. |
| Copilot policy | On Copilot Business or Enterprise, the **"MCP servers in Copilot"** policy must be enabled by an admin. |
| Docker (local server only) | Only for the local option in section 3.3. Image: `ghcr.io/github/github-mcp-server`. |

---

## 2. Install from the GitHub MCP Registry (recommended)

The Extensions view `@mcp` gallery is backed by the GitHub MCP Registry.

1. Open Extensions: `Ctrl+Shift+X`.
2. Search `@mcp github`.
3. Select **GitHub** (publisher `github`) and review the details page.
4. Choose where to install:
   - **Install**: user profile (all workspaces).
   - Right-click, **Install in Workspace**: writes `.vscode/mcp.json` in this repo.
5. Confirm the trust prompt when VS Code asks to start the server.
6. Complete the browser OAuth sign-in if prompted.

Alternatives:

- Command Palette (`Ctrl+Shift+P`): **MCP: Browse MCP Servers** opens the same gallery.
- Browse <https://github.com/mcp>, open a server page, and use **Install** for VS Code.
- Chat: Open Customizations, then **MCP Servers**, then **Add Server**, then **Browse MCP Servers**.

---

## 3. mcp.json

### 3.1 File locations and formats

| Scope | File | Top-level key | When to use |
| --- | --- | --- | --- |
| Workspace (VS Code format) | `.vscode/mcp.json` | `servers` | VS Code features: `inputs`, `envFile`, `dev`, sandbox |
| Workspace (portable) | `.mcp.json` | `mcpServers` | Shared with other Copilot tools. Stdio and HTTP only, no `${input:...}` |
| User profile | run **MCP: Open User Configuration** | `servers` | Personal, per profile |
| User (Copilot) | `~/.copilot/mcp-config.json` (or `$COPILOT_HOME/mcp-config.json`) | `mcpServers` | Personal, portable |

Open from the Command Palette: **MCP: Open Workspace Folder MCP Configuration**.

### 3.2 Remote GitHub server, OAuth (no token to manage)

`.vscode/mcp.json`:

```json
{
  "servers": {
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/"
    }
  }
}
```

### 3.3 Remote server with a PAT, or local Docker server

Remote with a PAT (prompted once, stored securely, hidden input):

```json
{
  "servers": {
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/",
      "headers": {
        "Authorization": "Bearer ${input:github_mcp_pat}"
      }
    }
  },
  "inputs": [
    {
      "type": "promptString",
      "id": "github_mcp_pat",
      "description": "GitHub Personal Access Token",
      "password": true
    }
  ]
}
```

Local server in Docker with a PAT:

```json
{
  "servers": {
    "github": {
      "type": "stdio",
      "command": "docker",
      "args": ["run", "-i", "--rm", "-e", "GITHUB_PERSONAL_ACCESS_TOKEN", "ghcr.io/github/github-mcp-server"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${input:github_token}"
      }
    }
  },
  "inputs": [
    {
      "type": "promptString",
      "id": "github_token",
      "description": "GitHub Personal Access Token",
      "password": true
    }
  ]
}
```

Do not use `-d` (detach) with Docker stdio servers. The server must run in the foreground.

### 3.4 Limit the exposed tools (optional, remote server)

Fewer tools means better tool selection and less context. Use headers:

```json
{
  "servers": {
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/",
      "headers": {
        "X-MCP-Toolsets": "repos,issues,pull_requests",
        "X-MCP-Readonly": "true"
      }
    }
  }
}
```

Or use URL paths: `/readonly`, `/x/all`, `/x/issues/readonly`. Notes from the official docs:

- Default toolsets: `context`, `repos`, `issues`, `pull_requests`, `users`.
- Unknown toolset names in `X-MCP-Toolsets` are silently ignored.
- Unknown tool names in `X-MCP-Tools` stop the server from starting.
- `/x/{toolset}` takes a single toolset only. Use the header for several.

### 3.5 Field reference (VS Code format)

| Server type | Required | Optional |
| --- | --- | --- |
| `stdio` | `type`, `command` | `args`, `cwd`, `env`, `envFile`, `dev`, `sandboxEnabled`, `sandbox` |
| `http` / `sse` | `type`, `url` | `headers`, `oauth` |

- Top-level keys: `servers` (required), `inputs` (optional), `sandbox` (optional, macOS and Linux only).
- Server names: camelCase, no spaces or special characters, unique (for example `github`).
- Input types: `promptString`, `pickString`, `command`. Each needs `type` and `id`.
- VS Code tries HTTP Stream first, then falls back to SSE.

---

## 4. Validate that the server works

### Step 1: Static validation of mcp.json

- Open the file in VS Code. IntelliSense underlines schema errors (unknown keys, missing `type`/`url`/`command`).
- Check the **Problems** panel (`Ctrl+Shift+M`).
- Confirm it parses (comments are allowed by VS Code, but plain JSON is easiest to check):

```bash
python3 -m json.tool .vscode/mcp.json > /dev/null && echo "mcp.json: valid JSON"
```

- Confirm the shape:

```bash
python3 - <<'EOF'
import json, pathlib
cfg = json.loads(pathlib.Path(".vscode/mcp.json").read_text())
assert "servers" in cfg, "top-level 'servers' missing (use 'mcpServers' only in .mcp.json)"
for name, s in cfg["servers"].items():
    t = s.get("type", "stdio" if "command" in s else "http")
    need = ["command"] if t == "stdio" else ["url"]
    missing = [k for k in need if k not in s]
    assert not missing, f"{name}: missing {missing}"
    print(f"{name}: type={t} OK")
EOF
```

### Step 2: Confirm the server is registered and running

1. `Ctrl+Shift+P`, then **MCP: List Servers**. `github` must be listed.
2. Select it. Available actions: **Start**, **Stop**, **Restart**, **Show Output**, **Disable**.
3. Choose **Start** (or **Restart** after config edits). The mcp.json editor also shows inline
   **Start | Restart | Stop** code lenses above each server.
4. A healthy server shows a running state with a tool count, for example `Discovered N tools` in the output.

### Step 3: Confirm the tools are available in chat

1. Open Chat (`Ctrl+Alt+I`) in **Agent** mode.
2. Click **Configure Tools** and confirm the `github` tools are listed and enabled.
3. Run a read-only prompt, for example:

   ```text
   Using the GitHub MCP server, who am I (get_me) and list my 5 most recently updated repositories.
   ```

4. Approve the tool call. A real response with your GitHub username means auth, transport and tools all work.

### Step 4: Endpoint reachability check (no credentials needed)

An unauthenticated request must return **401 with an OAuth challenge**. That proves the endpoint is
up and the URL is right.

```bash
curl -sS -o /dev/null -D - -X POST https://api.githubcopilot.com/mcp/ \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"probe","version":"0"}}}' \
  | grep -iE '^(HTTP|www-authenticate)'
```

Observed result when this guide was validated:

```text
HTTP/2 401
www-authenticate: Bearer error="invalid_request", error_description="No access token was provided in this request", resource_metadata="https://api.githubcopilot.com/.well-known/oauth-protected-resource/mcp/"
```

If this returns a different status, a network, proxy or DNS problem exists before VS Code is involved.

### Step 5: PAT authentication check (optional)

Export the token in your shell for this one command (do not write it to a file):

```bash
read -rs GITHUB_MCP_PAT && export GITHUB_MCP_PAT
curl -sS -o /dev/null -w '%{http_code}\n' -X POST https://api.githubcopilot.com/mcp/ \
  -H "Authorization: Bearer $GITHUB_MCP_PAT" \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"probe","version":"0"}}}'
unset GITHUB_MCP_PAT
```

`200` means the token is accepted. `401` or `403` means a bad, expired or under-scoped token, or an organization PAT policy.

---

## 5. Debug

### 5.1 View logs

Any of these opens the server's Output channel:

- **MCP: List Servers**, select the server, then **Show Output**.
- Select the error indicator in the Chat view, then **Show Output**.
- Chat: Open Customizations, then **MCP Servers**, then the server's `...` menu, then **Show Output**.
- Click the **Show Output** code lens in `mcp.json`.

### 5.2 Troubleshooting checklist

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Server not listed in **MCP: List Servers** | Wrong file, wrong top-level key, or invalid JSON | `.vscode/mcp.json` uses `servers`; `.mcp.json` uses `mcpServers`. Run Step 1. |
| Server never starts in a workspace | Workspace is in Restricted Mode | Trust the workspace. Workspace MCP config is blocked in restricted mode. |
| Trust prompt dismissed, no tools | Server not trusted | **MCP: Reset Trust**, then start the server and accept. |
| `401 Unauthorized` / auth loop | OAuth not completed, bad or expired PAT | Restart the server and sign in again. For a PAT, create a new token and verify it with Step 5. |
| `403 Forbidden` / tools fail | PAT scopes too narrow, or org policy | Grant the needed scopes. For orgs, enable "MCP servers in Copilot" and check PAT and OAuth app policies. |
| Enterprise Managed User cannot use PAT | PATs disabled by enterprise | Use OAuth, or ask an admin. |
| GitHub Enterprise Cloud (ghe.com) | Wrong URL | Use `https://copilot-api.<subdomain>.ghe.com/mcp`. For OAuth also set VS Code to your GHE instance. GHES has no remote server; use the local server with `GITHUB_HOST`. |
| Docker server fails on start | Docker not running, image pull denied, `-d` used | Start Docker. If the pull fails, run `docker logout ghcr.io` (an expired token can break public pulls). Remove `-d`. |
| `command not found` (stdio) | Command not on PATH for VS Code | Use the full path in `command`. |
| Server fails at startup after adding `X-MCP-Tools` | Invalid tool name | Use exact names (for example `get_file_contents`). Prefer `X-MCP-Toolsets`. |
| Tools list stale after server update | Cached tool list | **MCP: Reset Cached Tools**. |
| Tools missing in chat although server runs | Tools toggled off or too many tools | **Configure Tools** in the chat input and enable them. Narrow with toolsets. |
| Server disabled | Disabled globally or per workspace | **MCP: List Servers**, then **Enable**. |
| `${input:...}` server not visible to Copilot harness session | `.vscode/mcp.json` entries needing interactive input are not forwarded | Use a PAT-free OAuth config, or define the server where the harness reads it (`.mcp.json` / `~/.copilot/mcp-config.json`) without inputs. |
| Org-managed access blocked | `chat.mcp.access` policy | Ask an admin to allow the server. |

### 5.3 Useful commands

| Command | Purpose |
| --- | --- |
| MCP: List Servers | Start, stop, restart, show output, enable, disable |
| MCP: Show Installed Servers | List installed servers |
| MCP: Open Workspace Folder MCP Configuration | Open `.vscode/mcp.json` |
| MCP: Open User Configuration | Open user-profile `mcp.json` |
| MCP: Reset Cached Tools | Clear cached tool lists |
| MCP: Reset Trust | Re-prompt for server trust |
| MCP: Browse Resources | Browse resources exposed by servers |

### 5.4 Debugging a server you are developing

Add a `dev` block to a stdio server to restart on file change and attach a debugger (Node.js and Python):

```json
{
  "servers": {
    "myServer": {
      "type": "stdio",
      "command": "node",
      "args": ["${workspaceFolder}/server.js"],
      "dev": { "watch": "${workspaceFolder}/**/*.js" }
    }
  }
}
```

See the [MCP development mode guide](https://code.visualstudio.com/api/extension-guides/ai/mcp#mcp-development-mode-in-vs-code).

---

## 6. Validation checklist

- [ ] `code --version` is 1.101 or later.
- [ ] `mcp.json` parses and shows no Problems.
- [ ] **MCP: List Servers** shows `github`, and Start succeeds.
- [ ] Output channel shows tools discovered, with no auth errors.
- [ ] Unauthenticated `curl` returns `401` with `www-authenticate` (Step 4).
- [ ] Agent mode lists the `github` tools and a read-only prompt returns real data.
- [ ] No tokens appear in `mcp.json`; secrets use `${input:...}`.
