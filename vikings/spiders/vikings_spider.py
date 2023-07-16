import logging as log

import scrapy

from vikings.items import VikingItem


class VikingsSpider(scrapy.Spider):
    """
    Crawl me using:
    scrapy crawl vikings -O log/vikings.json
    """

    name = "vikings"
    MOVIE_NAME = "Vikings"

    start_urls = [
        "https://www.history.com/shows/vikings/cast"
    ]

    def parse(self, response):
        """ Scrapy me using:
        scrapy crawl vikings -O log/vikings.json
        """
        for item in response.xpath("/html/body/div[1]/div[2]/div/div/ul/li"):
            viking_name = item.css("a div.details strong::text").get()
            viking_image_url = item.css("a div.img-container img::attr(src)").get()
            if not viking_name:
                log.error(f"Could not parse viking name for: {item}")
                continue

            viking_page_url = item.css("a::attr(href)").get()
            viking_page_url = viking_page_url and viking_page_url.strip()
            if not viking_page_url:
                log.error(f"Could not parse viking page URL name for: {item}")
                continue

            viking_meta = {
                "name": viking_name,
                "image_urls": [viking_image_url]
            }
            viking_page_url = response.urljoin(viking_page_url)
            yield scrapy.Request(viking_page_url, callback=self.parse_hero, meta={"viking": viking_meta})

    def parse_hero(self, response):
        actor_name = self._parse_actor_name(response)
        description = self._parse_description(response)

        viking_meta = response.meta.get("viking")
        d: dict = {
            "name": viking_meta["name"],
            "actor": actor_name,
            "desc": description,
            "image_urls": viking_meta["image_urls"],
        }

        yield VikingItem.from_dict(self.MOVIE_NAME, d)

    def _parse_description(self, response):
        desc_xpath_v1 = "/html/body/div[1]/div[2]/div/div/article/p[1]/text()"
        desc_xpath_v2 = "/html/body/div[1]/div[2]/div/div/article/div[1]/div/div/p/text()"
        description = response.xpath(desc_xpath_v1).get() \
                      or response.xpath(desc_xpath_v2).get()
        description = description.strip() if description else ""
        return description

    def _parse_actor_name(self, response):
        xpath_ = "/html/body/div[1]/div[2]/div/div/article/header/h1/small/text()"
        actor_name = response.xpath(xpath_).get()
        actor_name = actor_name.strip() if actor_name else ""
        actor_name = actor_name.replace("Played by", "").strip()
        return actor_name
