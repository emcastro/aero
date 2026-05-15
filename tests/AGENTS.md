# Agent (and Human) Configuration Prompt for Testing

- Use `uv run` to activate the environment.
- Use pytest to run tests.
- Use mutmut for mutation testing.
- When using assert, don't add explanation text.
- Use `pytest.approx()` for floating point comparisons, not manual `abs()` checks.
- **Coordinate ranges for tests**: X (lon) and Y (lat) must use *distinct, non-overlapping* numeric ranges so tests can catch axis-swapping bugs. Both axes must include negative values. WGS84 bounds apply: lon ∈ [-180, 180], lat ∈ [-90, 90]. Example: X ∈ [-70, -50] and Y ∈ [-2, 10] is valid; X ∈ [0, 15] and Y ∈ [0, 15] is not.


## Mutmut emojis
When you run `mutmut browse`, the browser report annotates each mutation
with an emoji that shows its outcome:

- 🙁 **survived** – tests still passed; indicates a missing or weak test.
- 🫥 **no tests** – no test covered that line.
- ⏰ **timeout** – the test run timed out for this mutation.
- 🤔 **suspicious** – result was inconclusive.
- 🔇 **skipped** – mutation wasn’t applied (unsupported location).
- 🧙 **caught by type check** – the type checker prevented the mutation.
- 🛑 **interrupted** – you stopped the run.
- ? **not checked** – mutation wasn’t evaluated.
- 🎉 **killed** – mutation caused a test failure (desired).
- 💥 **segfault** – mutation crashed the process.

## Geodata visualization from tests
Many tests exercise geographic logic; it’s helpful to render their
input/output as GeoJSON.

Guidelines:

1. Generate one GeoJSON file per test, naming it after the test itself.
2. Include both the geometries mentioned in the test source and any
   features produced during execution.
3. Annotate features using the variable names from the test for clarity.
4. Validate each GeoJSON with `gdal info` before loading in a GIS.

These files make it easier to review edge cases and verify spatial
behaviour visually.
