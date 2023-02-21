cd /opt
sudo wget https://www.python.org/ftp/python/3.11.0/Python-3.11.0.tgz
sudo tar xzf Python-3.11.0.tgz
cd Python-3.11.0
sudo ./configure --enable-optimizations
sudo make altinstall
sudo rm -f /opt/Python-3.11.0.tgz

alias python='python3.11'
alias pip='pip3.11'
pip install --upgrade pip setuptools
npm install -g serverless
cd /root/src/
pip install -r requirements.txt
export DJANGO_SETTINGS_MODULE=vcbackend.settings.production
python manage.py migrate

python manage.py createsuperuser
python manage.py collectstatic

export AWS_PROFILE=<your-aws-profile-name>
serverless deploy -s production

npm install

