from shop2.domain import Task, Operator, Method
from shop2.planner import planner, StopException, FailedPlanException
from shop2.fact import Fact
from shop2.common import V
from shop2.conditions import Filter, NOT


#Domain Description
Domain = {
        "intAdd/3": [ 
            Operator(head=('intAdd', V('x'), V('y'), V('z')),
                        preconditions=(Fact(field=V('x'), value=V('vx'))&
                                      Fact(field=V('y'), value=V('vy'))),
                        effects=Fact(field=V('z'), value=(lambda x,y: x+y, V('vx'), V('vy')))),
            
        ],

        "intMult/3": [
            Operator(head=('intMult', V('x'), V('y'), V('z')),
                     preconditions=(Fact(field=V('x'), value=V('vx'))&
                                   Fact(field=V('y'), value=V('vy'))),
                     effects=Fact(field=V('z'), value=(lambda x,y: x*y, V('vx'), V('vy')))),
        ],

        "fracAdd/4": [
            Method(head=('fracAdd', V('xn'), V('yn'), V('xd'), V('yd')),
                   preconditions=(Fact(field=V('xn'), value=V('vnx'))& 
                                   Fact(field=V('yn'), value=V('vny'))& 
                                   Fact(field=V('xd'), value=V('vd'))& 
                                   Fact(field=V('yd'), value=V('vd'))),
                   subtasks=[Task('intAdd', 'xn', 'yn', 'nom'), Task('assign', 'xd', 'denom')],
            ),
            Method(head=('fracAdd', V('xn'), V('yn'), V('xd'), V('yd')),
                   preconditions=(Fact(field=V('xn'), value=V('vnx'))& 
                                  Fact(field=V('yn'), value=V('vny'))& 
                                  Fact(field=V('xd'), value=V('vxd'))& 
                                  Fact(field=V('yd'), value=V('vyd'))),
                   subtasks=([(Task('intMult', V('xn'), V('yd'), 'nom1'), Task('intMult', V('yn'), V('xd'), 'nom2')), Task('intAdd', 'nom1', 'nom2', 'nom')],
                             Task('intMult', 'xd', 'yd', 'denom'))
                 ),
                
        ],

        "fracMult/4": [
            Method(head=('fracMult', V('xn'), V('yn'), V('xd'), V('yd')),
                   preconditions=(Fact(field=V('xn'), value=V('vnx'))&
                                   Fact(field=V('yn'), value=V('vny'))&
                                   Fact(field=V('xd'), value=V('vxd'))&
                                   Fact(field=V('yd'), value=V('vyd'))),
                   subtasks=[Task('intMult', 'xn', 'yn', 'nom'), Task('intMult', 'xd', 'yd', 'denom')]
            ),
        ],
                            
        "add/0": [
            Method(head=('add',),
                   preconditions=(Fact(field=V('xn'), value=V('vnx'))&
                                  Fact(field=V('yn'), value=V('vny'))&
                                  Fact(field=V('xd'), value=V('vdx'))&
                                  Fact(field=V('yd'), value=V('vdy'))&
                                  Filter(lambda xn,yn,xd,yd: xn=='xn' and yn=='yn' and xd=='xd' and yd=='yd')),
                   subtasks=[Task('fracAdd', V('xn'), V('yn'), V('xd'), V('yd'))]
            ),
            Method(head=('add',),
                   preconditions=(Fact(field=V('x'), value=V('vx'))&
                                  Fact(field=V('y'), value=V('vy'))&
                                  Filter(lambda x,y: x!=y)),
                   subtasks=[Task('intAdd', V('x'), V('y'), 'ans')]
            ),
        ],

        "mult/0": [
            Method(head=('mult',),
                   preconditions=(Fact(field=V('xn'), value=V('vnx'))&
                                   Fact(field=V('yn'), value=V('vny'))&
                                   Fact(field=V('xd'), value=V('vdx'))&
                                   Fact(field=V('yd'), value=V('vdy'))&
                                   Filter(lambda xn,yn,xd,yd: xn=='xn' and yn=='yn' and xd=='xd' and yd=='yd')),
                   subtasks=[Task('fracMult', V('xn'), V('yn'), V('xd'), V('yd'))]
            ),
            Method(head=('mult',),
                   preconditions=(Fact(field=V('x'), value=V('vx'))&
                                  Fact(field=V('y'), value=V('vy'))&
                                  Filter(lambda x,y: x!=y)),
                   subtasks=[Task('intMult', V('x'), V('y'), 'ans')]
            ),
        ],
                                    
        "solve/0":  [
            Method(head=('solve',),
                   preconditions=Fact(field=V('op'), operator='*'),
                   subtasks=[Task('mult',)]
            ),
            Method(head=('solve',),
                   preconditions=Fact(field=V('op'), operator='+'),
                   subtasks=[Task('add',)]
            ),

        ],
}

def helper_function(state, action_name, x, y, z):
       x_value, y_value = None, None
       for fact in state:
              if fact['field'] == x:
                     x_value = fact['value']
              if fact['field'] == y:
                     y_value = fact['value']

       if action_name == 'intAdd':
              z_value = x_value + y_value
       elif action_name == 'intMult':
              z_value = x_value * y_value
       state = state & Fact(field=z, value=z_value)
       return state

if __name__ == "__main__":

       numerator_x, numerator_y = 2, 5
       denominator_x, denominator_y = 6, 5
       operator = "+"
       state = (Fact(field='op', operator=operator)&
              Fact(field='xn', value=numerator_x)&
              Fact(field='yn', value=numerator_y)&
              Fact(field='xd', value=denominator_x)&
              Fact(field='yd', value=denominator_y))
       
    
       Tasks = [Task('solve',)]
       plan = planner(state, Tasks, Domain)

       try: 
              action_name, action_args = plan.send(None)
              # Call helper functions to perform action_name over action_args to change state
              state = helper_function(state, action_name, *action_args)
              
              while True:
                     action_name, action_args = plan.send((True, state))
                     # Call helper functions to perform action_name over action_args to change state
                     state = helper_function(state, action_name, *action_args)
       except StopException as e: 
              print(e)
       except FailedPlanException as e:
              print(e)



    