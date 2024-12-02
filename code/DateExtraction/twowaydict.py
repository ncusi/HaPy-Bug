
class TwoWayDict(dict):
    def __setitem__(self, __key, __value) -> None:
        if __key in self:
            del self[__key]
        if __value in self:
            del self[__value]
        dict.__setitem__(self, __key, __value)
        dict.__setitem__(self, __value, __key )

    def __delitem__(self, __key) -> None:
        dict.__delitem__(self, self[__key])
        dict.__delitem__(self, __key)

    def __len__(self) -> int:
        return dict.__len__(self) / 2
    
