# Serial #
This module is a swiss army knife for serializability theory! It defines data
types for read, write, abort, and commit actions; transactions over those
actions; and schedules over transactions. Then, given a schedule, it can
determine whether it is

1. view-serializable,
2. conflict-serializable,
3. recoverable,
4. avoids cascading aborts, or
5. strict.

Moreover, we can pretty print schedules to LaTeX, tabularize schedules to
LaTeX, or generate the conflict-graph of the schedule using matplotlib.

But wait, there's more! We can also generate random schedules and use our
predicates to find a schedule satisfying each of the entries in the cross
product of serializability and recoverability:

```
{ conflict-serializable                        }   { strict               }
{ view-serializable, not conflict-serializable } x { aca, not strict      }
{ not view-serializable                        }   { recoverable, not aca }
                                                   { not recoverable      }
```

## Getting Started ##
It's recommended, though not necessary, that you use `virtualenv`. Install
`pip` and `virtualenv` and then run the following:

```bash
virtualenv .
source bin/activate
pip instsall -r requirements.json
```

Run `make test` to test the code, `make clean` to clean up garbage, and run
`python schedule.py` to generate random schedules satisfying various
properties. `serial.py` contains the meat of the code.
