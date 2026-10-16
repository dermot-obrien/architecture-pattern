# Pattern Skill Tests

Comprehensive test suite for the architecture pattern skill covering:
- Different pattern types (conceptual, logical, physical)
- Pattern complexities (simple, composite, multi-level)
- Diagram validation
- Scenario complexity
- Edge cases

## Running Tests

```bash
# Run all tests
pytest skills/pattern/tests/

# Run specific test file
pytest skills/pattern/tests/test_pattern_types.py

# Run with verbose output
pytest -v skills/pattern/tests/

# Run with coverage
pytest --cov=skills/pattern skills/pattern/tests/
```

## Test Structure

- `test_pattern_types.py` - Tests for different abstraction levels (conceptual, logical, physical)
- `test_complexity.py` - Tests for various pattern complexities
- `test_scenarios.py` - Tests for scenario validation and composition
- `test_validation.py` - Tests for diagram/document validation
- `test_composite.py` - Tests for composite patterns and participation
- `test_edge_cases.py` - Edge cases and error handling
- `fixtures/` - Test fixtures with various pattern examples

## Test Coverage Goals

- ✓ Simple patterns (3-5 building blocks)
- ✓ Complex patterns (10+ building blocks)
- ✓ Multiple scenarios per pattern
- ✓ Composite patterns (2+ levels deep)
- ✓ All pattern scopes (problem, solution, capability-area, domain, platform)
- ✓ All abstraction levels (conceptual, logical, physical, hybrid)
- ✓ Various diagram topologies (linear, hub-and-spoke, mesh)
- ✓ Edge cases (empty sections, missing data, invalid references)
