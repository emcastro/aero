# Agent (and Human) Configuration Prompt

You are assisting with a Python geospatial and aerial terrain analysis project. The workspace contains:

## Project Context

- **Language**: MicroPython (it is a subset of Python, with less standard functions).
- **Project topics**: Zarr (for elevation data), GeoJSON, geographic projections.
- **Purpose**: Aircraft terrain awareness and elevation data processing.
- **Data**: Digital Elevation Models (DEM) in Zarr and HGT formats, geographic grid data.

## Key Technologies

- Zarr: For efficient multi-dimensional array storage and retrieval.
- WGS84 Projection: For geographic coordinate transformations.
- GeoJSON: For geographic feature representation.
- LRU Caching: For performance optimization (to be used with extreme caution).

## Project Structure

```
src/
  ├── zarr_test.py          # Main Zarr integration and testing
  ├── geolib.py             # Geographic calculations and projections
  ├── geojson.py            # GeoJSON handling
  ├── ulogging.py           # Custom logging module
  ├── utyping.py            # Type definitions
  ├── microzarr/            # Zarr library implementation
  └── macropython/          # MicroPython compatibility
devdata/                    # Sample DEM data in multiple formats
experiments/                # Testing and experimentation notebooks
typings/                    # Typing stubs for MicroPython (https://micropython-stubs.readthedocs.io)
```

## Project Configuration

- All the Python tools MUST be configured in the `pyproject.toml` file.
- We use `uv` for package and tool management.

## Common Tasks

- Processing elevation data from Zarr stores.
- Projecting aircraft positions along great circle paths.
- Calculating terrain warnings and boundaries.
- Working with geographic bounding boxes and polygons.
- Converting between different coordinate systems.

## When Assisting

- Suggest efficient data access patterns for Zarr.
- Consider memory constraints in implementations.
- Recommend geographic accuracy for aviation use cases.
- Maintain consistency with existing code patterns in `src/`.
- Optimize for MicroPython compatibility when relevant.

## Performance Considerations

- Minimize memory allocations in loops.
- Cache geographic calculations where appropriate.
- Stream large datasets rather than loading entirely.

## Tests

- Read tests/AGENTS.md before working on tests.

## Code Style

- When generating code, ensure it integrates seamlessly with the existing project structure and conventions.
- Never commit anything without a direct order from the user.

- Use type hints with custom types from `utyping` module.
- Follow MicroPython conventions where applicable.
- Include docstrings for functions explaining purpose and parameters.
- Use logging via `ulogging` for debugging.
- Optimize for memory efficiency.
- No third party libraries can be used — they do not fit the target microcontroller, except for pytest purpose.
- Don't use \_-prefix for private function, unless stated.
- Do not guess future requirements. It is the responsibility of the user.
- Use the f"{dirname}/{basename}" pattern to build pathname, not os.path.join.
- Use typing annotation, but not for function return type.
- Never use defensive coding techniques. In case of doubt, just notify it in the chat.
- Markdown files must be formatted in MarkdownLint style. However, don't use any tool for that.

### Variable Naming Conventions

- Unit Suffixes: Use suffixes to indicate physical units:
  - `_m` for meter/distance values (e.g., `dist_m`, `elevation_m`)
  - `_d` for degree/angle values (e.g., `azimuth_d`, `azimuths_d`, `calc_azimuth_d`)
- Exclusions from Unit Suffixes: Do **not** use unit suffixes for:
  - **Coordinates/points**: Use plain names without suffixes (e.g., `point`, `origins`, `dest`)
  - **Constants**: Use plain names without suffixes (e.g., `EPS`, `METER`)
- Minimum Length Rule:
  - All variable names must be **at least 3 letters** to ensure clarity
  - **Exceptions**: The variables `x`, `y`, `xs`, `ys`, `px` may use their short forms (2 letters)
  - Expand abbreviated names to full words (e.g., `azimuth_d` not `az_d`, `azimuths_d` not `azims_d`)
- Consistency:
  - Use consistent naming across similar variables (e.g., `point`, `origins` for coordinates)
  - Avoid mixing short and long forms for the same concept within a function
