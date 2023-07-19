# create venv
python3 -m venv venv

# activate venv
source venv/bin/activate

# install requirements
pip install -r requirements.txt

curr_datetime=$(date +%Y_%m_%d-%H%M%S)
scrapy crawl vikings -O log/vikings_output_"${curr_datetime}".json --logfile log/vikings_"${curr_datetime}".log --loglevel ERROR

deactivate