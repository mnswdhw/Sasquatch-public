#searching 4 bit s boxes
from itertools import combinations
from locale import DAY_1

import json
import datetime, socket
import sys


cvc = []



def hw(n):
  """
  :type n: int
  :rtype: int
  """
  n = str(bin(n))
#   print(n)
  one_count = 0
  for i in n:
     if i == "1":
        one_count+=1
  return one_count
  


def _bin(x, n ):
    # print(type(x))
    # print(type(n))
    return '0bin' + bin(x)[2:].zfill( n )

def init_var():

    for i in range(sb):
        s = f"x{i} : BITVECTOR({size});"
        cvc.append(s)
        s = f"y{i} : BITVECTOR({size});"
        cvc.append(s)
        s = f"a{i} : BITVECTOR({size});"
        cvc.append(s)
        s = f"b{i} : BITVECTOR({size});"
        cvc.append(s)

    for i in range(sb):
        s = f"ASSERT( a{i} = {_bin(i,size)});"
        cvc.append(s)
        s = f"ASSERT( b{i} = {_bin(i,size)});"
        cvc.append(s)
        s = f"ASSERT( x{i} = {_bin(i,size)});"
        cvc.append(s)


def def_sbox():

    for i in range(sb):
        s = f"ASSERT(S[x{i}] = y{i});"
        cvc.append(s)
    
def bijective(resy):

    for r in resy:
        cvc.append(f"ASSERT( {r[0]} /= {r[1]});")

def non_bijective(resy):

    temp = f"ASSERT("
    for r in resy:
        temp = temp + f"({r[0]} = {r[1]}) OR "
    
    temp = temp[:-3] + ");"

    cvc.append(temp)
    


def without_fixed_point(lx,ly):

    for i,_ in enumerate(lx):
        cvc.append(f"ASSERT( {lx[i]} /= {ly[i]});")


def non_linear(resx):

    for r in resx:

        cvc.append(f"ASSERT( BVXOR(S[{r[0]}],S[{r[1]}]) /= S[BVXOR({r[0]},{r[1]})] );")

def init_ddt():


    for i in range(sb):
        for j in range(sb):
            s = f"ddt_a{i}_b{j} : BITVECTOR({size + 1});"
            cvc.append(s)
            for k in range(sb):
                s1 = f"istrue_a{i}_b{j}_x{k} : BITVECTOR(1);"
                cvc.append(s1)

def init_bct():

    for i in range(sb):
        for j in range(sb):
            s = f"bct_a{i}_b{j} : BITVECTOR({size + 1});"
            cvc.append(s)
            for k in range(sb):
                s1 = f"istbct_a{i}_b{j}_x{k} : BITVECTOR(1);"
                cvc.append(s1)



def init_lat():


    for i in range(sb):
        for j in range(sb):
            s = f"lat_a{i}_b{j} : BITVECTOR({size + 2});"
            cvc.append(s)
            for k in range(sb):
                s1 = f"istruelat_a{i}_b{j}_x{k} : BITVECTOR(1);"
                cvc.append(s1)


    #define h.w function/table 
    s = f"H: ARRAY BITVECTOR({size}) OF BITVECTOR({size});"
    cvc.append(s)
    for i in range(sb):
        s = f"ASSERT( H[{_bin(i,size)}] = {_bin(hw(i),size)});"
        cvc.append(s)



def def_lat():

    # Is size of sbox = 3, every value of lat is 5 bit as every value is in 2's complement to account for negative ([0,16] - 8) -> -8 to +8 can be represented in 5 bit in 2's complement 

    for i in range(sb):
        for j in range(sb):

            s1 = f"ASSERT( lat_a{i}_b{j} = BVSUB({size + 2}, BVPLUS({size + 2}, "

            for k in range(sb):

                s = f"ASSERT( IF ( (H[BVXOR((a{i} & x{k}),(b{j} & S[x{k}]))] & {_bin(1,size)}) = {_bin(0,size)} ) THEN istruelat_a{i}_b{j}_x{k} = {_bin(1,1)} ELSE istruelat_a{i}_b{j}_x{k} = {_bin(0,1)} ENDIF );"
                cvc.append(s)

                if k!= (sb-1):
                    s1 = s1 + f"{_bin(0,size+1)}@istruelat_a{i}_b{j}_x{k}, "
                else:
                    s1 = s1 + f"{_bin(0,size+1)}@istruelat_a{i}_b{j}_x{k})"

            s1 = s1 + f",{_bin(sb//2,size+2)}));"
            cvc.append(s1)

            

