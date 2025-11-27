FROM python:3.11-slim
# The version python that the container needs to download

# Create a directory for the Docker container
WORKDIR /app


COPY requirements.txt .
# First copy the requirements, which also includes playwright.

RUN pip install --no-cache-dir -r requirements.txt
# Install the requirements in the container.

COPY . .
# The line (. .) is used to copy the entire source files and directory into the container.

EXPOSE 5000
# The server value, since the hostname contains ":5000" at the ned

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

CMD ["flask", "run"]
