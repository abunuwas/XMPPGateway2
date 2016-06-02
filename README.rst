
REQUISITES

- Make sure you have an XMPP server running (ideally Ejabberd).

- Edit the config file of the XMPP server to listen to the ports
  that you will connect the application to as a component.

- Install Python 3.4+.

- Install pip.

- Install virtualenv. 


To be able to run the code and work on its development:

1) Make sure you have the requisites mentioned before.

2) Clone the repo:

git clone _____________

2.1) [cd XMPPGateway]

3) Create a virtual environment binding it to Python3:

3.1) On Linux/Unix:

XMPPGateway$ virtualenv venv python=python3

3.2) On Windows:

XMPPGateway$ virtualenv venv python=<path_to_Python3_executable, e.g. C:\Python.3.4>

4) Activate the virtual environment:

4.1) On Linux/Unix:

XMPPGateway$ source venv/bin/activate

4.2) On Windows:

XMPPGateway$ venv/scripts/activate

5) Install dependencies:

(venv) XMPPGateway$ pip install -r requirements.txt

6) To make SleekXMPP work, we need to install DNSPython:

6.1) Clone DNSPython

6.2) cd into dnspython

6.3) git checkout -b python3

6.4) setup.py install ....

6.5) ...

7) Add the directory to the PYTHONPATH in the virtual environment:

[run this command from the root directory of the code XMPPGateway/, the directory containing the virtual environment]

(venv) XMPPGateway$ echo {PWD%/*} > venv/lib/Python3.4/site-packages/.pth

# This adds the directory path to the site-packes directory of the virtual environment in a .pth file. 

8) To make sure everything is working properly, run the tests:

(venv) XMPPGateway$ python3 run_tests.py

9) To leave the virtual environment, type:

(venv) XMPPGateway$ deactivate

