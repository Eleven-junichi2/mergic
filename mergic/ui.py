from dataclasses import dataclass, field


@dataclass(init=False)
class PromptResult[T]:
    """This class represents the result of a User Selection on UI.
    The reason for wrapping the result in this class is to
    prevent values such as 0 and "" from being considered False."""

    value: T = field(init=False)
    _is_ok: bool = field(init=False)

    @classmethod
    def Ok(cls, value: T):
        wrapper = PromptResult[T]()
        wrapper.value = value
        wrapper._is_ok = True
        return wrapper

    @classmethod
    def Cancel(cls):
        wrapper = PromptResult[T]()
        wrapper._is_ok = False
        return wrapper

    def __bool__(self):
        return self._is_ok

    def unwrap(self) -> T:
        return self.value



