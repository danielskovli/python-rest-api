'''Configuration'''


class Security:
    api_key_length = 32
    api_key_prefix = 'z_'

    class Hashing:
        api_key_method = None

    class Headers:
        api_key = 'Z-ApiKey'
        app_name = 'Z-AppName'

    class Query:
        api_key = 'z_apikey'
        app_name = 'z_appname'


class Routing:
    route_prefix = 'demo'


class Hosts:
    pass


class RemoteEndpoints:
    pass