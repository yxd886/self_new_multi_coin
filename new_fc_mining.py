import rsa
from base64 import b64decode
import os
import uuid
from fcoin_api import  *
import threading
import base64

from multiprocessing import Process
import multiprocessing

'''
采用AES对称加密算法
'''
# str不是16的倍数那就补足为16的倍数
def add_to_16(value):
    while len(value) % 16 != 0:
        value += '\0'
    return str.encode(value)  # 返回bytes
#加密方法
def encrypt_oracle(text):
    # 秘钥
    key = 'fhkgg'
    # 初始化加密器
    aes = AES.new(add_to_16(key), AES.MODE_ECB)
    #先进行aes加密
    encrypt_aes = aes.encrypt(add_to_16(text))
    #用base64转成字符串形式
    encrypted_text = str(base64.encodebytes(encrypt_aes), encoding='utf-8')  # 执行加密并转码返回bytes
    return(encrypted_text)
#解密方法
def decrypt_oralce(text):
    # 秘钥
    key = 'fhkgg'
    # 初始化加密器
    aes = AES.new(add_to_16(key), AES.MODE_ECB)
    #优先逆向解密base64成bytes
    base64_decrypted = base64.decodebytes(text.encode(encoding='utf-8'))
    #执行解密密并转码返回str
    decrypted_text = str(aes.decrypt(base64_decrypted),encoding='utf-8').replace('\0','')
    return(decrypted_text)



class Section:
#粘贴的回调函数
    def onPaste(self):
        try:
            self.text = win.clipboard_get()
            #获得系统粘贴板内容
        except tkinter.TclError:
            pass
        #防止因为粘贴板没有内容报错
        show.set(str(self.text))
        #在文本框中设置刚刚获得的内容

    def onPaste1(self):
        try:
            self.text = win.clipboard_get()
            #获得系统粘贴板内容
        except tkinter.TclError:
            pass
        #防止因为粘贴板没有内容报错
        show1.set(str(self.text))
        #在文本框中设置刚刚获得的内容

    def onPaste2(self):
        try:
            self.text = win.clipboard_get()
            #获得系统粘贴板内容
        except tkinter.TclError:
            pass
        #防止因为粘贴板没有内容报错
        show2.set(str(self.text))
        #在文本框中设置刚刚获得的内容

#复制的回调函数
    def onCopy(self):
        self.text = T.get(1.0,tkinter.END)
        #获得文本框内容
        win.clipboard_append(self.text)
        #添加至系统粘贴板


def get_mac_address():
    node = uuid.getnode()
    mac = uuid.UUID(int = node).hex[-12:]
    return mac

def check_and_save():
    signature = entry1.get().strip().encode()
    #print("Signature")
    #print(signature)
    new_msg = msg1+gap+"lyaegjdfuyeu"
    try:
        rsa.verify(new_msg.encode(), b64decode(signature), public)
    except:
        print("wrong license!!!")
        a = input("")
        sys.exit()
    with open(yanzheng_file_name, 'w') as f:
        f.write(encrypt_oracle(msg1+":::::"+signature.decode()))
        #f.write("\n")
        #f.write(encrypt_oracle(signature.decode()))
        #f.write(msg1+"\n")
        #f.write(signature.decode())
    win.destroy()


