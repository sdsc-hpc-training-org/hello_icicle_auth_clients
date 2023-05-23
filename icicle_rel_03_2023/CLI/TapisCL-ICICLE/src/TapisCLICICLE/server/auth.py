import time
import os 
import sys

from tapipy.tapis import Tapis
from federatedTenantAuthAPI.get import get_client_code


class Auth:
    def username_grant(self, username: str, password: str, link: str):
        start = time.time()
        try:
            t = Tapis(base_url=f"https://{link}",
                    username=username,
                    password=password)
            t.get_tokens()
        except Exception as e:
            self.logger.warning(e)
            raise ValueError(f"Invalid tapis auth credentials")
        
        self.username = username
        self.password = password
        self.t = t
        self.url = link
        self.access_token = self.t.access_token

        self.configure_decorators(self.username, self.password)
        self.update_credentials(t, username, password)
        # V3 Headers
        header_dat = {"X-Tapis-token": t.access_token.access_token,
                      "Content-Type": "application/json"}
        # create authenticator for tapis systems
        authenticator = t.access_token
        # extract the access token from the authenticator
        
        if 'win' in sys.platform:
            os.system(f"set JWT={self.access_token}")
        else: # unix based
            os.system(f"export JWT={self.access_token}")

        self.logger.info(f"initiated in {time.time()-start}")

        return f"Successfully initialized tapis service on {self.url}"
    
    def device_code_grant(self, link):
        start = time.time()
        try:
            t = Tapis(base_url=f"https://{link}")
        except Exception as e:
            self.logger.warning(e)
            raise ValueError(f"Invalid uri")
        client_id = get_client_code(link)
        self.t.authenticator.generate_device_code(client_id=client_id)
        

