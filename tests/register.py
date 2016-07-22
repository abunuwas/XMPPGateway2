import requests
import json

def register_user(username, password):
    headers = {"content-type": "application/json", 
                "Host": "localhost"}
    args = ["user3", "localhost", "mypassword"]
    payload = {"key": "secret", 
    			"command": "register",
    			"args": args
    			}
    r = requests.post('http://127.0.0.1:8088/api/admin', headers=headers, data=json.dumps(payload))
    return r

if __name__ == '__main__':
	r = register_user('user3', 'mypassword')
	print(r.status_code)
	print(r.content)
	print(r.headers)
	for el in r.__dict__.items():
		print(el)
