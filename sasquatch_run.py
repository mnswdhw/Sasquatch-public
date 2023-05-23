#We cannot pass a dictionary as a command line argument, that is why I was passing a file

def name_files(file_name,k, output_dir_name):

    if file_name == "cvc":
        name = output_dir_name + "/_temp_readback_" + k + "_" + "cvc_file" + str(os.getpid()) + "_" + str(calendar.timegm(time.gmtime())) 

    if file_name == "temp":
        name = output_dir_name + "/_temp_readback_" + k + "_" + str(os.getpid()) + ".txt"

    return name 


def perform_sbox_checks(sbox, k, output_dir_name):

    size = sbox["size"]
    du = sbox["du"]
    fdu = sbox["frequency_du"]
    lu = sbox["alu"]
    flu = sbox["frequency_alu"]
    solution_fn = sbox["solution_fn"]
    fp = sbox["fp"]



    if du is None and fdu is not None:
        logging.warning("If du is null then frequency_du should be null")
        print("Warning: If du is null then frequency_du should be null")
        

    if lu is None and flu is not None:
        logging.warning("If lu is null then frequency_lu should be null")
        print("Warning: If du is null then frequency_du should be null")

    if (size < 3) or (size > 7):
        logging.warning("Warning: SBox size is too small (less than 3) or too big (more than 7)")
        print("Warning: SBox size is too small (less than 3) or too big (more than 7)")

    if fp == True:
        logging.warning("Fixed point (fp) should be null or false, true is not recognized. Interpreting true as null and proceeding")
        print("Fixed point (fp) should be null or false, true is not recognized. Interpreting true as null and proceeding")


    if solution_fn is None:
        name_fs = f"{output_dir_name}/{k}_solution" + "_" + str(os.getpid()) + "_" + str(calendar.timegm(time.gmtime())) 
    else:
        name_fs = output_dir_name + '/' + k + "_" + solution_fn + "_" + str(os.getpid()) + "_"  + str(calendar.timegm(time.gmtime()))


    return name_fs




def do_job_seq(item):

    k = item[0]
    v = item[1]

    output_dir_name = v["output_dir"]
    is_debug = v["debug"]

    name_fs = perform_sbox_checks(v,k, output_dir_name) 
    cvc_name = name_files("cvc", k, output_dir_name)
    temp_file = name_files("temp",k, output_dir_name)

    st = time.time()

    logging.info(f"{k} Start time: {st}")
    os.system("echo Start time: $(date +'%T')")
    os.system(f"python3 gen_search_sbox.py {config_name} {k} {name_fs} {cvc_name}")
    # os.system(f"cat {cvc_name}.cvc >> sasquatch.log") ##CVC FILE TAKING TOO MUCH SPACE HENCE NOT ADDING TO SASQUATCH.LOG
    logging.info(f"{k} STP Output\n") 
    os.system(f"echo '\n{datetime.now().time()} Below STP output of {k} [{os.getpid()}]' >> {temp_file}")
    os.system(f"stp {cvc_name}.cvc | tee -a {name_fs}.txt {temp_file} >/dev/null")
    os.system(f"echo '{datetime.now().time()} Above STP output of {k} [{os.getpid()}]\n' >> {temp_file}")
    os.system(f"cat {temp_file} >> sasquatch.log")  #APPEND ONE FILE TO ANOTHER USING CAT
    os.remove(f"{temp_file}")

    if not is_debug:
        os.remove(f"{cvc_name}.cvc")

    logging.info(f"{k} Final result\n") 
    os.system(f"python3 stp_finalsbox.py {k} {name_fs}| tee -a {name_fs}.txt sasquatch.log")

    p = Path(f'{name_fs}.txt')
    p.rename(p.with_suffix('.sbox'))

    os.system("echo End time: $(date +'%T')")
    et = time.time()
    logging.info(f"{k} End time: {et}")
    os.system(f"echo Time Taken in mins: {(et - st)/60}\n")

    logging.info(f"{k} Time Taken in mins: {(et - st)/60}\n")

    return os.getpid()


