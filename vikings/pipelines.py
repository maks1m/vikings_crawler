# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


import logging as log

import psycopg2
# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem

from vikings.items import VikingItem


class VikingsPipeline:
    def process_item(self, item, spider):
        return item


class DuplicatesPipeline:

    def __init__(self):
        self.vikings_seen = set()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if adapter["name"] in self.vikings_seen:
            raise DropItem(f"Duplicate viking item found: {item!r}")
        else:
            self.vikings_seen.add(adapter["name"])
            return item


class EmptyDescriptionValuePipeline:

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        desc = adapter.get("desc")
        if desc:
            return item
        else:
            log.error(f"Empty description for {adapter.get('name')}")
            raise DropItem(f"Viking description is absent {item}")


class DropInconsistentImagesPipeline:

    def process_item(self, item, spider):
        if item["image_count"] != len(item["image_urls"]):
            raise DropItem('skipping')

        return item


class SavingToPostgresPipeline:

    def __init__(self):
        self.connection = psycopg2.connect(
            host="localhost",
            dbname="vikings",
            user="admin",
            password="admin",
            port=5432)
        self.curr = self.connection.cursor()

    def process_item(self, item: VikingItem, spider):
        self.store_db(item)
        return item

    def store_db(self, item: VikingItem):
        try:
            viking_id = self.store_vikings(item)

            self.delete_viking_images(viking_id)
            self.delete_viking_movies(viking_id)

            movie_id = self.store_movies(item, viking_id)
            self.store_images(item, viking_id, movie_id)

            self.connection.commit()

        except Exception as e:
            log.error(f"An error occurred while storing item")
            log.error(f"Error message: {e}")
            self.connection.rollback()

    def store_vikings(self, item) -> int:
        insert_query = """
            INSERT INTO vikings.vikings ("name")
            VALUES (%s)
            ON CONFLICT ("name") DO NOTHING
            RETURNING "id";
        """
        values = (item['name'],)

        log.debug(f"running query: {insert_query}")
        log.debug(f"values: {values}")

        self.curr.execute(insert_query, values)
        log.debug("inserted")

        result = self.curr.fetchone()
        if not result:
            select_query = """
                select id
                from vikings.vikings
                where name = (%s);
            """

            log.debug("Viking already present, getting id...")
            log.debug(f"running query: {select_query}")
            log.debug(f"values: {values}")

            self.curr.execute(select_query, values)
            result = self.curr.fetchone()

        viking_id = result[0]
        print(f"Viking ID: {viking_id}")
        return viking_id

    def store_movies(self, item, viking_id) -> int:
        movie_values = {
            "viking_id": viking_id,
            "movie_name": item['movie_name'],
            "actor": item['actor'],
            "desc": item['desc']
        }

        query = f"""
            INSERT INTO vikings.viking_movies ("viking_id", "name", "actor_name", "description")
            VALUES (%(viking_id)s, %(movie_name)s, %(actor)s, %(desc)s)
            ON CONFLICT ("viking_id") DO NOTHING
            RETURNING "id";
        """

        log.debug(f"running query: {query}")

        self.curr.execute(query, movie_values)
        movie_id = self.curr.fetchone()[0]
        print(f"Movie ID: {movie_id}")
        return movie_id

    def store_images(self, item, viking_id, movie_id):
        for image in item["image_urls"]:
            query = f"""
                INSERT INTO vikings.viking_images ("viking_id", "movie_id", "image_url")
                VALUES (%s, %s, %s);
            """
            self.curr.execute(query, (viking_id, movie_id, image))

    def delete_records(self, table, condition_column, condition_value):
        query = f"""
        DELETE FROM {table}
        WHERE {condition_column} = %s
        """
        log.debug(f"running query:")
        log.debug(f"{query}")
        self.curr.execute(query, (condition_value,))

    def delete_viking_images(self, viking_id):
        self.delete_records('vikings.viking_images', 'viking_id', viking_id)

    def delete_viking_movies(self, viking_id):
        self.delete_records('vikings.viking_movies', 'viking_id', viking_id)

    def close_spider(self, spider):
        self.curr.close()
        self.connection.close()
