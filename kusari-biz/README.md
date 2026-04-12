```
░█░█░█░█░█▀▀░█▀█░█▀▄░▀█▀░░░░░█▀▄░▀█▀░▀▀█
░█▀▄░█░█░▀▀█░█▀█░█▀▄░░█░░▄▄▄░█▀▄░░█░░▄▀░
░▀░▀░▀▀▀░▀▀▀░▀░▀░▀░▀░▀▀▀░░░░░▀▀░░▀▀▀░▀▀▀
```

# kusari-biz

Business evaluation tools. Assess ideas, product plans, and features through a panel of investor personas.

## Commands

### /evaluate

```
/evaluate <idea description or file path>
```

Evaluates a business idea, product plan, or feature through a panel of seven investor personas running in parallel. Each persona applies a distinct investment philosophy and returns a structured assessment.

Argument is either inline text describing the idea or a path to a file containing it. Before launching the panel, the command checks for missing context (stage, constraints, target market) and asks in a single batch.

Investor personas:

| Persona | Core Lens |
|---------|-----------|
| Paul Graham | Founder quality, organic demand, simplicity |
| Peter Thiel | Monopoly, contrarian truth, definite plan |
| Sam Altman | Scale ceiling, ambition, timing |
| Marc Andreessen | Market size, distribution, technology waves |
| Naval Ravikant | Leverage, specific knowledge, permissionless scale |
| Balaji Srinivasan | Regulatory risk, tech curves, global-first |
| Patrick Collison | Infrastructure, developer experience, patience |

Each investor returns: verdict (invest/pass/conditional), conviction level, bull case, bear case, key question, lens-specific question, and advice. The command then synthesizes a unified report with a verdicts table, consensus analysis, recurring risks, key questions, and an integrated assessment.

## Components

| Type | Name | Used by | Purpose |
|------|------|---------|---------|
| Command | evaluate | /evaluate | Orchestrates investor panel evaluation |
| Agent | investor-graham | /evaluate | Paul Graham persona |
| Agent | investor-thiel | /evaluate | Peter Thiel persona |
| Agent | investor-altman | /evaluate | Sam Altman persona |
| Agent | investor-andreessen | /evaluate | Marc Andreessen persona |
| Agent | investor-naval | /evaluate | Naval Ravikant persona |
| Agent | investor-balaji | /evaluate | Balaji Srinivasan persona |
| Agent | investor-collison | /evaluate | Patrick Collison persona |
