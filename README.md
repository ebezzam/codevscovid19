# CodeVsCovid19 project

### Setup

1. Add following environment variables to use Twilio. E.g. on macOS, open your bash profile:
```bash
vim ~/.bash_profile 
```
And add the following lines with your values:
```bash
export TWILIO_SID=[YOUR_SID]
export TWILIO_TOKEN=[YOUR_TOKEN]
```
Enact changes:
```bash
source ~/.bash_profile
```

2. Get an API key from LocationIQ: https://locationiq.com/

Add it to your environment variables:
```bash
vim ~/.bash_profile 
```
And add the following lines with your values:
```bash
export LOCATIONIQ_TOKEN=[YOUR_KEY]
```
Enact changes:
```bash
source ~/.bash_profile
```

3. Create virtual / Conda environment:
```bash
virtualenv -p python3 venv 
```

4. Install in your environment:
```bash
source venv/bin/activate
pip install -e .
```

5. Install `ngrok` to setup light webserver. Follow steps here: https://ngrok.com/download

### Running webserver for webhook

Largely following this tutorial: https://www.twilio.com/docs/sms/quickstart/python-msg-svc

1. Start local server
```bash
python run_server.py
```

2. ngrok magic
```bash
ngrok http 5000
```

3. Copy ngrok URL (with the `/whatsapp) in the "WHEN A MESSAGE COMES IN" box: https://www.twilio.com/console/sms/whatsapp/sandbox


### Setup landing page for signup

Taking ideas from this tutorial: https://medium.com/@dushan14/create-a-web-application-with-python-flask-postgresql-and-deploy-on-heroku-243d548335cc

1) Install PostGres: https://thecodersblog.com/PostgreSQL-PostGIS-installation/
```bash
brew install postgres
brew install postgis
```

Create databases:
```bash
createdb covid19
createdb clients
```

Enter:
```bash
psql -d covid19
```

2) Install Heroku: https://devcenter.heroku.com/articles/heroku-cli#download-and-install
```bash
brew tap heroku/brew && brew install heroku
```

Make and account and login:
```bash
heroku login
```


Docs for Flask SQL: https://flask-sqlalchemy.palletsprojects.com/en/2.x/queries/
Docs for Bootstrap (framework for website): https://getbootstrap.com/docs/4.4/components/forms/#checkboxes-and-radios


### Get entries from dataset


```bash
sqlite3 volunteers.db   # .exit to quit
sqlite3 clients.db      # .exit to quit
```

To delete
```bash
rm *.db
```

launch:
```bash
python manage.py runserver
```

### Get entries from dataset

Add password to environment variable `COVID19_TOKEN`.

Get it from Eric.

Endpoint: 


