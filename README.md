# Claude Code — AWS Bedrock Connection

This directory configures [Claude Code](https://docs.anthropic.com/en/docs/claude-code) to run Anthropic Claude models through **AWS Bedrock** instead of the direct Anthropic API.

> Changing anything under `rules/`, `skills/` or `output-styles/`? Read two files first:
> [`PORTABILITY.md`](PORTABILITY.md) — this directory is its own repository and must name no directory
> of the workspace it is cloned into — and [`prompt-authoring.md`](prompt-authoring.md), the writing
> standard every prompt here follows.

## Configuration

The connection is defined in `settings.json`, which **must** be placed in the `.claude` folder inside your user home directory (not in the project):

- **Windows:** `C:\Users\<your-username>\.claude\settings.json`
- **macOS / Linux:** `~/.claude/settings.json`

It defines the following variables:

| Variable | Value | Purpose |
| --- | --- | --- |
| `CLAUDE_CODE_USE_BEDROCK` | `1` | Route all Claude Code requests through AWS Bedrock. |
| `AWS_REGION` | `eu-west-1` | Bedrock region the model is served from. |
| `ANTHROPIC_MODEL` | `eu.anthropic.claude-opus-5[1m]` | Bedrock inference profile / model ID to use. The `[1m]` suffix pins the 1M-token context window, which Claude Code applies only when a manually set model asks for it. |
| `NODE_TLS_REJECT_UNAUTHORIZED` | `0` | Disable TLS certificate verification (for corporate proxy / SSL inspection). |
| `NO_PROXY` | `*` | Bypass proxy for all hosts. |

## Prerequisite — AWS Credentials

Claude Code authenticates to Bedrock using the standard AWS credential chain. You **must** provide your AWS credentials in the `.aws` folder inside your user home directory.

- **Windows:** `C:\Users\<your-username>\.aws\`
- **macOS / Linux:** `~/.aws/`

Create (or update) these two files:

**`~/.aws/credentials`**

```ini
[default]
aws_access_key_id = YOUR_ACCESS_KEY_ID
aws_secret_access_key = YOUR_SECRET_ACCESS_KEY
aws_session_token = YOUR_SESSION_TOKEN
```

**`~/.aws/config`**

```ini
[default]
region = eu-west-1
```

> The credentials file is **never** committed to the repository — keep it only in your user folder. The `region` in `settings.json` takes precedence for Claude Code, but keeping it consistent in `~/.aws/config` avoids surprises with other AWS tools.

## Requirements

- An AWS account with **Amazon Bedrock** access enabled in `eu-west-1`.
- Model access granted for the Claude Opus model referenced by `ANTHROPIC_MODEL`. Confirm the profile exists in your region with `aws bedrock list-inference-profiles` before pinning it.
- IAM permissions to invoke Bedrock (e.g. `bedrock:InvokeModel`, `bedrock:InvokeModelWithResponseStream`).

## Verify the Connection

After placing your credentials in `~/.aws/`, confirm they resolve:

```bash
aws sts get-caller-identity
```

Then start Claude Code — it will pick up `~/.claude/settings.json` from your user home directory automatically and route requests through Bedrock.
