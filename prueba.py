from automata.fa.dfa import DFA
dfa = DFA(states={'q0','q1'}, input_symbols={'0','1'},
    transitions={'q0':{'0':'q0','1':'q1'}, 'q1':{'0':'q0','1':'q1'}},
    initial_state='q0', final_states={'q1'})
print(dfa.accepts_input('0101'), dfa.accepts_input('0110'))
dfa.show_diagram(path='afd.png')
