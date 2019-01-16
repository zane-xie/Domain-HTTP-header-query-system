#!/usr/bin/python
#coding=utf-8
# by xz
# 2018-11-12
# version v1.0

import socket
import re
import json
import os
import time
import datx
import threading
import urllib2
import sys
import subprocess
import random


# 定义api的基本数据
sk = socket.socket()
ip_port = ('127.0.0.1',1669)
sk.bind(ip_port)
sk.listen(20)


# 兼容中文字符串
defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
        reload(sys)
        sys.setdefaultencoding(defaultencoding)


# 定义一个函数，用于获取获取ip对应的区域名称(精确到市)
def get_ip_mess(ipaddr):
        # 获取ip区域
        try:
                c = datx.City("/home/app/ipip/mydata4vipday2.datx")
                mess_ip = (c.find(ipaddr))
                county = mess_ip[0]                        # 输出国家
                pro = mess_ip[1]                           # 输出省份
                city = mess_ip[2]                          # 输出城市
                isp = mess_ip[4]                           # 输出运营商
                ip_mess = county+'.'+pro+'.'+city+'.'+isp
        except:
                ip_mess = "IP归属地未知"

        return ip_mess



# 定义一个函数，用于获取A记录
def get_ip_digmess(localip,domain,wr_filename,digdns):
        # 定义变量
        os.environ['dig_domain']=str(domain)
        os.environ['dig_ip']=str(localip)
        os.environ['dig_dns']=str(digdns)

	cmd = "/home/app/ipip/dig @119.29.29.29 $dig_domain +subnet=$dig_ip +tries=1 +time=2 |egrep -v '^;|^$|^\.' | awk '/[0-9]\.[0-9]/ {print $NF}'"
	p = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
	out,err = p.communicate()
	for line in out.splitlines():
		if '.' in str(line):
			h = open(wr_filename, 'a')
			h.write(str(line))
			h.write('\n')
			h.close()
		else:
			h = open(wr_filename, 'a')
			h.write('notfind')
			h.write('\n')
			h.close()


# 定义一个函数，用于获取域名https相关信息
def get_https_mess(ip,url,allwr_filename):
	# 定义变量
	os.environ['curl_ip']=str(ip)
	os.environ['curl_url']=str(url)

	# 获取ip所在区域
	localip_qy = get_ip_mess(str(ip))

	# 异常兼容
	try:
		cmd = "echo | openssl s_client -servername $curl_url -connect $curl_ip:443 2>/dev/null |openssl x509 -noout -dates |grep 'After'| awk -F '=' '{print $2}'| awk -F ' +' '{print $0 }'"
		p = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
		out,err = p.communicate()
		for line in out.splitlines():
			if ':' in line:
				outmess = line
				# 将信息保存到本地 allwr_filename
				all_mess = '<tr><td>' + str(ip) + '</td><td>' + localip_qy + '</td><td>' + outmess + '</td></tr>'
				h = open(allwr_filename, 'a')
				h.write(all_mess)
				h.close()
			else:
				outmess = '请求超时或其它错误'
				# 将信息保存到本地 allwr_filename
				all_mess = '<tr><td>' + str(ip) + '</td><td>' + localip_qy + '</td><td>' + outmess + '</td></tr>'
				h = open(allwr_filename, 'a')
				h.write(all_mess)
				h.close()
	except:
		outmess = '请求超时或其它错误'
		# 将信息保存到本地 allwr_filename
		all_mess = '<tr><td>' + str(ip) + '</td><td>' + localip_qy + '</td><td>' + outmess + '</td></tr>'
		h = open(allwr_filename, 'a')
		h.write(all_mess)
		h.close()
			


