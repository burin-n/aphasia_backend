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
        over_spelling = list()    
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


    def clean(self, phones):
        temp = phones
        while True:
            phones = self.remove_duplicate(self.remove_interfering(phones))
            if(temp == phones):
                break
            temp = phones
        return phones