def buy_main_body(mutex2,api,bidirection,partition,_money,_coin,min_size,money_have,coin_place):
    market = _coin + _money
    buy_id1 = "-1"
    buy_id2 = "-1"
    need_buy = False
    need_sell =False
    min_price_tick = 1/(10**api.price_decimal[market])
    if bidirection==1 or bidirection==3:
        need_buy = True
    if bidirection==2 or bidirection==3:
        need_sell = True
    while True:
        try:
            api.wallet_to_trade("usdt", 5)
            api.cancel_all_pending_order(market)
            counter=0
            current_time = time.time()
            obj = api.get_depth(market)
            buy1 = obj["bids"][0*2]
            ask1 = obj["asks"][0*2]
            #if need_buy:
             #   api.take_order(market, "buy", buy1,min_size,coin_place)
            #if need_sell:
            #    api.take_order(market, "sell", ask1, min_size, coin_place)
            for i in range(9):
                buy_price=buy1-i*min_price_tick
                sell_price=ask1+i*min_price_tick
                if need_buy:
                    api.take_order(market, "buy", buy_price, min_size*(i+1), coin_place)
                    time.sleep(0.1)
                if need_sell:
                    api.take_order(market, "sell", sell_price, min_size*(i+1), coin_place)
                    time.sleep(0.1)

            money, coin, freez_money, freez_coin = api.get_available_balance(_money, _coin)

            buy_price = buy1 - 9 * min_price_tick
            sell_price = ask1 + 9 * min_price_tick

            if need_buy:
                current_money_have = money_have - coin*buy1
                available_coin_space = current_money_have/buy_price
                money1 = min(money_have,money)
                coin1_can_buy = money1/ buy_price
                print("level 1 coin can buy:%f"%coin1_can_buy)
                print("available_coin1_space:%f"%available_coin_space)
                if available_coin_space>min_size and coin1_can_buy>min_size:
                    print("take buy order 1")
                    buy_id1 = api.take_order(market, "buy", buy_price,
                                            (min(available_coin_space,coin1_can_buy)),
                                            coin_place)
            if need_sell:
                coin1_can_sell = coin
                if coin1_can_sell>min_size:
                    sell_id_1 = api.take_order(market, "sell", sell_price, coin1_can_sell,coin_place)

            # api.balance_account("QC","USDT")
        except Exception as ex:
            print(sys.stderr, 'zb request ex: ', ex)
            continue
        interval = 0.1
        while True:
            try:
                print("counter:%d"%counter)
                obj = api.get_depth(market)
                buy5 = obj["bids"][4 * 2]
                buy15 = obj["bids"][14 * 2]
                buy4 = obj["bids"][3 * 2]
                buy11 = obj["bids"][10 * 2]
                buy10 = obj["bids"][9 * 2]
                ask5 = obj["asks"][4 * 2]
                ask15 = obj["asks"][14 * 2]
                ask4 = obj["asks"][3 * 2]
                ask11 = obj["asks"][10 * 2]
                ask10 = obj["asks"][9 * 2]


                buy_upper1 = buy5
                buy_lower1 = buy15
                sell_upper1 = ask15
                sell_lower1 = ask5

                print("buy4:%f" % buy4)
                print("buy10:%f" % buy10)
                print("sell4:%f"% ask4)
                print("sell10:%f" % ask10)
                print("trade pair:"+market)
                restart = False

                if counter>300:
                    restart = True
                    print("cancel reason 1")
                elif need_buy and(buy_price>buy_upper1):
                    restart = True
                    print("cancel reason 3")
                elif need_buy and (buy_price<buy_lower1):
                    restart = True
                    print("cancel reason 4")
                elif need_sell and (sell_price>sell_upper1):
                    restart = True
                    print("cancel reason 5")
                elif need_sell and (sell_price<sell_lower1):
                    restart = True
                    print("cancel reason 6")

                counter = time.time()-current_time
                time.sleep(interval)
                if restart:
                    buy_id1="-1"
                    buy_id2="-1"
                    api.cancel_all_pending_order(market)
                    time.sleep(0.5)
                    break

            except Exception as ex:
                print(sys.stderr, 'zb request ex: ', ex)
                buy_id1 = "-1"
                buy_id2 = "-1"
                break




def load_record():
    global load_access_key,load_access_secret,load_money,load_coin,load_parition,load_total_money,load_bidirection,load_coin_place
    with open(config_file, 'r') as f:
        tmp = f.read()
        tmp = decrypt_oralce(tmp)
        parameters = tmp.split(gap)
        load_access_key = parameters[0]
        load_access_secret = parameters[1]
        load_money = parameters[2]
        load_coin = parameters[3]
        load_parition = parameters[4]
        load_total_money = parameters[5]
        load_bidirection = parameters[6]
        load_coin_place = parameters[7]