# 定义一个函数，用于发起curl请求
def get_curl_mess(key,ip,url,allwr_filename):
	# 定义变量
	os.environ['curl_key']=str(key)
	os.environ['curl_ip']=str(ip)
	os.environ['curl_url']=str(url)
	
	# 获取ip所在区域
	localip_qy = get_ip_mess(str(ip))

	# 异常兼容
	try:
		# 针对http和https做区分处理
		if 'https' in str(url):
			domain = str(url).split('/')[2]
			os.environ['curl_domain']=str(domain)
			cmd = "curl $curl_url -s -I -X HEAD --connect-timeout 2 -m 2 --retry 0 --resolve $curl_domain:443:$curl_ip|grep -i $curl_key|head -n 1"
		else:
			cmd = "curl $curl_url -s -I -X HEAD --connect-timeout 2 -m 2 --retry 0 -x $curl_ip:80|grep -i $curl_key|head -n 1"
	
		p = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
		out,err = p.communicate()
		for line in out.splitlines():
			if 'H' in line or 'g' in line or 't' in line:
				outmess = line
				# 将信息保存到本地 allwr_filename
				all_mess = '<tr><td>' + str(ip) + '</td><td>' + localip_qy + '</td><td>' + outmess + '</td></tr>'
				h = open(allwr_filename, 'a')
				h.write(all_mess)
				h.close()
			else:
				outmess = '请求超时或其它错误'
				# 将信息保存到本地 allwr_filename
				all_mess = '<tr><td>' + str(ip) + '</td><td>' + localip_qy + '</td><td>' + outmess + '</td></tr>'
				h = open(allwr_filename, 'a')
				h.write(all_mess)
				h.close()
	except:
		outmess = '请求超时或其它错误'
		# 将信息保存到本地 allwr_filename
		all_mess = '<tr><td>' + str(ip) + '</td><td>' + localip_qy + '</td><td>' + outmess + '</td></tr>'
		h = open(allwr_filename, 'a')
		h.write(all_mess)
		h.close()
			
	

