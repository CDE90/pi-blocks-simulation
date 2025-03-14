# Pi Blocks Simulation Development Guidelines

## Commands

-   Run simulation: `uv run simulation.py`
-   Install dependencies: `uv sync`

## Code Style

-   Python: 3.13+
-   Use Fractions for precise calculations
-   Limit fractions with `.limit_denominator(10**9)` to avoid slowdown
-   Format: Sort imports (std lib → external → local), 88 char line limit
-   Type annotations: Use them for function signatures
-   Naming: snake_case for functions/variables, PascalCase for classes
-   Error handling: Use precise exception types, avoid bare except
-   Math operations: Account for performance vs. precision tradeoffs
