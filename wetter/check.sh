while inotifywait -q -e modify -e create -e delete -e move --recursive /wetter/ ; do \
    clear; \
    echo "===================================================================="; \
    echo "Check & correct format via black"; \
    echo "===================================================================="; \
    black /wetter; \
    echo ""; \
    echo ""; \
    echo "===================================================================="; \
    echo "Formatting and linting"; \
    echo "===================================================================="; \
    flake8 /wetter; \
    echo ""; \
    echo "===================================================================="; \
    echo "Formatting and linting"; \
    echo "===================================================================="; \
    pytest -m "not (web or long)" --cov=/wetter --cov-report=term-missing --no-cov-on-fail; \
done
