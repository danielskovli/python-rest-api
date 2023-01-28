# Python 3.10 base image with minimal Linux distro
FROM python:3.10

# Create some dirs if required
WORKDIR /code/lib

# Copy and install requirements.txt. Install location is /code/lib
WORKDIR /tmp
COPY ./requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy codebase
COPY . /code/qshot-master/

# Copy across QApi source code
WORKDIR /code
COPY ./simple_rest_api/ /code/simple_rest_api/

# Set pythonpath and start uvicorn server
ENV PYTHONPATH "${PYTHONPATH}:/code:/code/lib"
EXPOSE 80
CMD ["uvicorn", "simple_rest_api.main:app", "--host", "0.0.0.0", "--port", "80"]