def def_ddt():


    for i in range(sb):
        for j in range(sb):
            s1 = f"ASSERT( ddt_a{i}_b{j} = BVPLUS({size + 1}, "
            for k in range(sb):

                s = f"ASSERT( IF BVXOR(S[x{k}],b{j}) = S[BVXOR(x{k},a{i})] THEN istrue_a{i}_b{j}_x{k} = {_bin(1,1)} ELSE istrue_a{i}_b{j}_x{k} = {_bin(0,1)} ENDIF );"
                cvc.append(s)
                
                if k!=(sb-1):
                    s1 = s1 + f"{_bin(0,size)}@istrue_a{i}_b{j}_x{k}, "
                else:
                    s1 = s1 + f"{_bin(0,size)}@istrue_a{i}_b{j}_x{k}));"

            
            cvc.append(s1)

    ## Redundant Constraint ##
    #DDT values cannot be odd

    # for i in range(sb):
    #     for j in range(sb):
    #         s = f"ASSERT( "
    #         for k in range(sb):
    #             if k%2 !=0:
    #                 s = s + f"(ddt_a{i}_b{j} /= {_bin(k,size+1)}) AND "

    #         s = s[:-4] + ");"
    #         cvc.append(s)





def def_bct():

    for i in range(sb):
        for j in range(sb):
            s1 = f"ASSERT( bct_a{i}_b{j} = BVPLUS({size + 1}, "
            for k in range(sb):

                s = f"ASSERT( IF (BVXOR(Sinv[BVXOR(S[x{k}],b{j})],Sinv[BVXOR(S[BVXOR(x{k},a{i})],b{j})]) = a{i}) THEN istbct_a{i}_b{j}_x{k} = {_bin(1,1)} ELSE istbct_a{i}_b{j}_x{k} = {_bin(0,1)} ENDIF );"
                cvc.append(s)
                
                if k!=(sb-1):
                    s1 = s1 + f"{_bin(0,size)}@istbct_a{i}_b{j}_x{k}, "
                else:
                    s1 = s1 + f"{_bin(0,size)}@istbct_a{i}_b{j}_x{k}));"

            
            cvc.append(s1)



def req_diff_bn(dbn):

    n = dbn["val"]
    exp = dbn["exp"]


    if exp == "==":
        s1 = f"ASSERT ( "

        for i in range(sb):
            for j in range(sb):

                if (i==0) and (j==0):
                    continue   
                if (hw(i)+hw(j) < n):
             
                    s = f"ASSERT( ddt_a{i}_b{j} = {_bin(0,size + 1)});"
                    cvc.append(s)
                
                if (hw(i) + hw(j) == n):

                    s1 = s1 + f"(ddt_a{i}_b{j} /= {_bin(0,size + 1)}) OR "

        s1 = s1[:-3] + ");"
        cvc.append(s1)

    elif exp == ">=":

        for i in range(sb):
            for j in range(sb):

                if (i==0) and (j==0):
                    continue   
                if (hw(i)+hw(j) < n):
      
                    s = f"ASSERT( ddt_a{i}_b{j} = {_bin(0,size + 1)});"
                    cvc.append(s)


    elif exp == "<=":

        s = f"ASSERT( "
        for i in range(sb):
            for j in range(sb):

                if (i==0) and (j==0):
                    continue   
                if (hw(i)+hw(j) <= n):
                    s = s + f"(ddt_a{i}_b{j} /= {_bin(0,size + 1)}) OR "


        s = s[:-3] + ");"
        cvc.append(s)


 


