import logging as log

import scrapy

from vikings.items import VikingsItem


class VikingsSpider(scrapy.Spider):
    name = "vikings"

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
        actor_name = self.parse_actor_name(response)
        description = self.parse_description(response)

        viking_meta = response.meta.get("viking")
        d = {
            "name": viking_meta["name"],
            "actor": actor_name,
            "desc": description,
            "image_urls": viking_meta["image_urls"],
        }

        yield VikingsItem.from_dict(d)

    @staticmethod
    def parse_description(response):
        desc_xpath_v1 = "/html/body/div[1]/div[2]/div/div/article/p[1]/text()"
        desc_xpath_v2 = "/html/body/div[1]/div[2]/div/div/article/div[1]/div/div/p/text()"
        description = response.xpath(desc_xpath_v1).get() \
                      or response.xpath(desc_xpath_v2).get()
        description = description.strip() if description else ""
        return description

    @staticmethod
    def parse_actor_name(response):
        xpath_ = "/html/body/div[1]/div[2]/div/div/article/header/h1/small/text()"
        actor_name = response.xpath(xpath_).get()
        actor_name = actor_name.strip() if actor_name else ""
        actor_name = actor_name.replace("Played by", "").strip()
        return actor_name
