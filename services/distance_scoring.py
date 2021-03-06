from services.utils import empty_char as EMPTY

class distance_scoring():
    
    # x is tuple of three Counter. Each counter includes number of phones in init, vowel, and final
    # y is list of three phones including init, vowel, and final
    
    init_gap = 4.0
    vow_gap = 4.0
    final_gap = 4.0
    
    def __call__(self, x, y):
        return self.dist_scoring(x, y)
    

    # IDENTIFY -----------------------------------------------------------------

    def isVow(self, x):
        return x in ['a','aa', 'i', 'ii', 'v', 'vv', 'u', 'uu', 'e', 'ee',
                    'x', 'xx', 'o', 'oo', '@', '@@', 'q', 'qq', 
                    'ia', 'iia', 'va', 'vva', 'ua', 'uua']


    def isFinal(self, x):
        return x[-1] == '^'


    def isInit(self, x):
        return not self.isVow(x) and not self.isFinal(x)


    # INIT ---------------------------------------------------------------------

        
    def get_cluster_cost(self, x , y):
        cluster_cost = 0
        if(x[-1] in ['r', 'l']):        
            if(not y[-1] in ['r', 'l']):
                cluster_cost += 0.5        
            
        elif(x[-1] == 'w' and len(x) > 1):
            if(not y[-1] == 'w' and len(y) > 1):
                cluster_cost += 1                    
        return cluster_cost
        

    def clean_cluster(self, x):
        if(len(x) > 1):
            if(x[-1] in ['r', 'l']):
                x = x[:-1]
            if(x[-1] == 'w'):
                x = x[-1]
        return x


    def initc_cost(self, x,y):
        #REF table: https://en.wikipedia.org/wiki/Thai_language#Initials
        #column: Labial, Alveolar, Palatal, Velar, Gloattal
        #row: Nasal, Plosive_voice, Plosive_tenuis, Plotsive_aspirated, Fricative, Approximant, Trill
        if(x==y): return 0
        
        table = [[] for i in range(7)]
        table[0].extend(['m', 'n', '' , 'ng', ''])
        table[1].extend(['b', 'd', '' , '', ''])
        table[2].extend(['p', 't', 'c', 'k', 'z'])
        table[3].extend(['ph', 'th', 'ch', 'kh', ''])
        table[4].extend(['f', 's', '', '', 'h'])
        table[5].extend(['', 'l', 'j', 'w', ''])
        table[6].extend(['', 'r', '', '', ''])
        
        # set default
        if(x == EMPTY): x = 'z'
        if(y == EMPTY): y = 'z'

        cluster_cost = 0
        if(x!= EMPTY and y!=EMPTY):
            cluster_cost = self.get_cluster_cost(x, y)
            cluster_cost += self.get_cluster_cost(y, x)
        
        x = self.clean_cluster(x)
        y = self.clean_cluster(y)    
        
        for i in range(7):
            for j in range(5):
                if(x == table[i][j]):
                    xi = i; xj = j
                if(y == table[i][j]):
                    yi = i; yj = j
        
        dist = ((xi-yi)**2 + (xj-yj)**2)**0.5 + cluster_cost
    #     return dist
        return min(dist, self.init_gap)/self.init_gap
        
        
    # VOWEL ---------------------------------------------------------------------
        
        
    def get_dipthongs_j(self, x):
        if(x in ['ia', 'iia']): return 0.5
        elif(x in ['va','vva']): return 2.5
        else: return 4.5
        
        
    def vow_cost(self, x,y):
        # REF table: https://en.wikipedia.org/wiki/Thai_language#Vowels
        # column: FUS, FUL, BUS, BUL, BRS, BRL
        # F: Front, B: Back, U: Unrounded, R: Rounded, S: Short, L: Long
        # row: High, Mid, Low
        if(x == y): return 0
        elif(x == EMPTY or y == EMPTY): return 1

        table = [[] for i in range(3)]
        table[0].extend(['i', 'ii', 'v', 'vv', 'u', 'uu'])
        table[1].extend(['e', 'ee', 'q', 'qq', 'o', 'oo'])
        table[2].extend(['x', 'xx', 'a', 'aa', '@', '@@'])

        dipthongs = ['ia', 'iia', 'va', 'vva', 'ua', 'uua']
    
        xi, yi, xj, yj = -1, -1, -1, -1
        
        # Dipthongs are insert at row 1, columns [0.5, 2.5, 4.5]
        if(x in dipthongs):
            xi = 1
            xj = self.get_dipthongs_j(x)
        
        if(y in dipthongs):
            yi = 1
            yj = self.get_dipthongs_j(y)    
        
        for i in range(3):
            for j in range(6):
                if(x == table[i][j]):
                    xi = i; xj = j
                if(y == table[i][j]):
                    yi = i; yj = j

    #     return ( (2*(xi-yi))**2 + (xj-yj)**2 )**0.5
        return  min(((2*(xi-yi))**2 + (xj-yj)**2 )**0.5, self.vow_gap)/self.vow_gap


    # FINAL ---------------------------------------------------------------------

        
    def finalc_cost(self, x, y):
        #REF table: https://en.wikipedia.org/wiki/Thai_language#Finals
        #column: Labial, Alveolar, Palatal, Velar
        #row: Nasal, Plosive, Approximant
        if(x == y):
            return 0

        table = [[] for i in range(3)]
        table[0].extend([['m^'], ['n^', 'l^'], [], ['ng^']])
        table[1].extend([['p^', 'f^'], ['t^','s^','ch^'], [], ['k^']])
        table[2].extend([['w^'], [], ['j^'], []])
        
        #default EMPTY as (Glottis)
        xi = 1; xj = 4; yi = 1; yj = 4
        
        for i in range(3):
            for j in range(4):
                if(x in table[i][j]):
                    xi = i; xj = j
                if(y in table[i][j]):
                    yi = i; yj = j

#         return ((xi-yi)**2 + (xj-yj)**2)**0.5    
        return min(((xi-yi)**2 + (xj-yj)**2)**0.5, self.final_gap)/self.final_gap
    
        
    # ----------------------------------------------------------------------

    def dist_scoring(self, speak, target):
        init, vowel, final = speak     
        t_final = EMPTY
        
        if(len(target) == 3): t_init, t_vowel, t_final = target
        else: t_init, t_vowel = target

        if(len(init) == 0): init[EMPTY] = 1
        if(len(vowel) == 0): vowel[EMPTY] = 1
        if(len(final) == 0): final[EMPTY] = 1    
        
        i_score = round(1-self.get_weighted_cost(init, t_init, self.initc_cost),2)
        v_score = round(1-self.get_weighted_cost(vowel, t_vowel, self.vow_cost),2)
        f_score = round(1-self.get_weighted_cost(final, t_final, self.finalc_cost),2)

        return i_score, v_score, f_score


    def get_weighted_cost(self, phones, target, func):
        psum = 0
        for phone in phones:
            psum += phones[phone]

        score = 0
        for phone in phones:
            score += (phones[phone]/psum)*func(phone, target)
     
        return score 