from B4_Automata import Automata


for i in range(1, 45):
    t = Automata(f"automaton/B4-{i}.txt")
    s = f"{f'TEST : Automate N°{i}':=^100}\n"
    with open(f"out/tests/B4-{i}.txt", 'w') as f:
        
        s += 2*'\n'
        s += str(t)
        s += 2*'\n'

        s += f"{'Information':-^50}\n"
        s += t.get_info()
        s += 2*'\n'
        
        s += f"{'Complétion':-^50}\n"
        s += str(t.get_complete())
        s += 2*'\n'
        
        s += f"{'Standardisation':-^50}\n"
        s += str(t.get_standard())
        s += 2*'\n'
        
        s += f"{'Determinisation':-^50}\n"
        s += str(t.get_determinized())
        s += 2*'\n'
        
        s += f"{'Complementaire':-^50}\n"
        s += str(t.get_complementary())
        s += 2*'\n'
        
        s += f"{'Ex simplification : complémentaire':-^50}\n"
        s += str(t.get_complementary()
                  .get_simplified())
        s += 2*'\n'        
        
        try:
            s += f"{'Minimiser':-^50}\n"
            s += str(t.get_minimized())
            s += 2*'\n'
        except:
            pass
        
        s += f"{'Test de mot : `aabb` ':-^50}\n"
        s += str(t.test_word('aabb'))
        s += 2*'\n'

        s += 100*'='
        f.write(s)