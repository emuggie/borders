# PWORM : Python Web On Relaid Modules
Experimental web framework for Serverlease based on python3

## Concept
Borders is Restful, stateless, web framework aims for more straight forward, simpler designs for web services.  

## Installation
For now, distribution on pypi is pending due to some of works which hasn't done yet.

## Hello World
```python

```
## Integration with Flask
By calling ``handle()`` function, you can follow chains you wish or remap if needed.
So basically, it is possible to integrate most of frameworks or tools there is.

## Filter chain
if request with path '/land/of/promise', Borders look up handlers with following rules.
/index.py -> /land.py -> /land/index.py -> /land/of.py -> /land/of/index.py -> /land/of/promise.py -> /land/of/promise/index.py
Each handler functions result passed to next handlers as arguments.
If ``proceed()`` function is invoked, it will return next handlers result which means by try catching error or reading result value,
prior handler can fully controll the result of next chains.
If ``proceed()`` is not invoked on previous handler, it will forced to execute to keep the chain.(Still, return value from previous will be passed as arguments)

Before invoking handler chain, there are to options which tells Borders framework to behave.
``on()`` tells that handler should be applied when condition has met.
``block()`` tells that handler will take care or requiest though request path is not exactly match.

# Scope and context
Of course, context can be varying depends on the server, or integrated frameworks, Borders manages context based on coroutine context.
``getLocal()`` function offers request scoped object which is shared through filter chain, possibly share requests, sessions if there is, etc.
This RequestContext is bound to coroutine task but if task is not reachable, context is bound to thread.
So beware if you create new event loop or task which tries to share context. Or you can create your own and manage as you wish.

## Logging
Border uses default python logging pacakages.
Just little pretty printing and additional features added.

## Interanl Server
Based on pythone server.HTTP pacakage, But additional feature is that it works on threaded event loop.
And ExtendedHTTPHandler based on BaseHTTPHandler, and you can set your custom Handler if you desire.

