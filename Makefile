.PHONY: backend-install backend-test frontend-install frontend-build run-backend run-frontend

backend-install:
	cd backend && python -m pip install -r requirements.txt

backend-test:
	cd backend && python -m pytest

frontend-install:
	cd frontend && npm install

frontend-build:
	cd frontend && npm run build

run-backend:
	cd backend && flask --app wsgi.py run --debug --port 5000

run-frontend:
	cd frontend && npm run dev
