from configparser import ConfigParser
import os
import sys

CONFIG_PATH = os.path.join(os.path.dirname(sys.argv[0]),'config.ini')
class MyConfig:
    def __init__(self):
        self.cf = ConfigParser()
        self.cf.read(CONFIG_PATH,encoding='utf-8-sig')
    def get_jq_account(self):
        account= self.cf['JQ_account']['account']
        pw = self.cf['JQ_account']['password']
        return account,pw
    def get_tushre_token(self):
        return self.cf['tushare_account']['token']