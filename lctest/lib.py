class ListNode:
    def __init__(self, x, next=None):
        self.val = x
        self.next = next

    def __str__(self):
        arr = []
        cur = self
        circle_at = None
        while cur:
            if cur in arr:
                circle_at = cur
                break
            arr.append(cur)
            cur = cur.next
        values = list(map(lambda x: x.val, arr))
        if circle_at:
            return f"{values} ○ {arr.index(circle_at)}|{circle_at.val}"
        else:
            return f"{values}"


class TreeNode:
    def __init__(self, val, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

    def __str__(self):
        arr = []

        def dfs(node: TreeNode):
            if not node:
                arr.append(None)
                return
            arr.append(node.val)
            if not node.left and not node.right:
                return
            dfs(node.left)
            dfs(node.right)

        dfs(self)
        return str(arr)


def linked_list(*arr, tail=None) -> ListNode:
    dummy = ListNode(0)
    last = dummy
    for item in arr:
        node = ListNode(item)
        last.next = node
        last = last.next

    if tail is not None:
        last.next = dummy.next
        while tail > 0:
            last.next = last.next.next
            tail -= 1

    return dummy.next


def tree2(*arr) -> TreeNode:
    """
    :param arr: Format: Same format as Leetcode
    :return:
    """

    if not arr:
        raise Exception()

    def standardize(arr):
        rows = [(arr[0],)]
        index = 1
        while index < len(arr):
            cur = rows[-1]
            valid_count = len(cur) - cur.count(None)
            next_row = arr[index:index + valid_count * 2]
            for i, v in enumerate(cur):
                if v is None:
                    next_row = next_row[:2 * i] + (None, None) + next_row[2 * i:]
            index += valid_count * 2
            rows.append(next_row)
        res = []
        for row in rows:
            res += row
        return res

    arr = standardize(arr)
    values = list(arr)
    root = TreeNode(values.pop(0))
    level = [root]

    def accept(node: TreeNode):
        return node if node.val is not None else None

    while values:
        items_left = len(values)
        required_items = len(level) * 2
        if items_left < required_items:
            values += [None] * (required_items - items_left)
        nodes = [TreeNode(v) for v in values[:required_items]]

        for i, n in enumerate(level):
            n.left = accept(nodes[i * 2])
            n.right = accept(nodes[i * 2 + 1])

        level = nodes

        values = values[required_items:]

    return root


class LoopError(Exception):
    def __init__(self, item):
        self.loop_item = item

    def __str__(self):
        return "Loop with %s" % self.loop_item.val


def linked_list_to_array(head):
    """
    :param head: NodeList
    :return: list
    """
    read_set = set()
    result = []
    first = head
    while first:
        if first in read_set:
            raise LoopError(first)
        read_set.add(first)
        result.append(first.val)
        first = first.next
    return result


def print_linked_list(head):
    if not head:
        print("Empty")
    first = head
    while first is not None:
        print("> %s" % first.val)
        first = first.next


def print_table(table):
    max_length = 0
    for row in table:
        for item in row:
            max_length = max(max_length, len(str(item)))

    format_str = "%" + str(max_length + 2) + "s"
    for row in table:
        print("".join([format_str % item for item in row]))
    print()