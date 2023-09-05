# You should install:

1. Docker
2. Docker compose
3. Ensure that the localhost ports (3000, 8000) are not in use by other application

# The rest dependencies will be installed by the docker build command

# Build the containers for database backend frontend

docker compose build

# Start the containers

docker compose up

# Make initial migrations

docker-compose exec backend python manage.py migrate

# Create a superuser to access django admin UI

docker-compose exec backend python manage.py createsuperuser

# Run this django command that will populate the database tables

docker-compose exec backend python manage.py import_efo_terms

# Create an account by clicking on Sign Up <a> html element

# Then it will redirect you to login page and you can log in to view the dashboard

# You can search for efo term by passing the efo term ID and press search

# You can navigate to all results by clicking clear

# You can navigate to each page through pagination buttons
