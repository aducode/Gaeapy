# Gaeapy

[Gaea](https://github.com/58code/Gaea) python client

### Install

> 1. git clone https://github.com/aducode/Gaeapy.git
> 2. cd Gaeapy
> 3. python setup.py install

### Usage

```python
from gaea.core import String, Int, Serializer, serializer
from gaea.core import service, operation

from gaea.client import proxy

serializer(name=String, age=Int)
class Persion(Serializer):
    """
    Persion类
    """
    pass

@proxy(('127.0.0.1', 9090))
@service()
class PersionService(object):

    @operation(name='getPersionById', args=(Int,), ret=Persion)
    def get_persion_by_id(persion_id):
        pass

if __name__ == '__main__':
    persion_service = PersionService()
    persion = persion_service.get_persion_by_id(0)
```

### TODO

> 1. 支持枚举类型
> 2. 规范异常
> 3. 支持Serializable类继承关系
