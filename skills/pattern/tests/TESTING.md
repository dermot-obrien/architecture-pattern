# Pattern Skill Testing Guide

This test suite provides comprehensive coverage of the architecture pattern skill's functionality.

## Test Coverage

### Pattern Types (`test_pattern_types.py`)
Tests different abstraction levels and pattern scopes:
- ✓ **Conceptual patterns**: All local IDs, no physical artifacts (3 tests)
- ✓ **Logical patterns**: Solution components with ABBs, deployment-agnostic (1 test)
- ✓ **Physical patterns**: Specific technologies and products (1 test)
- ✓ **Hybrid patterns**: Mix of conceptual, logical, and physical (1 test)
- ✓ **Scope variations**: problem, solution, capability-area, domain, platform (5 tests)

### Complexity Levels (`test_complexity.py`)
Tests patterns of varying complexity:
- ✓ **Simple**: 3-5 building blocks, 1-2 interfaces (1 test)
- ✓ **Medium**: 6-10 building blocks, multiple services, branching flows (1 test)
- ✓ **Complex**: 12+ building blocks, mesh topology, many-to-many relationships (1 test)
- ✓ **Hub-and-spoke**: Central orchestrator with spokes (1 test)

### Scenario Complexity (`test_scenarios.py`)
Tests various scenario patterns:
- ✓ **Single scenario**: Minimal valid scenario (1 test)
- ✓ **Multiple scenarios**: 5 different scenarios in one pattern (1 test)
- ✓ **Long scenarios**: 15+ step scenarios (1 test)
- ✓ **Explicit Start/Finish**: Properly declared entry/exit points (1 test)

### Composite Patterns (`test_composite.py`)
Tests pattern composition:
- ✓ **Simple composite**: One pattern calls another (1 test)
- ✓ **Multi-level**: 3-level deep composition (1 test)
- ✓ **Open participation**: TBD participating patterns (1 test)
- ✓ **Approval gate**: Approved patterns cannot reference Draft patterns (1 test)

### Edge Cases (`test_edge_cases.py`)
Tests boundary conditions and special cases:
- ✓ **No interfaces**: Single self-contained component (1 test)
- ✓ **Complex mappings**: Multiple catalogue relationships per component (1 test)
- ✓ **Bidirectional**: Two-way communication patterns (1 test)
- ✓ **Minimal sections**: Only required sections (1 test)
- ✓ **Status variations**: Draft, In Review, Approved, Active, Deprecated (5 tests)
- ✓ **Special characters**: Dashes, parentheses, colons in names (1 test)

## Running Tests

### Quick Start

```bash
# Run all tests
cd skills/pattern/tests
./run_tests.sh

# Or with pytest directly
pytest -v
```

### Selective Testing

```bash
# Run specific test file
pytest test_pattern_types.py

# Run specific test
pytest test_pattern_types.py::test_conceptual_pattern_simple

# Run tests matching pattern
pytest -k "conceptual"

# Run tests with verbose output
pytest -vv

# Run with coverage report
pytest --cov=.. --cov-report=html
```

### Parallel Execution

```bash
# Run tests in parallel (faster)
pytest -n auto
```

## Test Statistics

- **Total Tests**: 26+
- **Test Files**: 5
- **Pattern Fixtures**: 40+
- **Coverage Areas**:
  - Pattern types: 11 tests
  - Complexity levels: 4 tests
  - Scenarios: 4 tests
  - Composition: 4 tests
  - Edge cases: 13 tests

## Continuous Integration

These tests run automatically on every push and pull request via GitHub Actions:
- ✓ Isolated pytest execution
- ✓ Coverage reporting
- ✓ Fast feedback (< 1 minute)

## Writing New Tests

### Test Structure

```python
def test_new_pattern_feature(temp_workspace):
    """Test description."""
    # Create pattern directory
    pattern_dir = temp_workspace / "patterns" / "AP-XXX-test"
    pattern_dir.mkdir(parents=True)
    
    # Create pattern content
    pattern_content = """..."""
    
    # Write to file
    (pattern_dir / "index.md").write_text(pattern_content)
    
    # Assertions
    assert (pattern_dir / "index.md").exists()
```

### Fixtures

- `temp_workspace`: Provides temporary workspace with binding configuration
- `model_command`: Path to model.py command (configurable via MODEL_BIN env var)

### Best Practices

1. **One concept per test**: Test one thing clearly
2. **Descriptive names**: `test_composite_with_open_participating_pattern`
3. **Clear documentation**: Docstring explaining what's tested
4. **Use fixtures**: Leverage shared test infrastructure
5. **Assert clearly**: Make failures easy to diagnose

## Integration with model.py

These tests create pattern fixtures but don't execute model.py validation by default (that's tested in the CI's example job). To test with actual model validation:

```python
import subprocess

def test_with_validation(temp_workspace, model_command):
    # Create pattern...
    
    # Run model validation
    result = subprocess.run(
        [model_command, "validate", str(pattern_dir / "index.md")],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0, f"Validation failed: {result.stderr}"
```

## Future Enhancements

- [ ] Integration tests with actual model.py execution
- [ ] Diagram generation tests
- [ ] Publish.py end-to-end tests
- [ ] Performance benchmarks
- [ ] Property-based testing (hypothesis)
- [ ] Mutation testing
