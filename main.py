from daka import DaKa
from halo import Halo
from apscheduler.schedulers.blocking import BlockingScheduler
import logging
import getpass
import time, datetime, os, sys
import requests, json, re

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
    try:
        dk.login()
        spinner.succeed('已登录到浙大统一身份认证平台')
        logger.info('已登录到浙大统一身份认证平台')
    except Exception as err:
        spinner.fail(str(err))
        logger.info(str(err))
        return
    
    spinner.start(text='正在获取个人信息...')
    logger.info('正在获取个人信息...')
    try:
        dk.get_info()
        spinner.succeed('%s %s同学, 你好~' %(dk.info['number'], dk.info['name']))
        logger.info('%s %s同学, 你好~' %(dk.info['number'], dk.info['name']))
    except Exception as err:
        spinner.fail('获取信息失败，请手动打卡，更多信息: ' + str(err))
        logger.info('获取信息失败，请手动打卡，更多信息: ' + str(err))
        return    
    
    spinner.start(text='正在为您打卡打卡打卡')
    logger.info('正在为您打卡打卡打卡')
    try:
        res = dk.post()
        if str(res['e']) == '0':
            spinner.stop_and_persist(symbol='🦄 '.encode('utf-8'), text='已为您打卡成功！')
            logger.info('已为您打卡成功！')
        else:
            spinner.stop_and_persist(symbol='🦄 '.encode('utf-8'), text=res['m'])
            logger.info(res['m'])
    except:
        spinner.fail('数据提交失败')
        logger.info('数据提交失败')
        return 


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