def req_linear_bn(lbn):

    n = lbn["val"]
    exp = lbn["exp"]

    if exp == "==":
        s1 = f"ASSERT ( "

        for i in range(sb):
            for j in range(sb):

                if (i==0) and (j==0):
                    continue   
                if (hw(i)+hw(j) < n):
             
                    s = f"ASSERT( lat_a{i}_b{j} = {_bin(0,size + 2)});"
                    cvc.append(s)
                
                if (hw(i) + hw(j) == n):

                    s1 = s1 + f"(lat_a{i}_b{j} /= {_bin(0,size + 2)}) OR "

        s1 = s1[:-3] + ");"
        cvc.append(s1)

    elif exp == ">=":

        for i in range(sb):
            for j in range(sb):

                if (i==0) and (j==0):
                    continue   
                if (hw(i)+hw(j) < n):
      
                    s = f"ASSERT( lat_a{i}_b{j} = {_bin(0,size + 2)});"
                    cvc.append(s)


    elif exp == "<=":

        s = f"ASSERT( "
        for i in range(sb):
            for j in range(sb):

                if (i==0) and (j==0):
                    continue   
                if (hw(i)+hw(j) <= n):
                    s = s + f"(lat_a{i}_b{j} /= {_bin(0,size + 2)}) OR "


        s = s[:-3] + ");"
        cvc.append(s)



 



# Once STP knows how to calculate the total bibo we can give an assert statement to make the total bibo equal to the required bibo
def def_bibo_ddt():

    for i in range(sb):
        for j in range(sb):

            s = f"bibo_a{i}_b{j} : BITVECTOR(1);"
            cvc.append(s)

    s = f"total_bibo : BITVECTOR({size + 1});"
    cvc.append(s)
    
    for i in range(sb):
        for j in range(sb):

            s = f"ASSERT( IF ddt_a{i}_b{j} = {_bin(0,size+1)} THEN bibo_a{i}_b{j} = {_bin(0,1)} ELSE bibo_a{i}_b{j} = {_bin(1,1)} ENDIF );"
            cvc.append(s)


    s1 = f"ASSERT( total_bibo = BVPLUS({size + 1}, "
    for i in range(sb):
        for j in range(sb):

            if (hw(i) == 1) and (hw(j) == 1):

                s1 = s1+ f"{_bin(0,size)}@bibo_a{i}_b{j}, "

    
    s1 = s1[:-2]+ "));"

    cvc.append(s1)



def req_bibo_ddt(n):

    s = f"ASSERT( total_bibo = {_bin(n,size+1)} );"
    cvc.append(s)


def def_bibo_lat():

    for i in range(sb):

        for j in range(sb):

            s = f"bibo_lat_a{i}_b{j} : BITVECTOR(1);"
            cvc.append(s)

    s = f"total_bibo_lat : BITVECTOR({size + 1});"
    cvc.append(s)
    
    for i in range(sb):
        for j in range(sb):

            s = f"ASSERT( IF lat_a{i}_b{j} = {_bin(0,size+2)} THEN bibo_lat_a{i}_b{j} = {_bin(0,1)} ELSE bibo_lat_a{i}_b{j} = {_bin(1,1)} ENDIF );"
            cvc.append(s)


    s1 = f"ASSERT( total_bibo_lat = BVPLUS({size + 1}, "
    for i in range(sb):
        for j in range(sb):

            if (hw(i) == 1) and (hw(j) == 1):

                s1 = s1+ f"{_bin(0,size)}@bibo_lat_a{i}_b{j}, "

    
    s1 = s1[:-2]+ "));"

    cvc.append(s1)

def req_bibo_lat(n):

    s = f"ASSERT( total_bibo_lat = {_bin(n,size+1)} );"
    cvc.append(s)