def do_job_mult_pool(item):

    k = item[0]
    v = item[1]

    output_dir_name = v["output_dir"]
    is_debug = v["debug"]

    print(f"Started {k}")

    name_fs = perform_sbox_checks(v,k, output_dir_name)
    cvc_name = name_files("cvc", k, output_dir_name)
    temp_file = name_files("temp",k, output_dir_name)
    


    st = time.time()

    l.acquire()
    logging.info(f"{k} Start time: {st}")
    l.release()

    os.system("echo Start time: $(date +'%T')")
    os.system(f"python3 gen_search_sbox.py {config_name} {k} {name_fs} {cvc_name}")

    l.acquire()
    # os.system(f"cat {cvc_name}.cvc >> sasquatch.log")   ##CVC FILE TAKING TOO MUCH SPACE HENCE NOT ADDING TO SASQUATCH.LOG
    logging.info(f"{k} STP Output\n") 
    l.release()

    os.system(f"echo '\n{datetime.now().time()} Below STP output of {k} [{os.getpid()}]' >> {temp_file}")
    os.system(f"stp {cvc_name}.cvc | tee -a {name_fs}.txt {temp_file} >/dev/null")
    os.system(f"echo '{datetime.now().time()} Above STP output of {k} [{os.getpid()}]\n' >> {temp_file}")

    l.acquire()
    os.system(f"cat {temp_file} >> sasquatch.log")
    l.release()

    os.remove(f"{temp_file}")

    if not is_debug:
        os.remove(f"{cvc_name}.cvc")

    l.acquire()
    logging.info(f"{k} Final result\n") 
    os.system(f"python3 stp_finalsbox.py {k} {name_fs}| tee -a {name_fs}.txt sasquatch.log")
    l.release()

    p = Path(f'{name_fs}.txt')
    p.rename(p.with_suffix('.sbox'))

    os.system("echo End time: $(date +'%T')")
    et = time.time()

    l.acquire()
    logging.info(f"{k} End time: {et}")
    l.release()

    os.system(f"echo Time Taken in mins: {(et - st)/60}\n")

    l.acquire()
    logging.info(f"{k} Time Taken in mins: {(et - st)/60}\n")
    l.release()

    return os.getpid()


def do_job_mult(item,l):

    

    k = item[0]
    v = item[1]

    output_dir_name = v["output_dir"]
    is_debug = v["debug"]

    # print(output_dir_name)

    print(f"Started {k}")

    name_fs = perform_sbox_checks(v,k, output_dir_name)
    cvc_name = name_files("cvc", k, output_dir_name)
    temp_file = name_files("temp",k, output_dir_name)


    st = time.time()

    l.acquire()
    logging.info(f"{k} Start time: {st}")
    l.release()

    os.system("echo Start time: $(date +'%T')")
    os.system(f"python3 gen_search_sbox.py {config_name} {k} {name_fs} {cvc_name} {output_dir_name}")

    l.acquire()
    # os.system(f"cat {cvc_name}.cvc >> sasquatch.log")  ##CVC FILE TAKING TOO MUCH SPACE HENCE NOT ADDING TO SASQUATCH.LOG
    logging.info(f"{k} STP Output\n") 
    l.release()


    os.system(f"echo '\n{datetime.now().time()} Below STP output of {k} [{os.getpid()}]' >> {temp_file}")
    os.system(f"stp {cvc_name}.cvc | tee -a {name_fs}.txt {temp_file} >/dev/null")
    os.system(f"echo '{datetime.now().time()} Above STP output of {k} [{os.getpid()}]\n' >> {temp_file}")

    l.acquire()
    os.system(f"cat {temp_file} >> sasquatch.log")
    l.release()

    os.remove(f"{temp_file}")

    if not is_debug:
        os.remove(f"{cvc_name}.cvc")
    
    l.acquire()
    logging.info(f"{k} Final result\n") 
    os.system(f"python3 stp_finalsbox.py {k} {name_fs}| tee -a {name_fs}.txt sasquatch.log")
    l.release()

    p = Path(f'{name_fs}.txt')
    p.rename(p.with_suffix('.sbox'))

    os.system("echo End time: $(date +'%T')")
    et = time.time()

    l.acquire()
    logging.info(f"{k} End time: {et}")
    l.release()

    os.system(f"echo Time Taken in mins: {(et - st)/60}\n")

    l.acquire()
    logging.info(f"{k} Time Taken in mins: {(et - st)/60}\n")
    l.release()

    return os.getpid()


