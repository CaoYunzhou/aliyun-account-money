#!/bin/python3
# coding: utf-8
import time
import datetime
import requests
from datetime import datetime
import dateutil.relativedelta
import json
import os
from dotenv import load_dotenv
import math
import dateutil
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkcore.auth.credentials import AccessKeyCredential
from aliyunsdkcore.auth.credentials import StsTokenCredential
from aliyunsdkbssopenapi.request.v20171214.QueryAccountTransactionsRequest import QueryAccountTransactionsRequest
from aliyunsdkbssopenapi.request.v20171214.QueryAccountBalanceRequest import QueryAccountBalanceRequest
from aliyunsdkbssopenapi.request.v20171214.QueryAccountBillRequest import QueryAccountBillRequest
from aliyunsdkbssopenapi.request.v20171214.QueryInstanceGaapCostRequest import QueryInstanceGaapCostRequest
# from aliyunsdkbssopenapi.request.v20171214.QueryMonthlyBillRequest import QueryMonthlyBillRequest
from aliyunsdkbssopenapi.request.v20171214.QueryBillOverviewRequest import QueryBillOverviewRequest


update_times = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

load_dotenv()
sk = os.environ.get('SK')
ak = os.environ.get('AK')
webhook_url = os.environ.get('WEBHOOK_URL')
secret = os.environ.get('SECRET')

print(ak, sk, webhook_url, secret)


def get_before_day():
    import datetime
    before_days = str(datetime.date.today() - datetime.timedelta(days=1))
    return before_days


print(get_before_day())


def get_now_day():
    import datetime
    days = str(datetime.date.today())
    return days


print(get_now_day())


def get_delay_month():
    today_date = datetime.now().date()
    last_month = str(
        today_date - dateutil.relativedelta.relativedelta(months=1))
    # print(type(last_month))
    return last_month[:-3]


print(get_delay_month())


# 获取余额信息
def get_account_Amount():
    credentials = AccessKeyCredential(ak, sk)
    client = AcsClient(region_id='cn-shanghai', credential=credentials)
    request = QueryAccountBalanceRequest()
    request.set_accept_format('json')
    response = client.do_action_with_exception(request)
    result = json.loads(response)['Data']['AvailableCashAmount']
    return result


print(get_account_Amount())


# 获取上月度信息
def get_mounth_Transactions():
    total_memory = 0
    credentials = AccessKeyCredential(ak, sk)
    client = AcsClient(region_id='cn-shanghai', credential=credentials)
    request = QueryBillOverviewRequest()
    request.set_accept_format('json')
    request.set_BillingCycle(get_delay_month())
    response = client.do_action_with_exception(request)
    response = json.loads(response)
    result = response['Data']['Items']['Item']
    for i in result:
        total_memory += i['CashAmount']
    return total_memory
    # return response['Data']['NewInvoiceAmount']


print(get_mounth_Transactions())

# 获取昨日余额


def get_day_Transactions():

    credentials = AccessKeyCredential(ak, sk)
    client = AcsClient(region_id='cn-shanghai', credential=credentials)

    request = QueryAccountTransactionsRequest()
    request.set_accept_format('json')  # type: ignore
    # request.set_TransactionType("Consumption")

    request.set_CreateTimeStart(get_before_day()+"T00:00:00Z")  # type: ignore
    request.set_CreateTimeEnd(get_now_day()+"T00:00:00Z")  # type: ignore
    request.set_PageSize(100)  # type: ignore
    response = client.do_action_with_exception(request)  # type: ignore
    response = json.loads(response)  # type: ignore
    get_total = response['Data']['TotalCount']
    print(get_total)
    result_limit = math.ceil(get_total / 100)
    print(result_limit)

    sum_total = 0
    for i in range(result_limit + 3):
        if i != 0:
            request.set_PageNum(i)  # type: ignore
            response = client.do_action_with_exception(request)  # type: ignore
            response = json.loads(response)  # type: ignore
            result = response['Data']['AccountTransactionsList']['AccountTransactionsList']
            # print(result)
            for i in result:
                if i['TransactionType'] == "Consumption":
                    # print(float(i['Amount']))
                    sum_total += float(i['Amount'])
    print(sum_total)
    return sum_total

# 发送钉钉信息


def dingding_webhook():
    import time
    import hmac
    import hashlib
    import base64
    import urllib.parse

    timestamp = str(round(time.time() * 1000))
    secret_enc = secret.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc,
                         digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    print(timestamp)
    print(sign)

    url = webhook_url + "&timestamp=" + timestamp + "&sign=" + sign
    print(url)
    headers = {
        'Content-Type': 'application/json',
    }

    data = '{ "msgtype": "markdown", "markdown": { "title": "title", "text": %s } }' % mark_down()
    print(data)
    # print(type(mark_down()))
    response = requests.post(
        url=url, headers=headers, data=data)
    print(response.text)

# 数据格式化markdown


def mark_down():

    Account_id = "账户:阿里云账户余额\n"
    # print(Account_id)
    Account_amount = "> ###### 账户余额: **%s CNY**\n" % get_account_Amount()
    # Account_amount_type = "> ###### 币种: CNY\n"
    # 日消费
    split_line = "> ###### ---------------------------------\n"
    monty_day_account = "> ###### 昨日消费总额 [ %s ]: **%s**\n" % (
        get_before_day(), math.ceil(get_day_Transactions()))
    # # 月消费
    split_line = "> ###### ---------------------------------\n"
    monty_account = "> ###### 上月消费总额 [ %s ]: **%s** \n" % (
        get_delay_month(), math.ceil(get_mounth_Transactions()))
    # # 汇报时间
    up_time = "> ###### 汇总报告时间: %s" % update_times
    mark_mes = Account_id + Account_amount + split_line + \
        monty_day_account + split_line + monty_account + split_line+up_time
    return json.dumps(mark_mes)


# print(mark_down())
dingding_webhook()
