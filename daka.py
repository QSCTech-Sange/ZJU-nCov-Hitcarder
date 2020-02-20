# -*- coding: utf-8 -*-
import requests, json, re
import time, datetime, os, sys
import getpass
import logging
from halo import Halo
from apscheduler.schedulers.blocking import BlockingScheduler

class DaKa(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.login_url = "https://zjuam.zju.edu.cn/cas/login?service=https%3A%2F%2Fhealthreport.zju.edu.cn%2Fa_zju%2Fapi%2Fsso%2Findex%3Fredirect%3Dhttps%253A%252F%252Fhealthreport.zju.edu.cn%252Fncov%252Fwap%252Fdefault%252Findex"
        self.base_url = "https://healthreport.zju.edu.cn/ncov/wap/default/index"
        self.save_url = "https://healthreport.zju.edu.cn/ncov/wap/default/save"
        self.sess = requests.Session()

    def login(self):
        """Login to ZJU platform"""
        res = self.sess.get(self.login_url)
        execution = re.search('name="execution" value="(.*?)"', res.text).group(1)
        res = self.sess.get(url='https://zjuam.zju.edu.cn/cas/v2/getPubKey').json()
        n, e = res['modulus'], res['exponent']
        encrypt_password = self._rsa_encrypt(self.password, e, n)

        data = {
            'username': self.username,
            'password': encrypt_password,
            'execution': execution,
            '_eventId': 'submit'
        }
        res = self.sess.post(url=self.login_url, data=data)
        return self.sess
    
    def post(self):
        """Post the hitcard info"""
        res = self.sess.post(self.save_url, data=self.info)
        return json.loads(res.text)
    
    def get_date(self):
        today = datetime.date.today()
        return "%4d%02d%02d" %(today.year, today.month, today.day)
        
    def get_info(self, html=None):
        """Get hitcard info, which is the old info with updated new time."""
        if not html:
            res = self.sess.get(self.base_url)
            html = res.content.decode()
        
        old_info = json.loads(re.findall(r'oldInfo: ({[^}]+})', html)[0])
        name = re.findall(r'realname: "([^\"]+)",', html)[0]
        number = re.findall(r"number: '([^\']+)',", html)[0]

        new_info = old_info.copy()
        new_info['name'] = name
        new_info['number'] = number
        new_info["date"] = self.get_date()
        new_info["created"] = round(time.time())
        # form change
        new_info['jrdqtlqk[]'] = 0
        new_info['jrdqjcqk[]'] = 0
        self.info = new_info
        return new_info

    def _rsa_encrypt(self, password_str, e_str, M_str):
        password_bytes = bytes(password_str, 'ascii') 
        password_int = int.from_bytes(password_bytes, 'big')
        e_int = int(e_str, 16) 
        M_int = int(M_str, 16) 
        result_int = pow(password_int, e_int, M_int) 
        return hex(result_int)[2:].rjust(128, '0')

def doDaka(username, password,logger):
    print("\n[Time] %s" %datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("🚌 打卡任务启动")
    logger.info("🚌 打卡任务启动")

    spinner = Halo(text='Loading', spinner='dots')
    spinner.start('正在新建打卡实例...')
    logger.info('正在新建打卡实例...')

    dk = DaKa(username, password)
    spinner.succeed('已新建打卡实例')
    logger.info('已新建打卡实例')

    spinner.start(text='登录到浙大统一身份认证平台...')
    logger.info('登录到浙大统一身份认证平台...')
    dk.login()
    spinner.succeed('已登录到浙大统一身份认证平台')
    logger.info('已登录到浙大统一身份认证平台')

    spinner.start(text='正在获取个人信息...')
    logger.info('正在获取个人信息...')
    dk.get_info()
    spinner.succeed('%s %s同学, 你好~' %(dk.info['number'], dk.info['name']))
    logger.info('%s %s同学, 你好~' %(dk.info['number'], dk.info['name']))

    spinner.start(text='正在为您打卡打卡打卡')
    logger.info('正在为您打卡打卡打卡')
    res = dk.post()
    if str(res['e']) == '0':
        spinner.stop_and_persist(symbol='🦄 '.encode('utf-8'), text='已为您打卡成功！')
        logger.info('已为您打卡成功！')
    else:
        spinner.stop_and_persist(symbol='🦄 '.encode('utf-8'), text=res['m'])
        logger.info(res['m'])

def main():
    # Create log
    fh = logging.FileHandler('./log.txt',encoding='utf-8')
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    fm = logging.Formatter("[%(asctime)s] %(message)s",datefmt='%Y-%m-%d %H:%M:%S')
    logger.addHandler(fh)
    fh.setFormatter(fm)

    if os.path.exists('./config.json'):
        configs = json.loads(open('./config.json', 'r').read())
        users = configs["users"]
    else:
        users = []
        for i in range(int(input("👤 总共想帮几位用户打卡: "))):
            users.append(dict())
            users[i]["username"] = input("👤 浙大统一认证用户名: ")
            users[i]["password"] = getpass.getpass('🔑 浙大统一认证密码: ')
            print("⏲  请输入定时时间（默认每天6:05）")
            users[i]["schedule"] = dict()
            users[i]["schedule"]["hour"] = input("\thour: ") or 6
            users[i]["schedule"]["minute"] = input("\tminute: ") or 5

    # Schedule task
    scheduler = BlockingScheduler()
    for user in users:
        scheduler.add_job(doDaka, 'cron', args=[user["username"], user["password"],logger], hour=user["schedule"]["hour"], minute=user["schedule"]["minute"])
        print('⏰ 已启动定时程序，每天 %02d:%02d 为 %s 打卡' %(int(user["schedule"]["hour"]), int(user["schedule"]["minute"]),user["username"]))
        logger.info('⏰ 已启动定时程序，每天 %02d:%02d 为 %s 打卡' %(int(user["schedule"]["hour"]), int(user["schedule"]["minute"]),user["username"]))
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass


if __name__=="__main__":
    main()