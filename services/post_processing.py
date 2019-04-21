import services.utils as utils
from services.utils import empty_char as EMPTY
import numpy as np

class post_processing():
    INIT = 'init'
    VOW = 'vow'
    FINAL = 'final'

    def isVow(self, x):
        return x in ['a','aa', 'i', 'ii', 'v', 'vv', 'u', 'uu', 'e', 'ee',
                    'x', 'xx', 'o', 'oo', '@', '@@', 'q', 'qq', 
                    'ia', 'iia', 'va', 'vva', 'ua', 'uua']


    def isFinal(self, x):
        return x[-1] == '^'


    def isInit(self, x):
        return not self.isVow(x) and not self.isFinal(x)


    def __call__(self, phones, method=None, target=None):
        if(method == None):
            return self.no_post(phones)
        elif(method == 'LTB'):
            return self.LTB(phones)
        elif(method == 'BSS'):
            return self.BSS(phones)
        elif(method == 'BestMatch' and target != None):
            return self.bestMatch(phones, target)


    def unk_method(self, phones):
        # c_i = list() #initial consonant
        # v = list() #vowel
        # c_f = list() #final consonant
        # over_spelling = list()  
        phones = self.clean(phones)

        # has_init = False
        # has_vow = False
        # has_final = False

        # for i in range(len(phones)-1,-1,-1):
        #     phone = phones[i]
        #     if(self.isInit(phone)) has_init = True
        #     if(self.isVow(phone) and has_init) has_vow = True
        #     if(self.isFinal(phone) and has_vow) has_final = True


        state = ""
        start_index = 0
        done = False
        t_start_index = 0
        # has_vow_after_init = False
        best_composite = set()
        best_state = ""

        while(not done):            
            # first init+vow , 1st priority
            # first vow+final, 2nd priority
            # start_index = self.find_state(phones, "IV")
            if(start_index == -1):
                pass
                # start_index = self.find_state(phones, "VF")
            # print('outsisde', start_index)
            if(start_index == -1):
                temp_phones = self.clean(phones, remInterfere=True)
                if(temp_phones == phones):
                    break
                else:
                    phones=temp_phones
            else:
                done = True
            
            # find first init+vow+final
            # for i in range(len(phones)):       
                # if(state == 0):
                #     if(self.isInit(phones[i])): 
                #         temp_composite.add(self.INIT) 
                #     elif(self.isVow(phones[i])):
                #         state = 1
                #     else: 
                #         state = 2
                        
                # if(state == 1):
                #     if(self.isInit(phones[i])):
                #         # reset state
                #         if(best_composite(temp_composite, best_composite)):
                #             start_index = t_start_index
                #             temp_composite = []
                #         t_start_index = i
                #         state = 0
                #     elif(self.isVow(phones[i])):
                #         temp_composite.add(self.VOW)
                #     else: state = 2
                
                # if(state == 2):
                #     if(len(temp_composite) == 3):
                #         start_index = t_start_index
                #         break
                    
                    # if(self.isFinal(phones[i])):    
                    #     temp_composite.add(self.FINAL)
                    # else:
                    #     if(self.isInit(phones[i])): state = 0
                    #     else: state = 1
                    #     # reset state
                    #     if(better_composite(temp_composite, best_composite)):
                    #         start_index = t_start_index
                    #         temp_composite = []
                            
                # if(state == 3): # state == 3
                #     if(self.isInit(phones[i])):
                #         state = 0
                #         t_start_index = i

                # print(phones[i], state)
            # print()

        #     if(state != 2): 
        #         temp_phones = self.clean(phones, remInterfere=True)
        #         if(temp_phones == phones):
        #             break
        #         else:
        #             phones=temp_phones

        #     else: done=True

        
        # if(not has_vow_after_init):
        #     for i in range(len(phones)):
        #         if(self.isVow(phones[i])):
        #             start_index = i
        #             break
        return phones


    def no_post(self, phones):
        c_i = list() #initial consonant
        v = list() #vowel
        c_f = list() #final consonant
        for phone in phones:
            if(self.isInit(phone) and not phone in c_i):
                c_i.append(phone)
            elif(self.isVow(phone) and not phone in v):
                v.append(phone)
            elif(self.isFinal(phone) and not phone in c_f):
                c_f.append(phone)
        return c_i, v, c_f


    def LTB(self, phones):
        c_i = list() #initial consonant
        v = list() #vowel
        c_f = list() #final consonant
        # over_spelling = list()    
        state = 0
        phones = self.clean(phones)
        for i in range(len(phones)):
            if(state == 0):
                if(self.isInit(phones[i])): c_i.append(phones[i])
                elif(self.isVow(phones[i])): state = 1
                else: state = 2
                    
            if(state == 1):
                if(self.isInit(phones[i])): state = 3
                elif(self.isVow(phones[i])): v.append(phones[i])
                else: state = 2
            
            if(state == 2):
                if(self.isInit(phones[i])): state = 3
                elif(self.isVow(phones[i])): state = 3
                else: c_f.append(phones[i])
            
            else: #state = 3
                pass
        
        return c_i, v, c_f


    def BSS(self, phones):
        c_i = list() #initial consonant
        v = list() #vowel
        c_f = list() #final consonant
        phones = self.clean(phones)
        
        state = ""
        start_index = 0
        done = False
        t_start_index = 0
        # has_vow_after_init = False
        best_composite = set()
        best_state = ""

        while(not done):            
            # first init+vow , 1st priority
            # first vow+final, 2nd priority
            start_index = self.find_state_BSS(phones, "IV")
            if(start_index == -1):
                start_index = self.find_state_BSS(phones, "VF")
            # print('outsisde', start_index)
            if(start_index == -1):
                temp_phones = self.clean(phones, remInterfere=True)
                if(temp_phones == phones):
                    break
                else:
                    phones=temp_phones
            else:
                done = True
        if(not done): start_index = 0        
        state = 0
        if(len(phones) > 0 and self.isVow(phones[start_index])):
            c_i.append(EMPTY)
            state = 1
        elif(len(phones) > 0 and self.isFinal(phones[start_index])):
            c_i.append(EMPTY)
            v.append(EMPTY)
            state = 2

        for i in range(start_index,len(phones)):
            if(state == 0):
                if(self.isInit(phones[i])): c_i.append(phones[i])
                elif(self.isVow(phones[i])): state = 1
                else: 
                    v.append(EMPTY)
                    state = 2
                    
            if(state == 1):
                if(self.isInit(phones[i])): state = 3
                elif(self.isVow(phones[i])): v.append(phones[i])
                else: state = 2
            
            if(state == 2):
                if(self.isInit(phones[i])): state = 3
                elif(self.isVow(phones[i])): state = 3
                else: c_f.append(phones[i])
            
            if(state == 3): #state = 3
                pass
        
        if(len(v) == 0):
            v.append(EMPTY)    
        
        if(len(c_f) == 0):
            c_f.append(EMPTY)
        
        return c_i, v, c_f
        

    def find_state_BSS(self, phones, target = "IV"):
        # is_found = False
        state = "INIT"
        # t_start_index = 0
        start_index = -1
        # print('target:', target)
        for i, phone in enumerate(phones):
            # print(state + ' ->' , end= ' ')
            if(state == "I"):
                if(self.isInit(phone)): pass
                elif(self.isVow(phone)):
                    state = "IV"
                else: state = "F"
            
            elif(state == "V"):
                if(self.isInit(phone)): 
                    start_index = i
                    state = "I"
                elif(self.isVow(phone)): pass
                else: state = "VF"
            
            elif(state == "F"):
                if(self.isInit(phone)):
                    state = "I"
                    start_index = i
                elif(self.isVow(phone)):
                    state = "V"
                    start_index = i
                else: 
                    pass
            
            elif(state == "IV"):
                if(self.isInit(phone)):
                    state = "I"
                    start_index = i
                elif(self.isVow(phone)):
                    pass
                else:
                    state = "VF"

            elif(state == "VF"):
                if(self.isInit(phone)):
                    state = "I"
                    start_index = i
                elif(self.isVow(phone)):
                    state = "V"
                    start_index = i
                else:
                    pass

            else: # initial state
                if(self.isInit(phone)): state = "I"
                elif(self.isVow(phone)): state = "V"
                else: state = "F"
                start_index = 0

            # print(state + ', ' + phone, start_index)
            if(state == target):
                return start_index
        
        return -1

    
    def bestMatch(self, phones, target):
        # value for found init, vow, final
        exact_match_val = [0,4,3,2] 
        type_match_val = [0,1,1,1]
        # 3 is givened to torelate false following phones 
        skip_phone_cost = [0,-1,-1,-1]
        skip_class_cost = [0,-1,-1,-1]
        
        phones = self.clean(phones)
        INF = 100
        
        phones = ['pad'] + phones
        target = ['pad'] + target


        dp = np.ones((len(phones),len(target)), dtype=np.int) * -INF
        trace = np.empty((len(phones),len(target)), dtype=str)
        
        
        max_indexp = 0
        max_indext = 0
        max_value = 0
        
        # dp ; dp[i][j] = the highest value of phone if considering until position i 
        # and the latest type of phone is [j] [init,vow,final]
        for i in range(1,len(phones)):
            
            # # check initial consonant
            # if(phones[i] == target[1]):
            #     if(dp[i-1][1] + skip_phone_cost[1] > exact_match_val[1]):
            #         dp[i][1] = dp[i-1][1] + skip_phone_cost[1]
            #         trace[i][1] = 'U'
            #     else:
            #         dp[i][1] = exact_match_val[1]
            #         trace[i][1] = 'S'
            # elif(utils.isInit(phones[i])):
            #     if(dp[i-1][1] + skip_phone_cost[1] > type_match_val[1]):
            #         dp[i][1] = dp[i-1][1] - skip_phone_cost[1]
            #         trace[i][1] = 'U'
            #     else:
            #         dp[i][1] = type_match_val[1]
            #         trace[i][1] = 'S'
            
            # check initial consonant
            if(phones[i] == target[1]):
                UL_val = dp[i-1][0] + exact_match_val[1]
                U_val = dp[i-1][1] + skip_phone_cost[1]                
                S_val = exact_match_val[1]
                max_val = max(U_val, UL_val, S_val)
  
            elif(utils.isInit(phones[i])):
                UL_val = dp[i-1][0] + type_match_val[1]
                U_val = dp[i-1][1] + skip_phone_cost[1]               
                S_val = type_match_val[1]
                max_val = max(U_val, UL_val, S_val)
            else:
                UL_val = dp[i-1][0] + skip_class_cost[1] + skip_phone_cost[1]
                U_val = dp[i-1][1] + skip_phone_cost[1]
                S_val = -INF
                max_val = max(U_val, UL_val, S_val)
            if(UL_val == max_val):
                dp[i][1] = UL_val
                trace[i][1] = 'D'
            elif(U_val == max_val):
                dp[i][1] = U_val
                trace[i][1] = 'U'
            else:
                dp[i][1] = S_val
                trace[i][1] = 'S'




            # check vowel
            if(phones[i] == target[2]):
                UL_val = dp[i-1][1] + exact_match_val[2]
                U_val = dp[i-1][2] + skip_phone_cost[2]                
                S_val = exact_match_val[2]
                max_val = max(U_val, UL_val, S_val)
  
            elif(utils.isVow(phones[i])):
                UL_val = dp[i-1][1] + type_match_val[2]
                U_val = dp[i-1][2] + skip_phone_cost[2]               
                S_val = type_match_val[2]
                max_val = max(U_val, UL_val, S_val)
            else:
                UL_val = dp[i-1][1] + skip_class_cost[2] + skip_phone_cost[2]
                U_val = dp[i-1][2] + skip_phone_cost[2]               
                S_val = -INF
                max_val = max(U_val, UL_val, S_val)
            if(UL_val == max_val):
                dp[i][2] = UL_val
                trace[i][2] = 'D'
            elif(U_val == max_val):
                dp[i][2] = U_val
                trace[i][2] = 'U'
            else:
                dp[i][2] = S_val
                trace[i][2] = 'S'


            # check final consonant
            if(len(target) > 3):
                if(phones[i] == target[3]):
                    UL_val = dp[i-1][2] + exact_match_val[3]
                    U_val = dp[i-1][3] + skip_phone_cost[3]                
                    S_val = exact_match_val[3]
                    max_val = max(U_val, UL_val, S_val)
    
                elif(utils.isFinal(phones[i])):
                    UL_val = dp[i-1][2] + type_match_val[3]
                    U_val = dp[i-1][3] + skip_phone_cost[3]               
                    S_val = type_match_val[3]
                    max_val = max(U_val, UL_val, S_val)
                else:
                    UL_val = dp[i-1][2] + skip_class_cost[3] + skip_phone_cost[3]
                    U_val = dp[i-1][3] + skip_phone_cost[3]   
                    S_val = -INF
                    max_val = max(U_val, UL_val, S_val)
                if(UL_val == max_val):
                    dp[i][3] = UL_val
                    trace[i][3] = 'D'
                elif(U_val == max_val):
                    dp[i][3] = U_val
                    trace[i][3] = 'U'
                else:
                    dp[i][3] = S_val
                    trace[i][3] = 'S'


            argmax = dp[i].argmax()
            maxval = dp[i][argmax]
            if(maxval > max_value):
                max_indexp = i
                max_value = maxval
                max_indext = argmax
            elif(maxval == max_value):
                if(argmax >= max_indext):
                    max_indexp = i
                    max_value = maxval
                    max_indext = argmax 

        
        # backtrack
        row, col = max_indexp, max_indext
        start_i, fin_i = 1, row

        while(True):
            if(trace[row][col] == 'S'):
                start_i = row
                break
            elif(trace[row][col] == 'D'):
                row -= 1
                col -= 1
            elif(trace[row][col] == 'U'):
                row -= 1
            else:
                # some error here
                print('traceback error in bestMatch post processing')
                start_i = row
                break
            
                  
        # print(max_value, max_indexp, max_indext)
        # print(phones)
        # print(dp)
        
        # correct output format
        c_i = set() #initial consonant
        v = set() #vowel
        c_f = set() #final consonant
        for phone in phones[start_i:fin_i+1]:
            if(self.isInit(phone)): c_i.add(phone)
            elif(self.isVow(phone)): v.add(phone)
            else: c_f.add(phone)
        return list(c_i), list(v), list(c_f)


    def remove_interfering(self, phones, n=1):
        state = None
        skip = 0
        i = 0       
        while(i < len(phones)):
            ph = phones[i]
            if(state == None):
                state = ph
                skip = 0
            elif(ph != state):
                if(skip < n):
                    skip += 1
                else:
                    state = None               
                    i = i - skip - 1               
            elif(skip > 0):
                for j in range(skip):
                    phones[i-j-1] = state
            i += 1
            
        return phones


    def remove_duplicate(self, phones):
        result = []
        for i in range(len(phones)):
            if(len(result) == 0):
                result.append(phones[i])
            elif(phones[i] != result[-1]):
                result.append(phones[i])
        return result


    def clean(self, phones, remInterfere=False):
        if(not remInterfere):
            return self.remove_duplicate(phones)
        else:
            temp = phones
            while True:
                phones = self.remove_duplicate(self.remove_interfering(phones))
                if(temp == phones):
                    break
                temp = phones
            return phones


if __name__ == "__main__":
    import sys
    print(sys.argv[1])
    work = post_processing()
    print('working..')
    if(len(sys.argv) == 2):
        print(work(sys.argv[1].split(' '), method="BestMatch", target=["p", "aa", "k^"]))
    else:
        print(work(sys.argv[1].split(' '), method="BestMatch", target=sys.argv[2].split(' ')))