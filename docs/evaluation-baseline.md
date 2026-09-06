# WhyWrong classifier evaluation

- Provider: `deterministic`
- Evaluated: 2026-09-06
- Examples: 48
- Overall accuracy: **58.3%** (28/48)

## Results by label

| Expected label | Passed | Total | Accuracy |
|---|---:|---:|---:|
| `ambiguous` | 12 | 12 | 100.0% |
| `correct` | 2 | 12 | 16.7% |
| `gradient_misunderstanding` | 2 | 12 | 16.7% |
| `optimizer_confusion` | 12 | 12 | 100.0% |

## Errors

| Example | Expected | Predicted |
|---|---|---|
| `correct-02` | `correct` | `optimizer_confusion` |
| `correct-03` | `correct` | `optimizer_confusion` |
| `correct-04` | `correct` | `optimizer_confusion` |
| `correct-05` | `correct` | `optimizer_confusion` |
| `correct-06` | `correct` | `optimizer_confusion` |
| `correct-08` | `correct` | `optimizer_confusion` |
| `correct-09` | `correct` | `optimizer_confusion` |
| `correct-10` | `correct` | `optimizer_confusion` |
| `correct-11` | `correct` | `optimizer_confusion` |
| `correct-12` | `correct` | `optimizer_confusion` |
| `gradient-02` | `gradient_misunderstanding` | `optimizer_confusion` |
| `gradient-03` | `gradient_misunderstanding` | `optimizer_confusion` |
| `gradient-04` | `gradient_misunderstanding` | `optimizer_confusion` |
| `gradient-05` | `gradient_misunderstanding` | `optimizer_confusion` |
| `gradient-06` | `gradient_misunderstanding` | `optimizer_confusion` |
| `gradient-07` | `gradient_misunderstanding` | `optimizer_confusion` |
| `gradient-08` | `gradient_misunderstanding` | `optimizer_confusion` |
| `gradient-09` | `gradient_misunderstanding` | `optimizer_confusion` |
| `gradient-10` | `gradient_misunderstanding` | `optimizer_confusion` |
| `gradient-12` | `gradient_misunderstanding` | `optimizer_confusion` |

## Method

Correct answers must pass without diagnosis. Known misconception examples must rank the matching hypothesis first with a decisive margin. Ambiguous answers pass when the system asks a diagnostic probe instead of claiming the answer is correct.
