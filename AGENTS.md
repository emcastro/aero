# Agent Configuration Prompt

You are assisting with a Python geospatial and aerial terrain analysis project. The workspace contains:

## Project Context
- **Language**: MicroPython (it is a subset of Python, with less standard functions)
- **Project topics**: Zarr (for elevation data), GeoJSON, geographic projections
- **Purpose**: Aircraft terrain awareness and elevation data processing
- **Data**: Digital Elevation Models (DEM) in Zarr and HGT formats, geographic grid data

## Key Technologies
- Zarr: For efficient multi-dimensional array storage and retrieval
- WGS84 Projection: For geographic coordinate transformations
- GeoJSON: For geographic feature representation
- LRU Caching: For performance optimization (to be used with extreme caution)

## Code Style & Preferences
- Use type hints with custom types from `utyping` module
- Follow MicroPython conventions where applicable
- Include docstrings for functions explaining purpose and parameters
- Use logging via `ulogging` for debugging
- Optimize for memory efficiency
- No thrid party libraries can be used for any use because it does not fit the
  the target microcontroler, except for pytest purpose.  

## Project Structure
```
src/
  ├── zarr_test.py          # Main Zarr integration and testing
  ├── geolib.py             # Geographic calculations and projections
  ├── geojson.py            # GeoJSON handling
  ├── ulogging.py           # Custom logging module
  ├── utyping.py            # Type definitions
  ├── lru_cache.py          # Caching utilities
  ├── microzarr/            # Zarr library implementation
  └── macropython/          # MicroPython compatibility
devdata/                    # Sample DEM data in multiple formats
experiments/                # Testing and experimentation notebooks
typings/                    # Typing stubs for MicroPython (https://micropython-stubs.readthedocs.io)
```

## Project configuration
- All the Python tools MUST be configured in the `pyptoject.toml` file.
- We use `uv` for package and tool management.

## Common Tasks
- Processing elevation data from Zarr stores
- Projecting aircraft positions along great circle paths
- Calculating terrain warnings and boundaries
- Working with geographic bounding boxes and polygons
- Converting between different coordinate systems

## When Assisting
- Suggest efficient data access patterns for Zarr
- Consider memory constraints in implementations
- Recommend geographic accuracy for aviation use cases
- Maintain consistency with existing code patterns in `src/`
- Optimize for MicroPython compatibility when relevant

## Performance Considerations
- Minimize memory allocations in loops
- Cache geographic calculations where appropriate
- Stream large datasets rather than loading entirely

## Test
- Use pytest to run tests
- Use mutmut for mutation testing. When you run `mutmut browse` the
  browser-based report marks each mutation with an emoji indicating its
  outcome:

    * 🙁 **survived** – tests still passed; signals a missing or weak test.
    * 🫥 **no tests** – no test covered that location.
    * ⏰ **timeout** – the test run timed out on this mutation.
    * 🤔 **suspicious** – result was inconclusive.
    * 🔇 **skipped** – mutation wasn’t applied (unsupported spot).
    * 🧙 **caught by type check** – the type checker prevented the mutation.
    * 🛑 **check interrupted by user** – you stopped the run.
    * ? **not checked** – mutation wasn’t evaluated.
    * 🎉 **killed** – mutation caused a test failure (good).
    * 💥 **segfault** – mutation crashed the process.

## Code style
- Use the f"{dirname}/{basename}" pattern to build pathname, not os.path.join
- Use typing annotation
- Do not use return type annotation, unless instructed

When generating code, ensure it integrates seamlessly with the existing project structure and conventions.
