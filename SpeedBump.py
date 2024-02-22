import time
import signal
import requests
from time import sleep

class ApiException(Exception):
    pass

def signal_handler(signum, frame):
    global shutdown
    signal.signal(signal.SIGINT, signal.SIG_DFL)

API_KEY = {'X-API-Key':'3PAFQ3IA'}
shutdown = False

ORDER_LIMIT = 5
MAX_SIZE = 5000
TOTAL_VOLUME = 25000
COUNT = int(TOTAL_VOLUME/MAX_SIZE)
number_of_orders = 0
total_speedbumps = 0

def speedbumps(transaction_time):
    global total_speedbumps
    global number_of_orders
    
    order_speedbump = -transaction_time + 1/ORDER_LIMIT
    
    total_speedbumps = total_speedbumps + order_speedbump
    
    number_of_orders = number_of_orders + 1
    
    sleep(total_speedbumps/number_of_orders)
    
def main():
    with requests.Session() as s:
        s.headers.update(API_KEY)
        
        while number_of_orders < COUNT:
            start = time.time()
            
            resp = s.post('http://localhost:9999/v1/orders', params = {'ticker':'AC', 'type':'LIMIT', 'quantity': MAX_SIZE, 'price': 20, 'action': 'BUY'})
            
            if(resp.ok):
                transaction_time = time.time() - start
                
                speedbumps(transaction_time)
                
            else:
                print(resp.json())
                
if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    main() 
    
                        