# Citel_nap_backend
Backend for the Citel NAP Network Analyzer project

## Deployment in EC2
This app is now hosted in an EC2 virtual machine in AWS,
in 54.221.52.3, in the folder /home/ec2-user/citel-nap-backend/vcbackend,
under the ec2-user user. It is executed in a virtual environment, located in
the /home/ec2-user/citel-nap-backend/.venvpy37 folder.
You can deploy code here, for example, via SFTP, or via updates in the Git 
repository.
To update the service that is running, you shoud execute:
sudo systemctl restart nginx gunicorn
To test the backend server manually, in the EC2 server,
log in there, and execute:
`
source /home/ec2-user/citel-nap-backend/.venvpy37/bin/activate
cd /home/ec2-user/citel-nap-backend/vcbackend
python manage.py runserver 0:8000
`
- To update the code
The code is served in production via gunicorn, using the service 
file in vcbackend/config/gunicorn.service, and the configuration 
file vcbackend/config/gunicorn_prod.py file, and in Nginx, using 
the Nginx configuration file vcbackend/config/citen_backend.conf file

## Local deployment and executing
For deploying this code locally:
1. clone it to a folder
2. Create a virtual enviromment, using python 3.7 or higner
3. Activate that virtual environment
4. In a shell, go to the vcbackend folder of the repo and execute pip install -r requirements.txt
For executing the code locally:
1. in a shell, activate the virtual environment that you created for the code
2. go to the vcbackend folder of this project
3. execute `python manage.py runserver 0:8000`
