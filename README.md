# Simple python (REST) API demo project
This project serves as a demo and proof of concept for an API server built on the [FastAPI](https://fastapi.tiangolo.com/) architecture.

Thanks for stopping by, and make sure you skim the cliff notes below if you're interested in cloning and running this package.

## Requirements
This project was built using Python 3.10, and while it's very likely compatible with earlier versions, you will most likely have some type hinting issues.

The other requirements are simply pip packages as per [requirements.txt](requirements.txt).

The server binds to `localhost:80` by default, but can be changed easily by modifying the `uvicorn` flags for whichever launch mechanism you're using.

## Usage
I'll go through a few ways you can run this project below, but you'll most likely want to interface with it as well. Before you go ahead an make a super-slick react app, you could start by loading the supplied [Postman collection](postman_collection.json).

Once the server is running you can check out the [Swagger docs](http://localhost/docs). This particular link will only work at runtime, not necessarily right now as you're reading this on GitHub.

### Run: VSCode
Open this entire repository as your workspace, and you'll find some reasonably [settings](.vscode/settings.json) along with some [launch](.vscode/launch.json) configurations.

Go to `Run and Debug` and select the `API Server` dropdown. You're all set, just hit the `play` button or `F5`.

### Run: Docker
Build the container with the supplied [Dockerfile](Dockerfile) and run it.

If you're using a virtualized environment, you may have to inject some container bindings. For most scenarios I think something like this will serve you well: `docker run --rm -it -p 80:80 <image>`.

Your dynamic image name is very likely `simplerestapi:latest` if you didn't rename the repo.

### Run: Standalone
Open up a terminal and do something along these lines:
```ps
# Linux
cd path/to/repo
python -m pip install --upgrade -r requirements.txt
python -m uvicorn simple_rest_api.main:app --reload --host 0.0.0.0 --port 80

# Windows
cd C:\path\to\repo
python.exe -m pip install --upgrade -r requirements.txt
python.exe -m uvicorn simple_rest_api.main:app --reload --host 0.0.0.0 --port 80
```

Just make sure you're launching the correct Python interpreter. The system default isn't always the version you want -- particularly not when I've gone ahead and done some Python 3.10-esque things in this package.

## Security
For the sake of demobility (that's a real word, surely), the chosen authentication method is the reasonably straightforward API key scheme. However, I have chosen to expand upon this to require a set of paired keys; a *secret key* along with a known *app name*.

In an actual production environment, these keys will most definitely be stored in an external key vault. For this demo though, they are one-way hashed and stored right here [in the repository](simple_rest_api/tempstorage/pseudo_keystore.json).

To get started, you can use the default credentials:<br>
> *app-name* = `demo`<br>
> *api-key* = `z_IlZ7JiE2A4_MCdGK2SR5YbIwm3-64ePyZ3rGqKfZ`

Or if you prefer, you can generate and validate API keys with the supplied [VSCode launch settings](.vscode/launch.json). If that still doesn't cut the mustard, you can go straight to the standalone CLI via [generate_api_key.py](simple_rest_api/cli/generate_api_key.py) and [validate_api_key.py](simple_rest_api/cli/validate_api_key.py).

The keys need to either be injected into the headers of a request, or passed as query parameters. The specific naming for this is controlled via [config.py](simple_rest_api/config.py), but looks something like this:

### Headers
```
> Z-AppName: demo
> Z-ApiKey: z_IlZ7JiE2A4_MCdGK2SR5YbIwm3-64ePyZ3rGqKfZ

[GET] http://localhost/
```
### Query
```
[GET] http://localhost/?z_appname=demo&z_apikey=z_IlZ7JiE2A4_MCdGK2SR5YbIwm3-64ePyZ3rGqKfZ
```

## Persistence
This demo uses a simple In-Memory SQLite instance, which will not persist once you stop the running process. Initial data population happens in [init_db.py](simple_rest_api/utils/init_db.py), which you can tweak to your specific requirements. 

That said, if you're using something like this project for something real, you will obviously use a real backing database. If you want a database, which you may not.

PS: I've used relative imports throughout this package, anticipating that it will be renamed if someone actually wants any of the code. However, the name `simple_rest_api` is hardcoded in the [Dockerfile](Dockerfile), the [CLI utils](simple_rest_api/cli) and the [tests](tests)
