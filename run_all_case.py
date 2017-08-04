# coding:utf-8

import unittest
import baseinfo
import HTMLTestRunner
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from selenium import webdriver


def get_Result(filename):
    driver = webdriver.Firefox()

    # 得到测试报告路径
    result_url = "file://%s" % filename
    driver.get(result_url)
    driver.maximize_window()
    time.sleep(5)
    ratio = driver.find_element_by_css_selector(".btn.btn-primary").text
    total = driver.find_element_by_css_selector(".btn.btn-info").text
    res = driver.find_element_by_css_selector(".btn.btn-danger").text
    print ratio
    print total
    print res
    return ratio, total, res


def send_Mail(file_new, res_ratio, res_total, res_fail):
    f = open(file_new, 'rb')
    # 读取测试报告正文
    mail_body = f.read()
    f.close()
    try:
        smtpConf = smtplib.SMTP(baseinfo.smtp_server, 25)
        sender = baseinfo.smtp_sender
        password = baseinfo.smtp_sender_password
        receiver = baseinfo.smtp_receiver
        smtpConf.login(sender, password)
        msg = MIMEMultipart()
        # 编写html类型的邮件正文，MIMEtext()用于定义邮件正文
        # 发送正文
        text = MIMEText(mail_body, 'html', 'utf-8')
        text['Subject'] = Header('未名企鹅UI自动化测试报告', 'utf-8')
        msg.attach(text)
        # 发送附件  Header()用于定义邮件标题

        # msg['Subject'] = Header('【UI自动化执行结果：' + res_ratio +'；'+ res_total + '】'+ '执行时间： ' + now, 'utf-8')

        if int(res_fail[-1]) > 0:
            conclusion = u'失败'
        else:
            conclusion = u'成功'

        msg['Subject'] = Header(u'【'+ conclusion +u'】'+ now + u'-UI自动化测试执行结果')
        msg_file = MIMEText(mail_body, 'html', 'utf-8')
        msg_file['Content-Type'] = 'application/octet-stream'
        msg_file["Content-Disposition"] = 'attachment; filename="TestReport.html"'
        msg.attach(msg_file)
        msg['From'] = sender
        msg['To'] = ",".join(receiver)
        smtpConf.sendmail(sender, receiver, msg.as_string())
        smtpConf.quit()
        return True
    except smtplib.SMTPException as e:
        print(str(e))
        return False


def all_case():
    case_dir = baseinfo.test_dir
    testcase = unittest.TestSuite()
    discover = unittest.defaultTestLoader.discover(case_dir, pattern="test*.py", top_level_dir=None)
    for test_suit in discover:
        for test_case in test_suit:
            testcase.addTest(test_case)
    return testcase



if __name__ == '__main__':

    now = time.strftime("%Y%m%d%H%M%S")
    report_path = baseinfo.test_report + 'report' + now + '.html'
    fp = open(report_path, 'wb')
    runner = HTMLTestRunner.HTMLTestRunner(stream=fp, title=u'UI自动化测试报告', description=u'用例执行情况', tester=u'孟祥瑞')
    runner.run(all_case())
    fp.close()
    report, total_case, fails = get_Result(report_path)
    email = send_Mail(report_path, report, total_case, fails)
    if email:
        print u'发送成功'
    else:
        print u'发送失败'