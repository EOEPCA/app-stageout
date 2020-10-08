import requests

def post_request(endpoint, data, auth, headers={}):
    
    return requests.post(endpoint,
                         data=data,
                         headers=headers,
                         auth=auth)


def post_atom(atom, end_point, username, api_key):
    
    data = atom.to_string()
    
    auth = (username,
            api_key)
    
    headers = {'Content-Type': 'application/atom+xml',
               'Accept': 'application/xml'}
    
    r = post_request(end_point, 
                     data, 
                     auth,
                     headers)
    
    return r