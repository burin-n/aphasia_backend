class post_processing():
   
    def isVow(self, x):
        return x in ['a','aa', 'i', 'ii', 'v', 'vv', 'u', 'uu', 'e', 'ee',
                    'x', 'xx', 'o', 'oo', '@', '@@', 'q', 'qq', 
                    'ia', 'iia', 'va', 'vva', 'ua', 'uua']


    def isFinal(self, x):
        return x[-1] == '^'


    def isInit(self, x):
        return not self.isVow(x) and not self.isFinal(x)


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


        state = 0
        start_index = 0
        done = False
        t_start_index = 0
        

        while(not done):
            if(self.isInit(phones[0])): state = 0
            else: state = 3
            for i in range(len(phones)):       
                if(state == 0):
                    if(self.isInit(phones[i])): pass
                    elif(self.isVow(phones[i])): state = 1
                    else: 
                        state = 3
                        
                if(state == 1):
                    start_index = t_start_index
                    if(self.isInit(phones[i])): 
                        t_start_index = i
                        state = 0
                    elif(self.isVow(phones[i])): pass
                    else: state = 2
                
                if(state == 2):
                    if(not self.isFinal(phones[i])):
                        break
                
                if(state == 3): # state == 3
                    if(self.isInit(phones[i])):
                        state = 0
                        t_start_index = i

                print(phones[i], state)
            print()

            if(state != 2): 
                temp_phones = self.clean(phones, remInterfere=True)
                if(temp_phones == phones):
                    done=True
                else:
                    phones=temp_phones

            else: done=True

        state = 0
        for i in range(start_index,len(phones)):
            
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
            
            if(state == 3): #state = 3
                pass
        
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
                count = 0
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