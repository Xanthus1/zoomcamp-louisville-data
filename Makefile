init:
	@echo "-- TERRAFORM CREATING GOOGLE CLOUD PROJECT INFRASTRUCTURE --"
	cd terraform && \
		terraform init && \
		terraform apply -var project=${GCP_PROJECT_ID}

	@echo "-- BUILDING CONTAINERS WITH DOCKER --"
	docker compose build
	@echo "-- INIT COMPLETE --"

start:
	@echo "-- STARTING PREFECT CONTAINERS AND CREATING BLOCKS --"
	docker compose up --detach --no-attach lou-dbt

	@echo "-- RUNNING FLOWS --"
	# TODO: Using default years currently as a quicker test
	docker compose run --rm --entrypoint='python -m flows.web_to_gcs_etl' --name=prefect-etl prefect-scripts
	docker compose run --rm --entrypoint='python -m flows.gcs_to_bq_etl' --name=prefect-etl prefect-scripts
	@echo "-- START COMPLETE. RUN 'make transform' NEXT--"

transform:
	@echo "-- STARTING DBT CONTAINER FOR TRANSFORMATION --"
	docker compose run --rm --workdir='//usr/app/dbt/bq_louisville_data' lou-dbt run
	@echo "-- TRANSFORMATION COMPLETE. --"

stop:
	@echo "-- STOPPING DOCKER CONTAINERS / NETWORKS --"
	docker compose down
	@echo "-- STOP COMPLETE --"

destroy:
	@echo "-- TERRFORM REMOVING GOOGLE CLOUD PROJECT INFRASTRUCTURE --"
	cd terraform && \
		terraform destroy -var project=${GCP_PROJECT_ID}
	@echo "-- REMOVING LOCAL DOCKER INFRASTRUCTURE (INCL. IMAGES, VOLUMES) --"
	docker compose down --rmi --volumes
	@echo "-- DESTROY COMPLETE --"
