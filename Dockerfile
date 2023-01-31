# Python 3.10 base image with minimal Linux distro
FROM python:3.10

# Copy requirements.txt and install dependencies
WORKDIR /tmp
COPY ./requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy across package source code
WORKDIR /code
COPY ./simple_rest_api/ simple_rest_api/

# Set pythonpath and start uvicorn server
ENV PYTHONPATH "${PYTHONPATH}:/code"
EXPOSE 80
CMD ["uvicorn", "simple_rest_api.main:app", "--host", "0.0.0.0", "--port", "80"]