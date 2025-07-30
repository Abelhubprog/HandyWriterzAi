# Pricing Appendix

| Tier                | Alias we expose to Nodes | OpenRouter model slug            | Context | ¢ / 1 K in ↕ / out\*      | Primary role                         |
| ------------------- | ------------------------ | -------------------------------- | ------- | ------------------------- | ------------------------------------ |
| **Writer**          | `gemini-pro-25`          | `google/gemini-2.5-pro`          | **1 M** |  ≈ $7 / $21             | long‑form drafting, formatting       |
| **Research**        | `o3-reasoner`            | `openai/o3`                      | 200 K   |  $0.50 / $1.50          | reasoning, tool use, citations       |
|                     | `sonar-deep`             | `perplexity/sonar-deep-research` | 128 K   | \$0.20 / \$0.80 (+search) | exhaustive research queries          |
|                     | `kimi-k2`                | `moonshotai/kimi-k2`             | 131 K   | \~\$0.30 / \$1.20         | fallback MoE, code / tool calls      |
| **Evaluation / QA** | `claude4 -opus`            | `anthropic/claude-opus-4`        | 200 K   | \$15 / \$75               | rubric scoring, consensus judge      |
| **Rare**            | `grok‑4`                 | `x-ai/grok-4`                    | 256 K   | \$3 / \$15                | niche reasoning, parallel tool calls |
|                     | `claude 4-sonnet`        | `anthropic/claude-3-sonnet-20240229` | 200K    | $3 / $15                | research                             |

\* rough list‑prices; update `price_table.json` when OpenRouter changes.
