up:
	docker-compose -f docker-compose.yml up -d --build

init:
	python migrate
	docker-compose exec admin_panel python manage.py migrate
	docker-compose exec admin_panel python manage.py createsuperuser
	docker-compose exec admin_panel python manage.py collectstatic --no-input --clear

down:
	docker-compose down -v
