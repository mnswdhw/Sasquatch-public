import re
import sys


if __name__ == "__main__":

    name = sys.argv[1]
    stpo_fn = sys.argv[2]

    file = open(f"{stpo_fn}.txt")
    txt = file.read()
    file.close()
    # print(type(txt))
    x = re.findall(r"\nASSERT\( S\[.*",txt)
    # print(x)
    # print(len(x))
    # size = len((x[0][9:-4].split("="))[0][4:-2])
    size = len(x)
    # print(size)
    final_sbox = [0]*(size)

    # print(x)

    def check_string(string):

        try:
            int(string, 2)
        except ValueError:
            return int(string,16)   #hexadecimanl 
        return int(string,2)        #binary

    for match in x:
        # print(match[9:-3])
        m = match[9:-3].split("=")
        # print(m)

        # m[0][2:-2] = 0b111 or 0x8 inside the S[0b111] or S[0x8]
        # m[1][1:] 1 because there is a space in the right part after split ("=")
        p1 = check_string(m[0][2:-2])
        p2 = check_string(m[1][1:])
        # print(p1,p2)
        final_sbox[p1] = p2

    # print(f'Start: {datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")}\n')
    # print(f'Host: {socket.gethostname()}\n')
    print(f"{name} : {final_sbox}")
        
    
    
    