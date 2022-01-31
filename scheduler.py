import datetime

if __name__ == "__main__":
    date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = {}
    data["text"] = "Hello World"
    data["date_time"] = date_time
    print(data)