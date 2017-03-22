import os

file_list = []
count_list = []
target_string = "\r\n"
input_dir = "./" 

print "DOS files with \'\\r\\n\'"
print "filaname (count)"
for dirpath, dirnames, filenames in os.walk("./" + input_dir):
    for filename in [f for f in filenames if f.endswith(".txt")]:     
        numberfound = 0
        temp = os.path.join(dirpath, filename)
        file_list.append(temp)
        infile = open(temp,"rb")
        content = infile.read()
        count_list.append(content.count("\r\n"))

def print_result(index):
    if(count_list[index] != 0): 
        print str(file_list[index]) + "  (" + str(count_list[index]) + ")"
map(print_result, range(len(count_list)))