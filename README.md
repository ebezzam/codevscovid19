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

### Running webserver

1. Start local server
```bash
python run_server.py
```

2. ngrok magic
```bash
ngrok http 5000
```

3. Copy ngrok URL (with the `/whatsapp) in the "WHEN A MESSAGE COMES IN" box: https://www.twilio.com/console/sms/whatsapp/sandbox
