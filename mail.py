#!/usr/bin/python3
 
import smtplib
from email.mime.text import MIMEText
from email.header import Header
 

class Mail(object):
    def __init__(self,logger,receiver):
        self.mail_host="smtp.zju.edu.cn"    # 不一定是浙大邮箱
        self.mail_user="xxxxxxxxxx@zju.edu.cn"    #用户名
        self.mail_pass="XXXXXX"   # 授权码口令，非密码 
        self.sender = 'xxxxxxxxxx@zju.edu.cn'
        self.logger = logger
        self.receiver = receiver

    def send(self,send_message):
        message = MIMEText("错误原因：" + send_message, 'plain', 'utf-8')     
        message['From'] = Header("Auto Checkin Service", 'utf-8')
        message['To'] =  Header("用户", 'utf-8')
        subject = '今日打卡失败'
        message['Subject'] = Header(subject, 'utf-8')
        try:
            smtpObj = smtplib.SMTP_SSL() 
            smtpObj.connect(self.mail_host, 994)    # 994 为 SMTP SSL 端口号
            smtpObj.login(self.mail_user,self.mail_pass)
            smtpObj.sendmail(self.sender, self.receiver, message.as_string())  
        except smtplib.SMTPException as e:
            self.logger.info(e)