# 定义一个计算函数，多线程执行任务
def get_all_mess(domain,key,url):
        # 定义一个全国各个区域的ip列表
        iplist = [ 
        "219.147.198.242",
        "202.97.224.69",
        "211.137.241.36",
        "219.149.194.55",
        "202.98.0.68",
        "211.141.16.99",
        "219.148.204.66",
        "202.96.64.68",
        "211.137.32.188",
        "1.180.207.132",
        "202.99.224.67",
        "211.138.91.1",
        "202.106.46.151",
        "202.106.169.115",
        "211.136.17.107",
        "221.238.23.102",
        "202.99.96.68",
        "211.137.160.5",
        "222.222.202.202",
        "202.99.166.4",
        "111.11.4.239",
        "219.146.0.130",
        "202.102.134.68",
        "218.201.96.130",
        "219.149.135.188",
        "202.99.216.113",
        "211.138.106.2",
        "123.160.10.66",
        "202.102.224.68",
        "211.138.24.66",
        "218.30.19.40",
        "221.11.1.67",
        "211.137.130.2",
        "222.75.152.129",
        "221.199.12.157",
        "218.203.123.116",
        "202.100.64.66",
        "221.7.34.10",
        "218.203.160.194",
        "61.128.114.133",
        "221.7.1.20",
        "218.202.152.130",
        "202.98.224.69",
        "221.13.65.56",
        "211.139.73.34",
        "202.100.128.68",
        "221.207.58.58",
        "211.138.75.123",
        "202.98.96.68",
        "211.137.96.205",
        "183.221.253.100",
        "222.172.200.68",
        "221.3.131.11",
        "211.139.29.150",
        "61.128.128.68",
        "221.7.92.86",
        "218.201.17.1",
        "119.1.109.109",
        "211.92.136.81",
        "211.139.5.29",
        "202.103.224.68",
        "221.7.128.68",
        "211.138.240.100",
        "202.96.128.68",
        "210.21.4.130",
        "211.136.20.203",
        "202.100.192.68",
        "221.11.132.2",
        "221.11.141.9",
        "202.103.24.68",
        "218.104.111.112",
        "211.137.58.20",
        "202.102.192.68",
        "218.104.78.2",
        "211.138.180.3",
        "218.2.135.1",
        "58.240.57.33",
        "112.4.16.200",
        "118.118.118.51",
        "140.207.223.153",
        "211.136.112.50",
        "202.101.224.69",
        "220.248.192.12",
        "211.141.90.68",
        "222.246.129.80",
        "58.20.126.98",
        "211.142.211.124",
        "202.101.172.48",
        "221.12.102.227",
        "211.140.10.2",
        "202.101.107.54",
        "218.104.128.106",
        "211.138.151.66",
        "211.161.124.199",
        "124.14.16.3",
        "211.167.230.100",
        "101.47.94.10",
        "175.188.188.135",
        "211.162.31.80",
        "211.162.32.116",
        "211.162.208.12",
        "211.162.130.33",
        "202.112.30.157",
        "202.113.48.10",
        "202.120.2.100",
        "202.115.32.36",
        "211.69.143.1",
        "23.236.115.24",
        "128.1.64.246",
        "23.236.107.67",
        "107.155.16.200",
        "128.1.87.249",
        "202.116.0.1"
        ]

	# 获取当前时间戳
	now_time_sjc = int(time.time())
	# 定义每次任务存储路径 /home/app/weball/tmp/get-域名-时间戳
	wr_filename = '/home/app/weball/tmp/get-' + str(domain) + '-' + str(now_time_sjc)
	
	# 多线程执行任务
	for i in iplist:
		# 随机使用dns
		dnslist = ["119.28.28.28","119.29.29.29","182.254.116.116","182.254.118.118"]
		digdns = random.sample(dnslist,1)[0]
		t = threading.Thread(target=get_ip_digmess,args=(i,domain,wr_filename,digdns))
		mess = t.start()

	# 针对得出ip进行去重
	allip = []
	f = open(wr_filename, 'r')
	for line in f:
		if '.' in line:
			allip.append(str(line))
	f.close()
	allip_list = list(set(allip))
	# 删除刚刚生成的文件
	os.remove(wr_filename)

	# 定义返回文件名
	allwr_filename = '/home/app/weball/tmp/all-' + str(domain) + '-' + str(now_time_sjc)
	all_mess = '<table border="1" cellspacing="0"><tr><th>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;服务端IP地址&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</th><th>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;服务端IP归属地&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</th><th>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'+ str(key) + '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</th></tr>'

	# 针对http和https分别做处理
	if key == "https-crt-expire-time":
		# 多线程循环发起curl请求
		for x in allip_list:
			serip = x.split('\n')[0].strip()
			t = threading.Thread(target=get_https_mess,args=(serip,url,allwr_filename))
			mess = t.start()
	else:
		# 多线程循环发起curl请求
		for x in allip_list:
			serip = x.split('\n')[0].strip()
			t = threading.Thread(target=get_curl_mess,args=(key,serip,url,allwr_filename))
			mess = t.start()

	# 等待其它线程执行完成
	time.sleep(3)

	# 读取返回结果
	with open(allwr_filename) as f:
		for line in f:
			all_mess += line
	return all_mess
	os.remove(allwr_filename)



# 定义main函数
def main():
        while True:
                conn,address = sk.accept()
                # 获取客户所带数据，并进行相关判断
                data = conn.recv(1024)
                # 利用正则获取自己想要的相关数据
                p = re.compile(r'\n')
                mess = p.split(data)
		
                puttype = mess[-3].split('\r')[0].strip()
                proxy = mess[-7].split('\r')[0].strip()
                puturl = mess[-11].split('\r')[0].strip()

		try:
			# 进行数据返回
			weballmess = get_all_mess(proxy,puttype,puturl)
			content = 'HTTP/1.1 200 ok\r\nContent-Type: text/html; charset=UTF-8\r\n\r\n'
			content += '<p><font color="purple" size="域名头信息查询系统"></p>'
			content += str(weballmess)
			conn.send(content.encode('utf-8'))
			conn.close()
		except:
			content = 'HTTP/1.1 200 ok\r\nContent-Type: text/html; charset=UTF-8\r\n\r\n'
			content += '<p><font color="red" size="3">请求出错-该域名没有返回相关正确头信息 ^_^</p>'
			conn.send(content.encode('utf-8'))
			conn.close()


# 执行main函数
if __name__ == "__main__":
        main()