def mult(args, output_dir_name, is_debug):
    
    l = multiprocessing.Lock()

    for tup in args:
        sbox = tup[1]
        sbox["output_dir"] = output_dir_name
        sbox["debug"] = is_debug

    processes = [multiprocessing.Process(target = do_job_mult, args=(item,l,)) for item in args]

    for p in processes:
        p.start()

    for i,p in enumerate(processes):
        v = args[i][1]
        p.join(v["time_out"])
        # do_job(k,v)

        if p.is_alive():
            print(f"Process {p.pid} taking more time than expected, therefore killing it")

            # Terminate foo
            p.terminate()
            p.join()


def mult_pool(args, output_dir_name, is_debug, global_timeout):

    # print(global_timeout)

    def init(lock):
        global l
        l = lock

    lock = multiprocessing.Lock()

    for tup in args:
        sbox = tup[1]
        sbox["output_dir"] = output_dir_name
        sbox["debug"] = is_debug

    

    if len(args) < multiprocessing.cpu_count():
        max_workers = len(args)
    else:
        max_workers = multiprocessing.cpu_count()
    pool = ProcessPool(max_workers = max_workers, initializer = init, initargs = (lock,))
    future = pool.map(do_job_mult_pool,args,timeout = global_timeout)
    pool.close()
    pool.join()
    iterator = future.result()

    while True:
        try:
            result = next(iterator)
            # print(result)
        except StopIteration:
            break  
        except TimeoutError as error:
            print("function took longer than %d seconds" % error.args[1]) 


def seq(args, output_dir_name, is_debug, gt = None):

    for item in args:
        print(f"Started {item[0]}")
        item[1]["output_dir"] = output_dir_name
        item[1]["debug"] = is_debug
        

        p = multiprocessing.Process(target=do_job_seq, name="Dojob", args=(item,))
        v = item[1]
        p.start()
        if gt is not None:
            p.join(gt)
        else:
            p.join(v["time_out"])

        if p.is_alive():
            print(f"Process {p.pid} taking more time than expected, therefore killing it")

            # Terminate foo
            p.terminate()
            p.join()
        


if __name__ == "__main__":

    import os
    import time
    import sys
    import json
    import calendar
    import logging
    import multiprocessing
    from pebble import ProcessPool
    from concurrent.futures import TimeoutError
    from pathlib import Path    #for changing file extension 
    from datetime import datetime
    logging.basicConfig(filename='sasquatch.log', format='%(process)d - %(asctime)s - %(message)s',level=logging.INFO)
    

    if len(sys.argv) == 1:
        print("No configuration file provided, proceeding with config.json")
        config_name = "config"
    elif (len(sys.argv) == 2):
        config_name = sys.argv[1]


    with open(f'{config_name}.json', 'r') as config_file:
        data = json.load(config_file)
        
    global_timeout = data["global_timeout"]
    is_seq = data["sequential"]
    output_dir_name = data["output_dir"]
    is_debug = data["debug"]

    if output_dir_name is None:
        output_dir_path = os.getcwd() + "/output"
        output_dir_name = "output"
    else:
        output_dir_path = os.getcwd() + f"/{output_dir_name}"


#    check if output directory already exists
    if not os.path.isdir(output_dir_path):
        #create directory
        os.mkdir(output_dir_path)

    args_full = list(data.items())
    args_work = args_full[4:]

    # args = list(data.items())



    if (global_timeout is None) :
        if not is_seq:
        # multiprocessing with each process having individual timeout
            mult(args_work, output_dir_name, is_debug)
        else:
            seq(args_work, output_dir_name, is_debug)

    else:
        if not is_seq:
            # multiprocessing with pooled workers
            mult_pool(args_work, output_dir_name, is_debug, global_timeout)
        else:
            print("Global timeout will be used for all SBoxes")
            seq(args_work, output_dir_name, is_debug, gt = global_timeout)

   







    

















