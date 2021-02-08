from daka import DaKa
from mail import Mail
from halo import Halo
from apscheduler.schedulers.blocking import BlockingScheduler
import logging
import getpass
import time, datetime, os, sys
import requests, json, re

def doDaka(username, password,logger,mail_on):
    if mail_on:
        mail = Mail(logger,username+"@zju.edu.cn")
    logger.info("🚌 打卡任务启动")
    dk = DaKa(username, password)
    try:
        dk.login()
        logger.info('已登录到浙大统一身份认证平台')
    except Exception as err:
        logger.info(str(err))
        if mail_on:
            mail.send('用户名密码错误')
        return
    
    logger.info('正在获取个人信息...')
    try:
        dk.get_info()
        logger.info('%s %s同学, 你好~' %(dk.info['number'], dk.info['name']))
    except Exception as err:
        logger.info('获取信息失败，请手动打卡，更多信息: ' + str(err))
        if mail_on:
            mail.send('获取信息失败，请手动打卡，更多信息: ' + str(err))
        return    
    
    try:
        res = dk.post()
        if str(res['e']) == '0':
            logger.info('已为您打卡成功！')
        else:
            logger.info(res['m'])
            if mail_on:
                mail.send(res['m'])
    except:
        logger.info('数据提交失败')
        if mail_on:
            mail.send('数据提交失败')
        return 


def main(mail_on):
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
    scheduler = BlockingScheduler(timezone="Asia/Shanghai")
    for user in users:
        scheduler.add_job(doDaka, 'cron', args=[user["username"], user["password"],logger,mail_on], hour=user["schedule"]["hour"], minute=user["schedule"]["minute"])
        logger.info('⏰ 已启动定时程序，每天 %02d:%02d 为 %s 打卡' %(int(user["schedule"]["hour"]), int(user["schedule"]["minute"]),user["username"]))
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass


if __name__=="__main__":
    mail_on = False # 需要启用邮件提醒功能将这里改为 True
    main(mail_on)
