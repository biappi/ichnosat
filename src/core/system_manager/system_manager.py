from src.data.logger.logger import logger
import sys
from src.core.processing_pipe.src.PluginManager import PluginManager
#from src.core.downloader.start import start_downloader
from src.core.downloader.Downloader import Downloader
from src.data.database.db import DB
from src.core.processing_pipe.src.ProcessingPipeManager import ProcessingPipeManager
import configparser
from src.data.database.services.products_service import ProductsService

class SystemManager():
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config_file_path = "/usr/ichnosat/src/core/system_manager/config/config.cfg"
        self.ProcessingPipeManager = ProcessingPipeManager()
        self.config.read(self.config_file_path)
        self.pluginManager = PluginManager(self.config['PATHS']['plugins'])
        self.productService = ProductsService()

    def compile_plugins(self):
        self.pluginManager.compile_plugins()

    def trigger_downloader(self):
        logger.debug("(SystemManager trigger_downloader) ")
        logger.debug("(SystemManager get_pending_products) call downloader ")
        downloader = Downloader()
        downloader.start()
        logger.debug("(SystemManager get_pending_products) call processing")
        self.ProcessingPipeManager.start_processing()

    def create_database(self):
        try:
            db = DB()
            db.create_db()
            return True
        except Exception as err:
            logger.debug("(SystemManager create_database) Unexpected error:")
            logger.debug(err)
            return False


    def get_pending_products(self):
        logger.debug("(SystemManager get_pending_products) ")
        return self.productService.get_pending_products()

    def get_downloading_products(self):
        return self.productService.get_downloading_products()

    def get_downloaded_products(self):
        return self.productService.get_downloaded_products()

    def get_processing_products(self):
        return self.productService.get_processing_products()

    def get_processed_products(self):
        return self.productService.get_processed_products()

    def is_first_installation(self):
        self.config.read(self.config_file_path)
        return True if self.config['SYSTEM_STATUS']['first_installation'] == 'true' else False

    def set_first_installation_config(self, new_status):
        try:
            value = 'true' if new_status else 'false'
            config = configparser.RawConfigParser()
            config.read(self.config_file_path)
            config.set('SYSTEM_STATUS', 'first_installation', value)
            with open(self.config_file_path, 'w') as configfile:
                config.write(configfile)
            return True
        except Exception as err:
            logger.debug("(SystemManager set_first_installation_config) Unexpected error:")
            logger.debug(err)
            return False





