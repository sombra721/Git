import time, os

class Archive:
    def __init__(self, test_name, test_run_dir, archive_dir):
        self.archive_dir = str(archive_dir)
        self.test_run_dir = str(test_run_dir)

        self.test_name = str(test_name)
        # new archive folder with timestamp included
        self.test_archive_dir = self.archive_dir + "/" + self.date_string() + "-" + self.test_name       

    def date_string(self):
        return time.strftime("%Y.%m.%d_%H.%M.%S")		
    
    def cp_all(self):

        # if location of archive_dir does not exists, make it.
        if not os.path.exists(self.archive_dir):
            os.makedirs(self.archive_dir)
        
        # create a new folder of archive with timestamp included
        if not os.path.exists(self.test_archive_dir):
            os.mkdir(self.test_archive_dir, 0775)
       
        
        # copy all files from test to archive folder
        bashCommand = "cp -avr " + self.test_run_dir + "/* " + self.test_archive_dir  + "/"
        os.system(bashCommand )
