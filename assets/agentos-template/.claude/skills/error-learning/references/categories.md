# Error Categories

| Category | Description | Examples |
|----------|------------|----------|
| runtime-environment | Device/package/version/env issues | MPS unsupported, package version conflicts |
| code-logic | Code logic bugs, algorithm errors | Off-by-one, boundary conditions |
| data-handling | Data processing/feature engineering | Wrong column names, data types, missing values |
| latex-formatting | LaTeX/paper formatting | \cref vs \Cref, figure references |
| statistical-methods | Statistical method misuse | Wrong hypothesis test, multiple comparisons |
| library-api | Library function/parameter misuse | Guessing parameter names, deprecated API |
| file-paths | Path/file related | Nonexistent paths, relative path errors |
| conceptual | Conceptual/fundamental misunderstanding | Algorithm principle misunderstood |
| workflow | Workflow/process related | Git operation order, CI/CD |
| other | Doesn't fit above categories | - |

## Severity Levels

| Level | Criteria |
|-------|----------|
| low | Surface/style issue, user catches easily |
| medium | Functional error, but won't produce silently wrong results |
| high | Produces silently wrong results, or causes data loss |