def diff_uniform(du, u_hash):

    u_s = du["val"]
    exp1 = du["exp"]

    if u_hash is not None:
        u_h = u_hash["val"]
        exp2 = u_hash["exp"]

    if exp1 == "==":
        for i in range(sb):
            for j in range(sb):
                if i!=0:
                    s = f"ASSERT( BVLE(ddt_a{i}_b{j},{_bin(u_s,size+1)}) );"
                    cvc.append(s)


        s = f"total_freq : BITVECTOR({(2*size)+1});"
        cvc.append(s)

        for i in range(sb):
            for j in range(sb):

                s = f"istruef_a{i}_b{j} : BITVECTOR(1);"
                cvc.append(s)

        for i in range(sb):
            for j in range(sb):

                if i==0:
                    s = f"ASSERT ( istruef_a{i}_b{j} = {_bin(0,1)} );"
                    cvc.append(s)

                if i!=0:
                    s = f"ASSERT( IF ddt_a{i}_b{j} = {_bin(u_s,size+1)} THEN istruef_a{i}_b{j} = {_bin(1,1)} ELSE istruef_a{i}_b{j} = {_bin(0,1)} ENDIF );"
                    cvc.append(s)

        s1 = f"ASSERT( total_freq = BVPLUS({(2*size)+1}, "

        for i in range(sb):
            for j in range(sb):

                s1 = s1+ f"{_bin(0,2*size)}@istruef_a{i}_b{j}, "
                # s1 = s1+ f"{_bin(0,size)}@istruef_a{i}_b{j}, "

        s1 = s1[:-2]+ "));"

        cvc.append(s1)

        if u_hash is None: 
            temp = 1
            s = f"ASSERT( BVGE(total_freq,{_bin(temp,(2*size)+1)}) );"
        elif exp2 == "==":
            temp = u_h
            s = f"ASSERT( total_freq = {_bin(temp,(2*size)+1)} );"
        elif exp2 == ">=":
            temp = u_h
            s = f"ASSERT( BVGE(total_freq,{_bin(temp,(2*size)+1)}) );"
        elif exp2 == "<=":
            temp = u_h
            temp2 = 1
            s = f"ASSERT( BVLE(total_freq,{_bin(temp,(2*size)+1)}) AND BVGE(total_freq,{_bin(temp2,(2*size)+1)})  );"


    elif exp1 == "<=":

        # for setting the freq in this case we will need to know the du. 
        # For knowing the du we will have to write some more code to find the max value of a ddt, and then use that value as a variable to set the freq

        for i in range(sb):
            for j in range(sb):
                if i!=0:
                    s = f"ASSERT( BVLE(ddt_a{i}_b{j},{_bin(u_s,size+1)}) );"
                    cvc.append(s)

    elif exp1 == ">=":

        # follow same as above to set the freq.
        # have not implemented it yet. 

        s = f"total_freq : BITVECTOR({(2*size)+1});"
        cvc.append(s)

        for i in range(sb):
            for j in range(sb):

                s = f"istruef_a{i}_b{j} : BITVECTOR(1);"
                cvc.append(s)

        for i in range(sb):
            for j in range(sb):

                if i==0:
                    s = f"ASSERT ( istruef_a{i}_b{j} = {_bin(0,1)} );"
                    cvc.append(s)
                else:
                    s = f"ASSERT( IF BVGE(ddt_a{i}_b{j},{_bin(u_s,size+1)}) THEN istruef_a{i}_b{j} = {_bin(1,1)} ELSE istruef_a{i}_b{j} = {_bin(0,1)} ENDIF );"
                    cvc.append(s)


        s1 = f"ASSERT( total_freq = BVPLUS({(2*size)+1}, "

        for i in range(sb):
            for j in range(sb):

                s1 = s1+ f"{_bin(0,2*size)}@istruef_a{i}_b{j}, "
                # s1 = s1+ f"{_bin(0,size)}@istruef_a{i}_b{j}, "

        s1 = s1[:-2]+ "));"

        cvc.append(s1)

        temp = 1
        s = f"ASSERT( BVGE(total_freq,{_bin(temp,(2*size)+1)}) );"
        cvc.append(s)










# def req_freq_diff_uniform(du,u_hash):

#     u_s = du["val"]
#     exp = du["exp"]


#     # Assert all ddt to be less than equal to u_s
#     #@MANAS: Do not get it 
#     # in case of 4 bit sbox value of differential uniformity can be 256 as well hence need 9 bits (2*n + 1)



#     if du["exp"] == "==":

#         s = f"total_freq : BITVECTOR({(2*size)+1});"
#         cvc.append(s)

#         for i in range(sb):
#             for j in range(sb):

#                 s = f"istruef_a{i}_b{j} : BITVECTOR(1);"
#                 cvc.append(s)

#         for i in range(sb):
#             for j in range(sb):

#                 if i==0:
#                     s = f"ASSERT ( istruef_a{i}_b{j} = {_bin(0,1)} );"
#                     cvc.append(s)

#                 if i!=0:
#                     s = f"ASSERT( IF ddt_a{i}_b{j} = {_bin(u_s,size+1)} THEN istruef_a{i}_b{j} = {_bin(1,1)} ELSE istruef_a{i}_b{j} = {_bin(0,1)} ENDIF );"
#                     cvc.append(s)

#         s1 = f"ASSERT( total_freq = BVPLUS({(2*size)+1}, "

