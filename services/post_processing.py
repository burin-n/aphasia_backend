from services.utils import empty_char as EMPTY


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


    def find_state(self, phones, target = "IV"):
        is_found = False
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


    def __call__(self, phones):
        c_i = list() #initial consonant
        v = list() #vowel
        c_f = list() #final consonant
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
            start_index = self.find_state(phones, "IV")
            if(start_index == -1):
                start_index = self.find_state(phones, "VF")
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
        
    
    def remove_interfering(self, phones, n=1):
        state = None
        skip = 0
        i = 0
        
        while(i < len(phones)):
            ph = phones[i]
    #         print(i, state, skip)
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
    print(work(sys.argv[1].split(' ')))