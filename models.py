# used only for the mock/stub VALID_API_KEYS
import config

# In reality this would best be implemented with a lightweight db
# redis would be ideal 

class User():
    def __init__(self):
        self.api_key = None

    @classmethod
    def get_user_from_api_key(cls, api_key):
        """
        Looks up an API key in the DB
        If it exists, returns an instance of the relevant User
        """
        if api_key in config.VALID_API_KEYS:
            user = User()
            user.api_key = api_key
            return user
        return None