#         for i in range(sb):
#             for j in range(sb):

#                 s1 = s1+ f"{_bin(0,2*size)}@istruef_a{i}_b{j}, "
#                 # s1 = s1+ f"{_bin(0,size)}@istruef_a{i}_b{j}, "

#         s1 = s1[:-2]+ "));"

#         cvc.append(s1)

#         if u_hash is None:
#             # if frequency is none but du is not none then to enforce the du, we the frequency to be atleast 1
#             temp = 1
#             s = f"ASSERT( BVGE(total_freq,{_bin(temp,(2*size)+1)}) );"
#         else:
#             temp = u_hash["val"]
#             s = f"ASSERT( total_freq = {_bin(temp,(2*size)+1)} );"

#         cvc.append(s)


#     elif u_hash["exp"] == ">=":

#         s = f"total_freq : BITVECTOR({(2*size)+1});"
#         cvc.append(s)

#         for i in range(sb):
#             for j in range(sb):

#                 s = f"istruef_a{i}_b{j} : BITVECTOR(1);"
#                 cvc.append(s)

#         for i in range(sb):
#             for j in range(sb):

#                 if i==0:
#                     s = f"ASSERT ( istruef_a{i}_b{j} = {_bin(0,1)} );"
#                     cvc.append(s)
#                 else:
#                     s = f"ASSERT( IF BVGE(ddt_a{i}_b{j},{_bin(u_s,size+1)}) THEN istruef_a{i}_b{j} = {_bin(1,1)} ELSE istruef_a{i}_b{j} = {_bin(0,1)} ENDIF );"
#                     cvc.append(s)


#         s1 = f"ASSERT( total_freq = BVPLUS({(2*size)+1}, "

#         for i in range(sb):
#             for j in range(sb):

#                 s1 = s1+ f"{_bin(0,2*size)}@istruef_a{i}_b{j}, "
#                 # s1 = s1+ f"{_bin(0,size)}@istruef_a{i}_b{j}, "

#         s1 = s1[:-2]+ "));"

#         cvc.append(s1)

#         temp = 1
#         s = f"ASSERT( BVGE(total_freq,{_bin(temp,(2*size)+1)}) );"
#         cvc.append(s)




    

def def_walsh_trans():

    for i in range(sb):
        for j in range(sb):
            s = f"w_a{i}_b{j} : BITVECTOR({size + 3});"
            cvc.append(s)
    
    for i in range(sb):
        for j in range(sb):
            # s = f"ASSERT( IF (lat_a{i}_b{j}[{size+1}:{size+1}] = 0bin1) THEN w_a{i}_b{j} = (lat_a{i}_b{j} << 1) ELSE w_a{i}_b{j} = 0bin0@lat_a{i}_b{j} ENDIF );"
            s = f"ASSERT( w_a{i}_b{j} = (lat_a{i}_b{j} << 1) );"
            cvc.append(s)



def linear_uniform(lu):

    l_s = lu["val"]
    exp = lu["exp"]

    if exp == "==":
        for i in range(sb):
            for j in range(sb):
                if j!=0:
                    s = f"ASSERT( IF (w_a{i}_b{j}[{size+2}:{size+2}] = 0bin1) THEN BVLE(BVPLUS({size + 3},~w_a{i}_b{j},{_bin(1,size + 3)}),{_bin(l_s,size + 3)}) ELSE BVLE(w_a{i}_b{j},{_bin(l_s,size + 3)}) ENDIF );"
                    # s = f"ASSERT( BVLE(w_a{i}_b{j},{_bin(l_s,size + 3)}) );"
                    cvc.append(s)
    
    elif exp == "<=":
        for i in range(sb):
            for j in range(sb):
                if j!=0:
                    s = f"ASSERT( IF (w_a{i}_b{j}[{size+2}:{size+2}] = 0bin1) THEN BVLE(BVPLUS({size + 3},~w_a{i}_b{j},{_bin(1,size + 3)}),{_bin(l_s,size + 3)}) ELSE BVLE(w_a{i}_b{j},{_bin(l_s,size + 3)}) ENDIF );"
                    # s = f"ASSERT( BVLE(w_a{i}_b{j},{_bin(l_s,size + 3)}) );"
                    cvc.append(s)
    


