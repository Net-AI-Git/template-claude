---
paths:
  - "*/src/repositories/**/*"
---

# repositories/ — Layer Standards

> Which file an artifact goes in, where SQL lives and how `task_data` / `flow_id` travel are
> [`02-code-layout.md`](02-code-layout.md) Sections 1, 3 and 4. The `try/except` shape and every Splunk
> event are [`04-error-and-logging.md`](04-error-and-logging.md). This file carries only what is true of
> the repository layer and of nowhere else.

## Purpose
All external-system access. Three categories live here and are **never mixed** in one file: the shared
Oracle repository, the shared CRM repository, and one GPT repository per feature. A shared repository is
added when the first feature needs it. Optional vendor-client stubs ship as reusable examples —
`pinecone_repository.py`, `doci_repository.py`, `embeddings_repository.py` — delete any your service
does not use.

If a feature needs Oracle + CRM + GPT, the **service** coordinates between them — never the repositories
themselves.

---

## SECTION A — Oracle (`oracle_repository.py`)
- Single class `OracleRepository`, engine as a class-level attribute. All methods `@staticmethod`.
- Methods grouped by feature, new features appended at the bottom. Each method handles its own connection and commit.
- Imports: `os`, `dotenv`, `sqlalchemy` (`create_engine`, `text`, `Engine`), `SplunkRepository`.

## SECTION B — GPT (`gpt_<feature_name>_repository.py`)
- Class name `Gpt<FeatureName>Repository`. `AzureOpenAI` client as a class-level attribute — no factory, no dataclass, no `lru_cache`. All methods `@staticmethod`.
- The file opens with the header comment allowed by [`03-code-quality.md`](03-code-quality.md) Section 5. It carries the `task_data` keys the methods read and an example of the parsed output, including its empty form.
- Prompt text, model parameters and response handling are Section E.
- Imports: `os`, `httpx`, `AzureOpenAI`, `dotenv`, `SplunkRepository`, and the `<ResponseModel>` from `schemas/gpt_responses.py`.

## SECTION C — CRM (`crm_repository.py`)
- Single class `CrmRepository`, session and certificate as a class-level mechanism.
- Shared infra at the top of the file: `get_session`, `reset_session`, `resolve_cert_path`, `send_to_crm`.
- `@classmethod` for session-state methods; `@staticmethod` for stateless ones.
- Whether a feature gets its own method or the service calls `send_to_crm` inline is decided by the trivial-wrapper threshold in [`03-code-quality.md`](03-code-quality.md) Section 5.
- Imports: `os`, `ssl`, `tempfile`, `time`, `requests`, `urllib3`, `cryptography`, `dotenv`, `SplunkRepository`.

## SECTION D — General (every repository)
- **Duplication across repositories is correct.** Each owns its own client, engine or session, and the logic lives directly in its methods. Never factor a shared caller, base class or dataclass out of two repositories — simplicity beats DRY at this layer.

---

## SECTION E — Prompt Standards (apply when writing/modifying a GPT prompt)

### E.1 — Placement
- The prompt text is written inline in the method, directly in the `messages` list. No external prompt files, no YAML / JSON / Jinja2 / `string.Template`, no `prompts/` directory lookup, no `PromptManager`.
- Model parameters (`seed`, `top_p`, `temperature`) and the deployment name via `os.getenv()` go inline in the call — no `MODEL_PARAMS` constants.

### E.2 — Message Structure
- Use the exact list-of-objects format:
  ```python
  messages=[
      {"role": "system", "content": [{"type": "text", "text": "...prompt text..."}]},
      {"role": "user",   "content": [{"type": "text", "text": f"PROVIDED_OBJECT:\n{user_input}"}]},
  ]
  ```
- Never use the shorthand `"content": "string"` form.
- Multiple inputs → multiple `content` objects inside **one** user message, not multiple user messages.

### E.3 — System Prompt Text Format
- Wrap the entire prompt in `[INSTRUCTIONS]...[/INSTRUCTIONS]`.
- Section headers MUST appear in this exact order, exact casing, exact wording:
  1. `[DEFINITIONS]...[/DEFINITIONS]` — domain terms (see E.6).
  2. `ROLE:` — one sentence.
  3. `TASK:` — what to do.
  4. `RULES:` — numbered or bulleted strict rules.
  5. `CONFIDENCE SCORE (integer 1–5):` — scale definition (see E.7).
  6. `RESPONSE FORMAT:` — exact output spec.
  7. `[EXAMPLE 01]...[/EXAMPLE_01]` — concrete input/output (see E.4).
- Do NOT use variations like `STRICT RULES:`, `CRITICAL RULE:`, `ANSWER FORMAT:`, `RESPONSE:`.
- The system message is a **regular string** (`"""..."""`) — never an f-string. Only the user message uses an f-string for variable injection.
- The prompt's own indentation inside the triple-quoted string is part of the text the model reads. Never reflow, dedent or re-wrap it to satisfy a code-formatting rule.

### E.4 — Examples
- Use `[EXAMPLE 01]...[/EXAMPLE_01]` (two-digit numbered).
- Include at least one empty / edge-case example (e.g. `Answer: []`).
- Use realistic Hebrew data that mirrors production. Include the `"score"` field at varying confidence levels (including < 4).
- Examples MUST use real production data. Before inserting examples, **ask the user** where real examples can be found (test files, DB exports, Ground Truth files). Never invent example transcripts, intents, or outputs.

### E.5 — Reference Implementation
- Canonical example: [`reference/gpt_feature_name_repository.py`](reference/gpt_feature_name_repository.py:1).

### E.6 — Definitions Section
- When the prompt uses domain-specific terms the LLM cannot infer, include a `[DEFINITIONS]` block at the top of `[INSTRUCTIONS]`.
- Domain terms appear in **UPPERCASE** throughout the prompt (definitions, rules, task, examples).
- Only define terms specific to this domain — not common English words. Terms not in the definitions list MUST NOT be uppercased.

### E.7 — Mandatory Confidence Score
- Every prompt MUST instruct the LLM to return a **CONFIDENCE SCORE** (integer 1–5) per item, with the scale spelled out:
  ```
  CONFIDENCE SCORE (integer 1–5):
    5 = Certain — explicitly and clearly present in the input
    4 = High confidence — strong evidence supports this
    3 = Moderate — some evidence but ambiguous
    2 = Low — weak or indirect evidence
    1 = Very low — barely mentioned, speculative
  ```
- The response format MUST include a `"score"` field per result item.

### E.8 — Response Format & Parsing
- Every GPT method calls `client.beta.chat.completions.parse()` with `response_format=<ResponseModel>` and returns `response.choices[0].message.parsed`. Never `json.loads` of raw response text.
- The prompt states the output shape **and** `<ResponseModel>` enforces it — the two must describe the same structure. Specify exact keys and types, an inline example, and the empty-result form (`[]` or `{}`).
- Every prompt MUST explicitly forbid markdown wrappers:
  `- Do NOT wrap the response in markdown code blocks (no \`\`\`json or \`\`\`).`
- Plain-text responses: return `response.choices[0].message.content` from the same call, as-is, no parsing.

### E.9 — Confidence Scores Leave Here Unfiltered
- The repository returns the **full unfiltered list** with every score. Filtering against the threshold is the service's ([`11-services.md`](11-services.md)).

---

## Forbidden in this directory
- No cross-mixing: the Oracle file has no GPT/CRM code; CRM has no SQL/GPT; GPT has no SQL/CRM.
- No business logic anywhere in this directory — no threshold comparison, no conditional derivation, no data transformation. The service computes the value; the repository moves it in or out ready-made.
