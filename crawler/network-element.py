from selenium import webdriver
from browsermobproxy import Server
import time
import json

PATH_PROXY = r'toolset\browsermob\bin\browsermob-proxy.bat'
PATH_CHROMIUM_DRIVER = r'toolset\chromium\chromedriver.exe'

server = Server(path = PATH_PROXY, options={'port':9200})
server.start()
proxy = server.create_proxy()

# Options
options = webdriver.ChromeOptions()
#options.add_argument('--headless') # 开启无界面模式
#options.add_argument('--disable-gpu') # 禁用显卡
#options.add_argument('blink-settings=imagesEnabled=false')
options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36") # 替换UA
options.add_argument('--ignore-certificate-errors')
print('using proxy: ' + proxy.proxy)
options.add_argument('--proxy-server={0}'.format(proxy.proxy))
options.add_argument('window-size=300,600')
# options.add_argument('start-fullscreen')
# options.add_argument('kiosk') 

driver = webdriver.Chrome(executable_path = PATH_CHROMIUM_DRIVER, chrome_options=options)

proxy.new_har(options={'captureHeaders': True, 'captureContent': True,})
driver.get("https://www.ai66.cc/e/DownSys/play/?classid=8&id=12687&pathid1=0&bf=0")
time.sleep(10)

result = proxy.har
with open('Networks.js', 'w', encoding='utf-8') as f:
	f.write(json.dumps(result['log']['entries'], indent=2))
	
server.stop()
driver.quit()