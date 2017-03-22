import time

class log(object):
    def __init__(self, file_name):
        self.f = open(file_name, "a")

    def write(self, host, mess_type, message):
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        self.f.write('{:<20} {:<5}  {:<10}  {:<100}\n'.format(current_time, "["+mess_type+"]", host, message))

    def close(self):
        self.f.close()
