#!/bin/bash

###############################################################################
# Devflow npm Package Integration Tests
#
# Tests the npm package installation and all CLI commands
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
TESTS_PASSED=0
TESTS_FAILED=0

# Test functions
pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((TESTS_PASSED++))
}

fail() {
    echo -e "${RED}✗${NC} $1"
    ((TESTS_FAILED++))
}

info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

echo "======================================"
echo "Devflow npm Package Integration Tests"
echo "======================================"
echo ""

# Test 1: Python Detection
info "Testing Python detection..."
if node lib/python-check.js --silent; then
    pass "Python 3.9+ detected"
else
    fail "Python detection failed"
fi

# Test 2: All bin scripts exist
info "Checking all 14 bin scripts exist..."
BIN_SCRIPTS=(
    "devflow-cost"
    "devflow-validate"
    "devflow-story"
    "devflow-checkpoint"
    "devflow-memory"
    "devflow-collab"
    "devflow-create-persona"
    "devflow-personalize"
    "devflow-validate-overrides"
    "devflow-new-doc"
    "devflow-tech-debt"
    "devflow-setup-checkpoint"
    "devflow-init"
    "devflow-version"
)

for script in "${BIN_SCRIPTS[@]}"; do
    if [ -f "bin/${script}.js" ]; then
        pass "bin/${script}.js exists"
    else
        fail "bin/${script}.js missing"
    fi
done

# Test 3: All Python scripts exist
info "Checking all Python scripts exist..."
PYTHON_SCRIPTS=(
    "cost_dashboard.py"
    "validate_setup.py"
    "run-story.py"
    "context_checkpoint.py"
    "memory_summarize.py"
    "run-collab.py"
    "create-persona.py"
    "personalize_agent.py"
    "validate-overrides.py"
    "new-doc.py"
    "tech-debt-tracker.py"
    "setup-checkpoint-service.py"
    "init-project-workflow.py"
    "update_version.py"
)

for script in "${PYTHON_SCRIPTS[@]}"; do
    if [ -f "tooling/scripts/${script}" ]; then
        pass "tooling/scripts/${script} exists"
    else
        fail "tooling/scripts/${script} missing"
    fi
done

# Test 4: package.json is valid
info "Validating package.json..."
if node -e "JSON.parse(require('fs').readFileSync('package.json', 'utf-8'))" 2>/dev/null; then
    pass "package.json is valid JSON"
else
    fail "package.json is invalid"
fi

# Test 5: Version sync works
info "Testing version sync..."
if node scripts/sync-version.js 2>&1 | grep -q "sync complete"; then
    pass "Version sync script works"
else
    fail "Version sync script failed"
fi

# Test 6: lib utilities are valid JavaScript
info "Checking lib utilities..."
for lib in lib/*.js; do
    if node -c "$lib" 2>/dev/null; then
        pass "$(basename $lib) is valid JavaScript"
    else
        fail "$(basename $lib) has syntax errors"
    fi
done

# Test 7: Bin scripts are executable (on Unix)
if [[ "$OSTYPE" != "msys" && "$OSTYPE" != "win32" ]]; then
    info "Checking bin scripts are executable..."
    for script in bin/*.js; do
        if [ -x "$script" ] || head -n 1 "$script" | grep -q "^#!/usr/bin/env node"; then
            pass "$(basename $script) has shebang"
        else
            fail "$(basename $script) missing shebang or not executable"
        fi
    done
fi

# Summary
echo ""
echo "======================================"
echo "Test Results"
echo "======================================"
echo -e "${GREEN}Passed:${NC} $TESTS_PASSED"
echo -e "${RED}Failed:${NC} $TESTS_FAILED"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed.${NC}"
    exit 1
fi
