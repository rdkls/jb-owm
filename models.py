
# In reality this would best be implemented with a lightweight db
# redis would be ideal 

class User():
    @classmethod
    def check_api_key(self, api_key):
        return self

    def rate_limit_is_ok(self, api_key):
        return true
