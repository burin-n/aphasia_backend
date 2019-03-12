class scoring():
    
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


    def initc_score(self, x,y):
        #REF table: https://en.wikipedia.org/wiki/Thai_language#Initials
        #column: Labial, Alveolar, Palatal, Velar, Gloattal
        #row: Nasal, Plosive_voice, Plosive_tenuis, Plotsive_aspirated, Fricative, Approximant, Trill
        table = [[] for i in range(7)]
        table[0].extend(['m', 'n', '' , 'ng', ''])
        table[1].extend(['b', 'd', '' , '', ''])
        table[2].extend(['p', 't', 'c', 'k', 'z'])
        table[3].extend(['ph', 'th', 'ch', 'kh', ''])
        table[4].extend(['f', 's', '', '', 'h'])
        table[5].extend(['', 'l', 'j', 'w', ''])
        table[6].extend(['', 'r', '', '', ''])
        
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
        return min(dist, 4.0)/5.0
        
        
    # VOWEL ---------------------------------------------------------------------
        
        
    def get_dipthongs_j(self, x):
        if(x in ['ia', 'iia']): return 0.5
        elif(x in ['va','vva']): return 2.5
        else: return 4.5
        
        
    def vow_score(self, x,y):
        # REF table: https://en.wikipedia.org/wiki/Thai_language#Vowels
        # column: FUS, FUL, BUS, BUL, BRS, BRL
        # F: Front, B: Back, U: Unrounded, R: Rounded, S: Short, L: Long
        # row: High, Mid, Low 

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
        return  min(((2*(xi-yi))**2 + (xj-yj)**2 )**0.5, 4.0)/5.0


    # FINAL ---------------------------------------------------------------------

        
    def finalc_score(self, x, y):
        #REF table: https://en.wikipedia.org/wiki/Thai_language#Finals
        #column: Labial, Alveolar, Palatal, Velar
        #row: Nasal, Plosive, Approximant
        table = [[] for i in range(3)]
        table[0].extend([['m^'], ['n^', 'l^'], [], ['ng^']])
        table[1].extend([['p^', 'f^'], ['t^','s^','ch^'], [], ['k^']])
        table[2].extend([['w^'], [], ['j^'], []])
        
        #default as (Glottis)
        xi = 1; xj = 4; yi = 1; yj = 4
        
        for i in range(3):
            for j in range(4):
                if(x in table[i][j]):
                    xi = i; xj = j
                if(y in table[i][j]):
                    yi = i; yj = j
    #     return ((xi-yi)**2 + (xj-yj)**2)**0.5    
        return min(((xi-yi)**2 + (xj-yj)**2)**0.5, 3.3)/4.125
    
        
    # ----------------------------------------------------------------------

    def dist_scoring(self, speak, target):
        init, vowel, final = speak     
        t_final = ''
        
        if(len(target) == 3): t_init, t_vowel, t_final = target
        else: t_init, t_vowel = target
        
        i_cost = self.get_weighted_score(init, t_init, self.initc_score)
        v_cost = self.get_weighted_score(vowel, t_vowel, self.vow_score)
        f_cost = self.get_weighted_score(final, t_final, self.finalc_score)

        return i_cost, v_cost, f_cost


    def get_weighted_score(self, phones, target, func):
        psum = 0
        for phone in phones:
            psum += phones[phone]

        cost = 0
        for phone in phones:
            cost += (phones[phone]/psum)*func(phone, target)

        return cost 