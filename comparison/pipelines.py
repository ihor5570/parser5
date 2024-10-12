import json

from utils import TEMP_DIR_NAME


class ComparisonPipeline:
    """
    Pipeline that saves new products and their prices into json file
    after closing spider
    """

    def __init__(self) -> None:
        self.data = {}

    def process_item(self, item, spider):
        """
        Process received items and adding it to dict
        """
        code = item["code"]

        self.data[code] = item

        # spider.logger.info(f'[{code}] has been added to file from: {spider.name}')

        return item

    def close_spider(self, spider) -> None:
        """
        Save processed items to json file
        """

        new_file_path = f"{TEMP_DIR_NAME}/{spider.name}.json"
        with open(new_file_path, "w") as file:
            json.dump(self.data, file, indent=4)
