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

2. Create virtual / Conda environment:
```bash
virtualenv -p python3 venv 
```

3. Install in your environment:
```bash
source venv/bin/activate
pip install -e .
```
