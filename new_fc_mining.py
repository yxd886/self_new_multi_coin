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

    need_balance = True
    cell_num=20
    market = _coin + _money
    stamp = int(time.time())
    time_local = time.localtime(stamp)
    new_hour = int(time_local.tm_hour)
    min_price_tick = 0.005
    if new_hour == 0:
        daily_restart = True
    else:
        daily_restart = False
    while True:
        try:

            print("in init market")
            price_list = list()
            sell_order_list = list()
            buy_order_list = list()
            tmp_buy_order_list = list()
            tmp_sell_order_list = list()

            api.cancel_all_pending_order(market)



            obj = api.get_depth(market)
            ask1 = obj["asks"][0 * 2]
            buy1 = obj["bids"][0*2]

            print("trade_pair:%s"%(market))
            base_price = buy1 - (cell_num / 2) * min_price_tick*buy1

            money, coin, freez_money, freez_coin = api.get_available_balance(_money, _coin)
            remain_coin = coin
            for i in range(cell_num):
                price = base_price + base_price*min_price_tick*i
                price_list.append(price)

            buy_lower = min(price_list)
            sell_upper = max(price_list)
            if max(price_list)<ask1:
                gap = 100
            elif min(price_list)>ask1:
                gap = 0
            else:
                gap = 99
                for i in range(len(price_list)-1):
                    if price_list[i]<ask1 and price_list[i+1]>=ask1:
                        gap = i
                        break
                gap+=1
            print("gap:%d"%gap)

            coin_need = coin
            min_coin_need = len( price_list[gap:])*min_size
            min_money_need_for_sell = 0
            sell_step = 0


            if gap<cell_num:

                for price in price_list[gap:]:
                    min_money_need_for_sell+= price*min_size

                money_for_sell = (len( price_list[gap:])/cell_num)*min(money_have,money+coin*buy1)


                coin_need = (money_for_sell/min_money_need_for_sell)*min_coin_need if min_money_need_for_sell>0 else 0
                print("coin need:",coin_need)


            if need_balance:
                if remain_coin-coin_need>2*min_size:
                    api.take_order(market,"sell",buy1-buy1*0.01,remain_coin-coin_need-min_size,coin_place)
                elif remain_coin<coin_need:
                    api.take_order(market,"buy",ask1+ask1*0.01,coin_need-remain_coin+min_size,coin_place)
            time.sleep(1)

            money, coin, freez_money, freez_coin = api.get_available_balance(_money, _coin)
            sell_step = max((coin / len(price_list[gap:])) + 1 / (10 ** api.amount_decimal[market]), min_size)

            print("sell step:",sell_step)

            new_list = list()
            buy_step=0

            if gap>0:
                new_list =price_list[:gap]
                new_list.reverse()
                min_money_need_for_buy=0
                #print(new_list)
                money_for_buy = (len( new_list)/cell_num)*min(money_have,money+coin*buy1)
                print(money_for_buy)
                for price in new_list:
                    min_money_need_for_buy+= price*min_size

                if money_for_buy>=min_money_need_for_buy:
                    buy_step = (money_for_buy/min_money_need_for_buy)*min_size+1/(10**api.amount_decimal[market])
                else:
                    buy_step = min_size
            print("buy_step:", buy_step)
            _counter=0
            for price in new_list:
                if price<ask1:
                    size = buy_step
                    id = api.take_order(market,"buy",price,size,coin_place)
                    if id!="-1":
                        _counter=0
                        buy_order_list.append({"id":id,"pair":(market,"sell",price+min_price_tick*price/2,size,coin_place),"self":(market,"buy",price,size,coin_place)})
                    else:
                        _counter+=1
                        if _counter>=3:
                            break

            _counter = 0
            if gap<cell_num:
                for price in price_list[gap:]:
                    if price>ask1:
                        size = sell_step
                        id = api.take_order(market,"sell",price,size,coin_place)
                        if id !="-1":
                            _counter = 0
                            sell_order_list.append({"id":id,"pair":(market,"buy",price-min_price_tick*price/2,size,coin_place),"self":(market,"sell",price,size,coin_place)})
                        else:
                            _counter += 1
                            if _counter >= 3:
                                break


        except Exception as ex:
            print(sys.stderr, 'in init: ', ex)
            print("exception")
            continue
        _start_time = time.time()
        while True:
            try:

                obj = api.get_depth(market)
                ask1 = obj["asks"][0 * 2]
                buy1 = obj["bids"][0 * 2]
                print("current ask:%f"%ask1)
                print("current buy:%f"%buy1)
                print("trade_pair:%s"%market)
                print("time spent:%f seconds"%(time.time()-_start_time))
                print("len of buy_order_list:", len(buy_order_list))
                if len(buy_order_list)>0:
                    buy_item =  buy_order_list[0]
                    buy_id_to_monitor =buy_item["id"]
                    time.sleep(1)
                    if api.is_order_complete(market,buy_id_to_monitor):
                        _market = buy_item["pair"][0]
                        _direction = buy_item["pair"][1]
                        _price = buy_item["pair"][2]
                        _size = buy_item["pair"][3]
                        _coin_place = buy_item["pair"][4]
                        id = api.take_order(_market,_direction,_price,_size,_coin_place)
                        if id !="-1":
                            tmp_sell_order_list.insert(0,{"id":id,"pair":buy_item["self"],"self":buy_item["pair"]})
                        buy_order_list.remove(buy_item)
                else:
                    break
                print("len of sell order list:",len(sell_order_list))
                if len(sell_order_list)>0:
                    sell_item = sell_order_list[0]
                    sell_id_to_monitor = sell_item["id"]
                    time.sleep(1)
                    if api.is_order_complete(market,sell_id_to_monitor):
                        _market = sell_item["pair"][0]
                        _direction = sell_item["pair"][1]
                        _price = sell_item["pair"][2]
                        _size = sell_item["pair"][3]
                        _coin_place = sell_item["pair"][4]
                        id = api.take_order(_market,_direction,_price,_size,_coin_place)
                        if id !="-1":
                            tmp_buy_order_list.insert(0,{"id":id,"pair":sell_item["self"],"self":sell_item["pair"]})
                        sell_order_list.remove(sell_item)
                else:
                    break

                if len(tmp_buy_order_list)>0:
                    tmp_buy_item = tmp_buy_order_list[0]
                    tmp_buy_id = tmp_buy_item["id"]
                    time.sleep(1)
                    if api.is_order_complete(market, tmp_buy_id):
                        _market = tmp_buy_item["pair"][0]
                        _direction = tmp_buy_item["pair"][1]
                        _price = tmp_buy_item["pair"][2]
                        _size = tmp_buy_item["pair"][3]
                        _coin_place = tmp_buy_item["pair"][4]
                        id = api.take_order(_market, _direction, _price, _size, _coin_place)
                        if id != "-1":
                            sell_order_list.insert(0, {"id": id, "pair": tmp_buy_item["self"], "self": tmp_buy_item["pair"]})
                        tmp_buy_order_list.remove(tmp_buy_item)


                if len(tmp_sell_order_list)>0:
                    tmp_sell_item = tmp_sell_order_list[0]
                    tmp_sell_id = tmp_sell_item["id"]
                    time.sleep(1)
                    if api.is_order_complete(market, tmp_sell_id):
                        _market = tmp_sell_item["pair"][0]
                        _direction = tmp_sell_item["pair"][1]
                        _price = tmp_sell_item["pair"][2]
                        _size = tmp_sell_item["pair"][3]
                        _coin_place = tmp_sell_item["pair"][4]
                        id = api.take_order(_market, _direction, _price, _size, _coin_place)
                        if id != "-1":
                            buy_order_list.insert(0, {"id": id, "pair": tmp_sell_item["self"], "self": tmp_sell_item["pair"]})
                        tmp_sell_order_list.remove(tmp_sell_item)


            except Exception as ex:
                print(sys.stderr, 'in monitor: ', ex)
                print("restart in 5 seconds......")
                time.sleep(5)





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
        api.wallet_to_trade("usdt")
        min_size=api.set_demical(_money, coins)
        print("start cancel existing pending orders")
        for market in markets:
            time.sleep(0.1)
            api.cancel_all_pending_order(market)
        print("cancel pending orders completed")

       # total_money, coin, freez_money, freez_coin = api.get_available_balance(_money, coins[0])


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
    total_load_coin="eos eth ltc trx etc zec xlm ada btc bch xrp ft ada dash bsv iota"
    load_coin = "ltc"
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









