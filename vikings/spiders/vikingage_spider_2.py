from logging import log

import scrapy

import logging as log


class VikingsSpider(scrapy.Spider):
    """
    Crawl me using:
    scrapy crawl vikingage -O log/vikingage.json
    """
    name = "vikingage_2"

    start_urls = [
        "https://www.imdb.com/title/tt5905354/fullcredits"
    ]

    def parse(self, response):
        rows = response.css("table.cast_list > tr")
        for row in rows:
            actor_name = self.parse_actor_name(row)
            viking_name = self.parse_viking_name(row)
            viking_photos_url = self.parse_photos_url(row)

            if not viking_name:
                log.error(f"Could not parse viking name for: {row}")
                continue

            # yield {
            #     "actor": actor_name,
            #     "viking_name": viking_name,
            #     "photos_url": viking_photos_url
            # }

            viking_meta = {
                "viking_name": viking_name,
                "actor_name": actor_name,
                "image_urls": []
            }

            if not viking_photos_url:
                log.error(f"Could not parse photos url for viking: {viking_name} in el: {row}")
                continue

            viking_photos_url = response.urljoin(viking_photos_url)
            r_meta = {
                "viking": viking_meta
            }
            yield scrapy.Request(viking_photos_url, callback=self.parse_images, meta=r_meta)

    def parse_images(self, response):
        for url in response.css("a.titlecharacters-image-grid__thumbnail-link::attr(href)").getall():
            if url:
                viking_meta = response.meta["viking"]
                r_meta = {
                    "viking": viking_meta
                }

                url = response.urljoin(url.strip())
                yield scrapy.Request(url, callback=self.parse_image, meta=r_meta)

    def parse_image(self, response):

        image_url = response.xpath(
            "/html/body/div[2]/main/div[2]/div[3]/div[5]/img/@src").get()

        viking_meta = response.meta["viking"]

        viking_name = viking_meta.get("viking_name")
        actor_name = viking_meta.get("hero_name")
        image_urls = viking_meta["image_urls"]
        image_urls.append(image_url)

        # yield viking_meta
        yield {
            "name": viking_name,
            "actor": actor_name,
            "image_urls": image_urls
        }

    @staticmethod
    def parse_viking_name(el) -> str:
        name = el.css("td:nth-child(4) > a:nth-child(1)::text").get()
        return name and name.strip()

    @staticmethod
    def parse_actor_name(el) -> str:
        name = el.css("td:nth-child(2) > a:nth-child(1)::text").get()
        return name and name.strip()

    @staticmethod
    def parse_photos_url(el) -> str:
        url = el.css("td:nth-child(4) > a:nth-child(1)::attr(href)").get()
        return url and url.strip()
