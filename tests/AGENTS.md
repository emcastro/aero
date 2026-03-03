# Agent (and Human) Configuration Prompt for Testing

## Mutmut emojis
When you run `mutmut browse`, the browser report annotates each mutation
with an emoji that shows its outcome:

* 🙁 **survived** – tests still passed; indicates a missing or weak test.
* 🫥 **no tests** – no test covered that line.
* ⏰ **timeout** – the test run timed out for this mutation.
* 🤔 **suspicious** – result was inconclusive.
* 🔇 **skipped** – mutation wasn’t applied (unsupported location).
* 🧙 **caught by type check** – the type checker prevented the mutation.
* 🛑 **interrupted** – you stopped the run.
* ? **not checked** – mutation wasn’t evaluated.
* 🎉 **killed** – mutation caused a test failure (desired).
* 💥 **segfault** – mutation crashed the process.

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

## Variable Naming Conventions

### Unit Suffixes
Use suffixes to indicate physical units:
- `_m` for meter/distance values (e.g., `dist_m`, `elevation_m`)
- `_d` for degree/angle values (e.g., `azimuth_d`, `azimuths_d`, `calc_azimuth_d`)

### Exclusions from Unit Suffixes
Do **not** use unit suffixes for:
- **Coordinates/points**: Use plain names without suffixes (e.g., `point`, `origins`, `dest`)
- **Constants**: Use plain names without suffixes (e.g., `EPS`, `METER`)

### Minimum Length Rule
- All variable names must be **at least 3 letters** to ensure clarity
- **Exceptions**: The variables `x`, `y`, `xs`, `ys` may use their short forms (2 letters)
- Expand abbreviated names to full words (e.g., `azimuth_d` not `az_d`, `azimuths_d` not `azims_d`)

### Consistency
- Use consistent naming across similar variables (e.g., `point`, `origins` for coordinates)
- Avoid mixing short and long forms for the same concept within a function