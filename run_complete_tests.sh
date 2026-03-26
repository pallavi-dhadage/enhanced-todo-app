#!/bin/bash
cd ~/my-todo-app
source venv/bin/activate
export PYTHONPATH="${PYTHONPATH}:${PWD}"

echo "🧪 Running Complete Test Suite..."
echo "================================"

# Run all tests
pytest tests/test_working.py tests/test_simple.py tests/test_integration_simple.py tests/test_coverage.py \
    -v \
    --cov=src \
    --cov-report=term-missing \
    --cov-report=html \
    --tb=short

TEST_RESULT=$?

echo ""
echo "================================"

if [ $TEST_RESULT -eq 0 ]; then
    echo "✅ All tests passed!"
    COVERAGE=$(coverage report | grep TOTAL | awk '{print $4}' | sed 's/%//')
    echo "📊 Total coverage: ${COVERAGE}%"
    echo "📁 Coverage report: htmlcov/index.html"
    echo ""
    echo "To view coverage:"
    echo "  xdg-open htmlcov/index.html"
else
    echo "❌ Some tests failed"
    exit 1
fi
