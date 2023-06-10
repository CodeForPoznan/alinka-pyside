test:
	pytest .

type=specjalne
generate:
	python app/create_documents.py --type ${type}

style:
	black .
	isort .
	flake8 .

start:
	python app/main.py