def req_freq_linear_uniform(lu,l_hash):

    l_s = lu["val"]
    exp = lu["exp"]


    t_c = _bin(l_s,size + 3)

    # print(t_c)

    if exp == "==":

        s = f"total_lin_freq : BITVECTOR({(2*size) + 1});"
        cvc.append(s)

        for i in range(sb):
            for j in range(sb):

                s = f"istruelinf_a{i}_b{j} : BITVECTOR(1);"
                cvc.append(s)
        
        for i in range(sb):
            for j in range(sb):

                if i == 0:
                    s = f"ASSERT( istruelinf_a{i}_b{j} = {_bin(0,1)} );"
                    cvc.append(s)

                if i !=0:
                    s = f"ASSERT( IF w_a{i}_b{j} = {t_c} THEN istruelinf_a{i}_b{j} = {_bin(1,1)} ELSE istruelinf_a{i}_b{j} = {_bin(0,1)} ENDIF );"
                    cvc.append(s)

        s1 = f"ASSERT( total_lin_freq = BVPLUS({(2 * size) + 1}, "

        for i in range(sb):
            for j in range(sb):

                s1 = s1+ f"{_bin(0,(2*size))}@istruelinf_a{i}_b{j}, "

        s1 = s1[:-2]+ "));"

        cvc.append(s1)

        if l_hash is None:
            # if frequency is none but du is not none then to enforce the du, we the frequency to be atleast 1
            temp = 1
            s = f"ASSERT( BVGE(total_lin_freq,{_bin(temp,(2*size)+1)}) );"
        else:
            s = f"ASSERT( total_lin_freq = {_bin(l_hash,(2*size)+1)} );"

        cvc.append(s)

    elif exp == ">=":

        s = f"total_lin_freq : BITVECTOR({(2*size) + 1});"
        cvc.append(s)

        for i in range(sb):
            for j in range(sb):

                s = f"istruelinf_a{i}_b{j} : BITVECTOR(1);"
                cvc.append(s)

        for i in range(sb):
            for j in range(sb):

                if i == 0:
                    s = f"ASSERT( istruelinf_a{i}_b{j} = {_bin(0,1)} );"
                    cvc.append(s)

                if i !=0:
                    s = f"ASSERT( IF BVGE(w_a{i}_b{j},{t_c}) THEN istruelinf_a{i}_b{j} = {_bin(1,1)} ELSE istruelinf_a{i}_b{j} = {_bin(0,1)} ENDIF );"
                    cvc.append(s)

        s1 = f"ASSERT( total_lin_freq = BVPLUS({(2 * size) + 1}, "

        for i in range(sb):
            for j in range(sb):

                s1 = s1+ f"{_bin(0,(2*size))}@istruelinf_a{i}_b{j}, "

        s1 = s1[:-2]+ "));"

        cvc.append(s1)

        temp = 1
        s = f"ASSERT( BVGE(total_lin_freq,{_bin(temp,(2*size)+1)}) );"
        cvc.append(s)


def test_fn(du):

    val = du["val"]
    exp = du["exp"]

    s = f"ASSERT( "
    for i in range(sb):
        for j in range(sb):
            if i!=0:
                s = s + f"(ddt_a{i}_b{j} = {_bin(val,size+1)}) OR "


    s = s[:-3] + ");"

    cvc.append(s)


    

def basic_vars():

    s = f"S: ARRAY BITVECTOR({size}) OF BITVECTOR({size});"
    cvc.append(s)

    lx = [f"x{i}" for i in range(sb)]
    ly = [f"y{i}" for i in range(sb)]

    # lx = ["x0","x1","x2","x3","x4","x5","x6","x7","x8","x9","x10","x11","x12","x13","x14","x15"]
    # ly = ["y0","y1","y2","y3","y4","y5","y6","y7","y8","y9","y10","y11","y12","y13","y14","y15"]
    resy = list(combinations(ly, 2))
    resx = list(combinations(lx, 2))

    return (lx,ly,resx,resy)



def def_sinv():

    s = f"Sinv: ARRAY BITVECTOR({size}) OF BITVECTOR({size});"
    cvc.append(s)

    for i in range(sb):
        s = f"ASSERT(Sinv[y{i}] = x{i});"
        cvc.append(s)
    


def involution():

    for i in range(sb):
        s = f"ASSERT( Sinv[{_bin(i,size)}] = S[{_bin(i,size)}] );"
        cvc.append(s)



