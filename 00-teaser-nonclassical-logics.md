# Teaser — Verifying LLM reasoning under EU AI Act Art. 13

A small slice of a separate, ongoing project. Shows the shape of the work and the empirical hook; methodology details, scoring functions, scenarios, and judge prompts are not included here.

## The empirical hook

Across a benchmark of 82 formal scenarios spanning seven non-classical logic systems (classical baseline, paraconsistent, intuitionistic, relevance, temporal LTL, deontic SDL, Dempster–Shafer evidential), one frontier model scores:

| Category                  | Accuracy | Mean stated confidence |
|---------------------------|---------:|-----------------------:|
| Classical baseline        |    41.1% |                  4.6/5 |
| Paraconsistent            |    36.9% |                  4.6/5 |
| Intuitionistic            |    31.0% |                  4.6/5 |
| Relevance                 |    29.8% |                  4.6/5 |
| Temporal                  |       0% |                  4.6/5 |
| Deontic                   |       0% |                  4.6/5 |
| Evidential combination    |       0% |                  4.6/5 |

Three categories at floor while confidence stays pinned at ceiling. The interesting bit is not "the model is wrong" — it is the **decoupling**. Under EU AI Act Art. 13 and GDPR Art. 22, a system that confidently explains an incorrect inference is, by construction, not providing a *meaningful* explanation. That is the gap the project addresses.

## The shape of the runner

Single illustrative slice — data model and prompt envelope. The scorer, the keyword taxonomies, the LLM-as-judge fallback, the aggregation, and the benchmark scenarios themselves are out of scope for this teaser.

```python
@dataclass
class ScenarioResult:
    scenario_id: str
    category: str
    logic: str
    domain: str
    difficulty: str
    model_output: str
    correct_answer: str
    classical_answer: str
    classical_fails: bool
    # Scored fields — filled by the scorer (not shown)
    agrees_with_correct: Optional[bool] = None
    agrees_with_classical: Optional[bool] = None
    flags_uncertainty: Optional[bool] = None
    flags_escalation: Optional[bool] = None
    score: Optional[float] = None


SYSTEM_PROMPT = """You are a reasoning AI assistant.
Answer the following question based ONLY on the premises provided.
Be explicit about uncertainty. If you cannot determine a definitive answer,
say so clearly. Do not use outside knowledge beyond what is given."""


def build_prompt(scenario: dict) -> str:
    premises = "\n".join(f"- {p}" for p in scenario["premises"])
    return (
        f"CONTEXT: {scenario['context']}\n\n"
        f"PREMISES:\n{premises}\n\n"
        f"QUESTION: {scenario['query']}\n\n"
        f"Provide your answer and reasoning:"
    )
```

Reproducibility note: generation is run with `do_sample=False` for deterministic outputs; runs are pinned per model revision; results are stored per-scenario before aggregation so any failure can be inspected without re-running the model.

## Metrics taxonomy

Four headline metrics. Definitions only — implementation withheld.

| Metric                    | What it measures |
|---------------------------|------------------|
| `overall_agreement`       | Fraction of scenarios where the model's answer agrees with the formally correct one. |
| `classical_failure_rate`  | On scenarios where classical logic gives the wrong answer, how often the model takes the classical trap. |
| `uncertainty_calibration` | On scenarios whose correct answer is `UNKNOWN` / `NOT PROVABLE`, how often the model actually flags uncertainty instead of guessing. |
| `escalation_rate`         | On scenarios that require human escalation, how often the model produces an escalation signal. |

## Why this is in the same folder as three JSON-lint prompts

The same design discipline runs through both:

- **Quote, don't act.** The eform prompts treat hostile-shaped `field_guidance` ("ignore previous instructions…") as data inside a `code:"INSTRUCTION_LIKE_TEXT"` finding, never as input to themselves. The non-classical pipeline applies the same rule when a model under test outputs role-claim text — it goes into the evidence column, not the next stage.
- **Confidence is not correctness.** Prompt 3's `confidence` field on every semantic finding is the operational version of the same idea: a flagged `OPTION_LABEL_INCOHERENT` at `low` confidence is not the same artifact as one at `high`, and the downstream operator gets to triage on that.
- **Right tool per layer.** Structural checks run on Haiku; graph reasoning on Sonnet; bilingual nuance on Opus. The non-classical work makes the same call empirically: scale helps on relevance and paraconsistent, plateaus on temporal and deontic. Buying a larger model is not a substitute for a verifier.

## Where the rest lives

Public proof-of-concept repository — `github.com/th00masml/nonclassical_logics`.

Working title for the framework: **Formalis**, a 9-stage verification pipeline that wraps an LLM agent and routes each decision through verifiers tied to specific non-classical logics. Not all stages are open. What is open is the benchmark runner skeleton (sketched above), the metric definitions, and a subset of the 82 scenarios. The verifier-per-logic implementations, the LLM-as-judge prompts, and the scaled benchmark (target 3,500+ scenarios) are held back pending publication.

## Sources

- Regulation (EU) 2024/1689 (AI Act), Art. 13 — https://eur-lex.europa.eu/eli/reg/2024/1689/oj
- Regulation (EU) 2016/679 (GDPR), Art. 22 — https://eur-lex.europa.eu/eli/reg/2016/679/oj
- Priest, *In Contradiction* (paraconsistent LP, foundational) — https://global.oup.com/academic/product/in-contradiction-9780199263301
- Pnueli, "The Temporal Logic of Programs" (LTL, foundational) — https://doi.org/10.1109/SFCS.1977.32
- Shafer, *A Mathematical Theory of Evidence* (Dempster–Shafer) — https://press.princeton.edu/books/paperback/9780691100425/a-mathematical-theory-of-evidence
- van Ditmarsch, van der Hoek, Kooi, *Dynamic Epistemic Logic* — https://link.springer.com/book/10.1007/978-1-4020-5839-4
- OWASP Top 10 for LLM Applications, LLM01 (Prompt Injection) — https://genai.owasp.org/llm-top-10/

As of May 2026. Regulatory cites are stable; foundational references are textbook-canonical. Empirical numbers above are from a frozen run on Claude Sonnet 4.5 over 82 scenarios; expansion runs in progress and unpublished.
