container:
	@echo "===================================================================="
	@echo "Build Docker Container"
	@echo "===================================================================="
	@docker build --tag wetter/wetter .

bash: container
	@echo "===================================================================="
	@echo "Start and enter container"
	@echo "===================================================================="
	@docker run --rm -it -v $(shell pwd):/wetter wetter/wetter bash
