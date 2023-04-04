container:
	@echo "===================================================================="
	@echo "Build Docker Container"
	@echo "===================================================================="
	@docker build --tag wetter/wetter .

bash: container
	@echo "===================================================================="
	@echo "Start and enter container"
	@echo "===================================================================="
	@docker run --rm -it -v $(shell pwd)/wetter:/wetter wetter/wetter bash

watch: container
	@echo "===================================================================="
	@echo "Starting watch environment in docker container"
	@echo "===================================================================="
	@docker run --pull never --workdir /wetter --rm -it -v $(shell pwd)/wetter:/wetter wetter/wetter bash check.sh

package: container
	@echo "===================================================================="
	@echo "Start and enter container"
	@echo "===================================================================="
	@docker run --rm -it -v $(shell pwd)/wetter:/wetter wetter/wetter poetry build

wheel: package
