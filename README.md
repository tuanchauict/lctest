# lctest

A small library for simulate running leetcode

## Installation
```
pip3 install lctest
```
See more at: https://www.piwheels.org/project/lctest/
## Sample

```python
from lctest import *
from lctest.stdlib import *


# noinspection PyMethodMayBeStatic
@testcase(
    ([0, 1], [2,7,11,15], 9), # (expected, param0, param1, ...), when expected matches the result, print log will be filtered out
    (None, [3,2,4], 9) # use None for expected if no need to do assessment. print log will be kept
)
class Solution:
    @solution
    def twoSum(self, nums, target):
        store = {}
        for index, num in enumerate(nums):
            if num in store:
                return [store[num], index]
            store[target - num] = index
        return []
```

then run the file

Check the code for more apis
