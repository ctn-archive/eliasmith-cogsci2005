D=128   # number of dimensions per ensemble
N=20    # number of neurons per ensemble is N*D
experiment=2   # 1 for learning in different contexts, 2 for generalization within a context
learning_rate=5e-7
stimulus_time=1.5

mode_other='direct'# mode to use for all neurons that aren't part of the learning system (or part of convolution)
mode_conv='direct' # mode to use for the convolution computation
# Set both mode parameters to 'default' to use spiking neurons for everything.  The resulting
#  model will run quite slowly....

import random
import nef
import hrr

# number of neurons to use for other neural groups
N_other=N*D
if mode_other=='direct': N_other=1

# number of neurons to use for convolution subcomponents
N_conv=300
if mode_conv=='direct': N_conv=1

net=nef.Network('Wason',seed=16)
vocab=hrr.Vocabulary(D,max_similarity=0.05)

context=net.make('context',N,1,intercept=(0.2,0.9))
rule=net.make('rule',N_other,D,mode=mode_other)

transform=net.make('transform',N*D,D)
answer=net.make('answer',N_other,D,mode='direct')

nef.convolution.make_convolution(net,'*',rule,transform,answer,N_conv,mode=mode_conv)


correct_transform=net.make('correct transform',N_other,D,mode=mode_other)
correct_answer=net.make('correct answer',N_other,D,mode='direct')
nef.convolution.make_convolution(net,'/',correct_answer,rule,correct_transform,N_conv,mode=mode_conv,invert_second=True)

nef.templates.learned_termination.make(net,'error',int(N*D*1.1),'context','transform',learning_rate)
error=net.get('error')

net.connect(transform,error,weight=-1)
net.connect(correct_transform,error)


error.addTermination('gate',[[-1]]*error.neurons,0.005,False)

import random
random.seed(99)  #seed for vocabulary items

if experiment==1:
    RULE1=vocab.parse('ANTE*VOWEL+CONS*EVEN')
    RULE2=vocab.parse('ANTE*DRINK+CONS*OVER18')
    ANSWER1=vocab.parse('VOWEL+EVEN')
    ANSWER2=vocab.parse('DRINK+NOT*OVER18')
    vocab.add('NOT_OVER18',vocab.parse('NOT*OVER18'))
    ANSWER1.normalize()
    ANSWER2.normalize()
    RULE1.normalize()
    RULE2.normalize()


    class Inputs(nef.SimpleNode):
        def origin_context(self):
            index=int(self.t_start/stimulus_time)%2
            return [[-1],[1]][index]
        def origin_rule(self):
            index=int(self.t_start/stimulus_time)%2
            return [RULE1.v,RULE2.v][index]
        def origin_answer(self):
            index=int(self.t_start/stimulus_time)%2
            return [ANSWER1.v,ANSWER2.v][index]
        def origin_errorgate(self):
            if self.t_start>stimulus_time*2:
                return [1]              # turn off learning
            else:
                return [0]              # allow learning

elif experiment==2:
    RULE1=vocab.parse('ANTE*DRINK+CONS*OVER21')
    RULE2=vocab.parse('ANTE*VOTE+CONS*OVER18')
    RULE3=vocab.parse('ANTE*DRIVE+CONS*OVER16')

    ANSWER1=vocab.parse('DRINK+NOT*OVER21')
    ANSWER2=vocab.parse('VOTE+NOT*OVER18')
    ANSWER3=vocab.parse('DRIVE+NOT*OVER16')
    vocab.add('NOT_OVER16',vocab.parse('NOT*OVER16'))
    vocab.add('NOT_OVER18',vocab.parse('NOT*OVER18'))
    vocab.add('NOT_OVER21',vocab.parse('NOT*OVER21'))
    
    
    ANSWER1.normalize()
    ANSWER2.normalize()
    ANSWER3.normalize()
    RULE1.normalize()
    RULE2.normalize()
    RULE3.normalize()


    class Inputs(nef.SimpleNode):
        def origin_context(self):
            return [1]
        def origin_rule(self):
            index=int(self.t_start/stimulus_time)%3
            return [RULE1.v,RULE2.v,RULE3.v][index]
        def origin_answer(self):
            index=int(self.t_start/stimulus_time)%3
            return [ANSWER1.v,ANSWER2.v,ANSWER3.v][index]
        def origin_errorgate(self):
            if self.t_start>stimulus_time*2:
                return [1]      # turn off learning
            else:
                return [0]      # allow learning


inputs=Inputs('inputs')
net.add(inputs)

net.connect(inputs.getOrigin('context'),context)
net.connect(inputs.getOrigin('rule'),rule)
net.connect(inputs.getOrigin('answer'),correct_answer)
net.connect(inputs.getOrigin('errorgate'),error.getTermination('gate'))

net.add_to_nengo()
net.set_layout({'state': 0, 'height': 579, 'width': 950, 'x': 0, 'y': 28},
 [(u'answer', None, {'label': False, 'height': 33, 'width': 82, 'x': 322, 'y': 219}),
  (u'answer', 'semantic pointer', {'label': True, 'normalize': False, 'sel_dim': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], 'last_maxy': 2.0000000000000013, 'height': 446, 'width': 514, 'x': 425, 'smooth_normalize': False, 'show_pairs': False, 'autozoom': False, 'y': 13}),
  (u'correct answer', None, {'label': False, 'height': 33, 'width': 158, 'x': 59, 'y': 405}),
  (u'correct transform', None, {'label': False, 'height': 33, 'width': 184, 'x': 165, 'y': 326}),
  (u'rule', None, {'label': False, 'height': 33, 'width': 49, 'x': 33, 'y': 237}),
  (u'context', None, {'label': False, 'height': 33, 'width': 85, 'x': 27, 'y': 29}),
  (u'transform', None, {'label': False, 'height': 33, 'width': 108, 'x': 104, 'y': 115}),
  (u'*', None, {'label': False, 'height': 33, 'width': 20, 'x': 138, 'y': 214}),
  (u'/', None, {'label': False, 'height': 33, 'width': 17, 'x': 135, 'y': 273}),
  (u'error', None, {'label': False, 'height': 33, 'width': 58, 'x': 232, 'y': 38})],
 {'dt': 0, 'show_time': 1.5, 'sim_spd': 4, 'filter': 0.03, 'rcd_time': 4.0})

