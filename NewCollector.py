import signal
import requests
import time
import sys
import ritc

 
API_KEY = {'X-API-Key':'3PAFQ3IA'}

def news_writer():
    url = "http://localhost:9999/v1/News"

    payload = {}
    headers = {
    'X-API-Key': '3PAFQ3IA'
    }

    flag = True

    while flag:
        status  = requests.get("http://localhost:9999/v1/case", headers=headers, data=payload)
        status = status.json()
        current_status = status['status']
        if current_status == 'ACTIVE':
            if status['tick'] > 300 and status['period'] == 2:
                break
            print("Case less than 300 ticks or in period 1")
            if status['period'] == 1:
                time.sleep(312)
            else:
                sleep_time = 300 - status['tick']
                if sleep_time > 0:
                    time.sleep(sleep_time)
                else:
                    pass
        else:
            print("Case Inactive")
            time.sleep(5)
                        
    output = requests.get(url, headers=headers, data=payload)
    output = output.json()
    my_string = None
    counter = 2
    for items in output:
        if my_string is None:
            my_string = "\n1. "+ items['body']
        else:
            my_string = my_string + "\n"+ str(counter) +"." + items['body']
            counter += 1
            
        

    # Specify the file path
    file_path = "News_Fixed_Income.txt"

    # Open the file in write mode ('w')
    with open(file_path, 'a') as file:
        # Write the string to the file
        file.write(my_string)

    print(f'String has been stored in {file_path}')

def main():
    my_counter = 8
    for a in range(my_counter):
        news_writer()
        time.sleep(5)
    print("Done with 8 rounds of news")

main()             

