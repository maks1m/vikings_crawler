curr_datetime=$(date +%Y_%m_%d-%H%M%S)
scrapy crawl vikingage -O log/vikingage_output_"${curr_datetime}".json --logfile log/vikingage_"${curr_datetime}".log --loglevel ERROR