def tick(load_access_key, load_access_secret, load_money, load_coin, load_parition, load_total_money, load_bidirection, load_coin_place):
    try:
        mutex2 = threading.Lock()
        access_key = load_access_key.strip()
        access_secret = load_access_secret.strip()
        _money =load_money.strip().lower()
        tmp =load_coin.strip().lower()
        if " "in tmp:
            coins =tmp.split(" ")
        else:
            coins = [tmp]
        markets = [_coin+_money for _coin in coins]
        print(markets)
        partition = int(load_parition.strip())
        assert(partition!=0)
        money_have = float(load_total_money.strip())

        market_exchange_dict = {"bbgcusdt":"renren","btmusdt":"jingxuanremenbi","zipusdt":"servicex","fiusdt":"fiofficial","dogeusdt":"tudamu","aeusdt":"servicex","zrxusdt":"tudamu","batusdt":"jiucai","linkusdt":"jingxuanremenbi","icxusdt":"allin","omgusdt":"ninthzone","zilusdt":"langchao"}

        bidirection=int(load_bidirection.strip())
        coin_place_list = [market_exchange_dict.get(item,"main") for item in markets]



        api = fcoin_api(access_key, access_secret)
        api.wallet_to_trade("usdt", 40)
        min_size=api.set_demical(_money, coins)
        print("start cancel existing pending orders")
        for market in markets:
            time.sleep(0.1)
            api.cancel_all_pending_order(market)
        print("cancel pending orders completed")
        for i, market in enumerate(markets):
            time.sleep(0.1)
            thread = threading.Thread(target=buy_main_body,args=(mutex2,api,bidirection,partition,_money,coins[i],min_size[market],money_have/len(markets),coin_place_list[i]))
            thread.setDaemon(True)
            thread.start()
        time.sleep(3600)
        print("tick exit!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

    except Exception as ex:
        print(sys.stderr, 'tick: ', ex)
        #a= input()



def init_sell(apikey,apisecret,total_load_coin,load_money):
    access_key = apikey.strip()
    access_secret = apisecret.strip()
    _money =load_money.strip().lower()
    tmp =total_load_coin.strip().lower()
    if " "in tmp:
        coins =tmp.split(" ")
    else:
        coins = [tmp]
    markets = [_coin+_money for _coin in coins]
    print(markets)
    partition = int(load_parition.strip())
    assert(partition!=0)
    api = fcoin_api(access_key, access_secret)
    min_size=api.set_demical(_money, coins)
    for market in markets:
        print("cancel"+market)
        api.cancel_all_pending_order(market)
        time.sleep(0.5)
    for _coin in coins:
        market=_coin+_money
        obj = api.get_depth(market)
        buy13 = obj["bids"][12 * 2]
        money, coin, freez_money, freez_coin = api.get_available_balance(_money, _coin)
        if coin>min_size[market]:
            api.take_order(market, "sell", buy13, coin, coin_place)
            time.sleep(0.5)

if __name__ == '__main__':
    multiprocessing.freeze_support()

    print("begin")

    load_access_key, load_access_secret, load_money, load_coin, load_parition, load_total_money, load_bidirection, load_coin_place = None, None, None, None, None, None, None, None
    win1 = None
    license_day=0
    emerency = False

    mutex1 = threading.Lock()
    mutex3 = threading.Lock()
    mutex4 = threading.Lock()
    mutex5 = threading.Lock()

    access_key = None
    access_secret = None

    _money =None
    coins = None
    min_size = None
    money_have = None

    api = None
    partition=0
    bidirection=3
    coin_place = "main"
    total_amount_limit = 0
    yanzheng_file_name = "multi_coin_yanzheng.txt"
    gap = "multicoin"
    config_file = "multi_coinlastconfig.txt"
    multi_config_file = "multi_account_config.txt"

    need_exit = False
    coins = list()
    coin_place_list = list()
    markets = list()


    load_money = "usdt"
    total_load_coin="eos etc bch trx xrp xlm ft zec ada dash bsv iota"
    load_coin = "eth btc ltc"
    load_parition="2"
    load_total_money="100"
    load_bidirection="3"
    load_coin_place="1"
    processes =list()
    with open(multi_config_file, "r") as f:
        local_thread=list()
        for line in f.readlines():
            apikey = line.split("#")[0]
            apisecret = line.split("#")[1]
            total_money = line.split("#")[2]
            thread = threading.Thread(target=init_sell,args=(apikey,apisecret,total_load_coin,load_money))
            thread.setDaemon(True)
            thread.start()
            local_thread.append(thread)
        for _th in local_thread:
            _th.join()
    while True:
        with open(multi_config_file, "r") as f:
            for line in f.readlines():
                apikey = line.split("#")[0]
                apisecret = line.split("#")[1]
                total_money = line.split("#")[2]
                p1 = Process(target=tick, args=(
                    apikey, apisecret, load_money, load_coin, load_parition, total_money,
                    load_bidirection, load_coin_place))
                p1.daemon = True
                p1.start()
                processes.append(p1)
        processes[0].join(timeout=3600)
        for p in processes:
            p.terminate()
        processes=[]

  #  period_restart()









