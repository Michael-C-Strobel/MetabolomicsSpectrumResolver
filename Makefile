build:
	docker build -f Dockerfile -t metabolomicsusi .

clean:
	docker rm metabolomicsusi |:

development: clean
	docker run -it -p 5087:5000 --name metabolomicsusi metabolomicsusi /app/run_dev_server.sh

server: clean
	docker run -d -p 5087:5000 --name metabolomicsusi metabolomicsusi /app/run_server.sh

interactive: clean
	docker run -it -p 5087:5000 --name metabolomicsusi metabolomicsusi /app/run_server.sh

bash: clean
	docker run -it -p 5087:5000 --name metabolomicsusi metabolomicsusi bash

attach:
	docker exec -i -t metabolomicsusi /bin/bash



#Docker Compose
server-compose-interactive:
	docker-compose build
	docker-compose up

server-compose:
	docker-compose build
	docker-compose up -d

server-compose-production-interactive:
	docker-compose build
	docker-compose -f docker-compose.yml -f docker-compose-production.yml up

server-compose-production:
	docker-compose build
	docker-compose -f docker-compose.yml -f docker-compose-production.yml up -d