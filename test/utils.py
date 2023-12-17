def get_mongo_credentials(path : str):
    username = None
    password = None

    try:
        with open(path, 'r') as file:
            for line in file:
                if line.startswith('MONGO_INITDB_ROOT_USERNAME='):
                    username = line.strip().split('=')[1]
                elif line.startswith('MONGO_INITDB_ROOT_PASSWORD='):
                    password = line.strip().split('=')[1]
    except FileNotFoundError:
        print('mongo.auth.env file not found')

    return username, password