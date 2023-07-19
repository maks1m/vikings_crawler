## Scrapy project.

It has to scrapers:
- vikings/spiders/vikingage_spider.py
- vikings/spiders/vikings_spider.py

All scraped data is saved to PostgreSQL database using this pipeline:
- vikings/pipelines.SavingToPostgresPipeline

To run scrapers there are two bash files:
- [run_vikingage.sh](run_vikingage.sh)
- [run_vikings.sh](run_vikings.sh)

Every script file will do next:
- create a virtual env into local directory
- install all dependencies
- run scraper
- deactivate venv

Logs and text outputs would be saved to `log/` directory.