def fix_some_ys(lookup):

    for k,v in lookup.items():
        
        index = int(k)

        if v["exp"] == "==":
            s = f"ASSERT( y{index} = {_bin(v['val'], size)} );"
            cvc.append(s)
        elif v["exp"] == ">=":
            s = f"ASSERT( BVGE(y{index},{_bin(v['val'], size)}) );"
            cvc.append(s)
        elif v["exp"] == "<=":
            s = f"ASSERT( BVLE(y{index},{_bin(v['val'], size)}) );"
            cvc.append(s)
        elif v["exp"] == "!=":
            s = f"ASSERT( y{index} /= {_bin(v['val'], size)} );"
            cvc.append(s)
            
        
        
    


    


def solve(data,cvc_name):

    fp = data["fp"]
    dbn = data["dbn"]
    lbn = data["lbn"]
    bddt = data["bddt"]
    blat = data["blat"]
    #expecting data["du"] to be a dictionary of the form {"val"... , "exp": ....}
    du = data["du"]
    u_hash = data["frequency_du"]
    fdu = data["frequency_du"]
    lu = data["alu"]
    flu = data["frequency_alu"]
    is_bct = data["bct"]
    is_involution = data["involution"]
    lookup = data["lookup"]
    is_bijective = data["is_bijective"]
    lx,ly,resx,resy = basic_vars()

    init_var()
    def_sbox() 
    if is_bijective:
        bijective(resy)
    else:
        non_bijective(resy)
    # non_linear(resx)   #THIS OPTION IS NOT REQUIRED, WILL CREATE PROBLEMS
    def_sinv()
    if lookup is not None:
        fix_some_ys(lookup)


    if is_involution:
        involution()

    if (du is not None) or (bddt is not None) or (dbn is not None) or (fdu is not None):
        init_ddt()
        def_ddt()

    if (lu is not None) or (flu is not None) or (lbn is not None) or (blat is not None):
        init_lat()
        def_lat()
        def_walsh_trans()
        
    if is_bct == True:
        init_bct()
        def_bct()
    
    if fp == False:
        without_fixed_point(lx,ly)

 
    if du is not None:

        # exp = du["exp"]

        # if (exp == "==") and (fdu is None):
        #     diff_uniform(du)
        #     test_fn(du)
        # else:
        #     diff_uniform(du, u_hash)
        #     # req_freq_diff_uniform(du,fdu)

        # # diff_uniform(du)
        # # req_freq_diff_uniform(du,fdu)


        if fdu is None: 
            u_hash = None
        else:
            u_hash = fdu
        diff_uniform(du, u_hash)
        

    if lu is not None:

        lu["val"] = abs(lu["val"])
        
        linear_uniform(lu)
        req_freq_linear_uniform(lu,flu)

    if dbn is not None:
        req_diff_bn(dbn)

    if lbn is not None:
        req_linear_bn(lbn)

    if bddt is not None:
        def_bibo_ddt()
        req_bibo_ddt(bddt)
    
    if blat is not None:
        def_bibo_lat()
        req_bibo_lat(blat)


    s = 'QUERY FALSE;'
    cvc.append(s)
    s = 'COUNTEREXAMPLE;'
    cvc.append(s)


    f = open( f'{cvc_name}.cvc', 'w' )
    print ( '\n'.join( cvc ), file = f )
    f.close()





global size
global sb

config_name = sys.argv[1]
sbox_name = sys.argv[2]
name_int = sys.argv[3]
cvc_name = sys.argv[4]


with open(f'{config_name}.json', 'r') as config_file:
    data_full = json.load(config_file)
    data = data_full[sbox_name]
    data["global_timeout"] = data_full["global_timeout"]
    data["sequential"] = data_full["sequential"]
    data["output_dir"] = data_full["output_dir"]
    data["debug"] = data_full["debug"]


f = open(f'{name_int}.txt',"w")
print(f'Host: {socket.gethostname()}')
f.write(f'Start: {datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")}\n')
f.write(f'Host: {socket.gethostname()}\n')
f.write("INPUT\n")
f.write(json.dumps(data))
f.write("\n\nOUTPUT\n")
f.close()


size = data["size"]
sb = 2**size

solve(data,cvc_name)

    

