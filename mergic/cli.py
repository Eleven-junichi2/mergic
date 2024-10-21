from dataclasses import dataclass, field
from typing import Optional


@dataclass(init=False)
class PromptResult[T]:
    """This class represents the result of a CLI prompt.
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


def ask_yes_no(question: str, prompt_symbol=">") -> bool:
    answer = input(f"{question}(y/n)" + prompt_symbol)
    return True if answer in ("y", "") else False


def inquire_typed_value[T](
    prompt,
    type_: type[T],
    default_value: Optional[T] = None,
    ask_cancel=True,
    prompt_symbol=">",
) -> PromptResult[T]:
    while True:
        try:
            display_default = f"(デフォルト={default_value})" if default_value else ""
            value = input(f"{prompt}{display_default}{prompt_symbol}")
            if value == "":
                if default_value:
                    return PromptResult.Ok(default_value)
            value = type_(value)
        except ValueError:
            if ask_cancel:
                if ask_yes_no("やめる？"):
                    return PromptResult.Cancel()
                else:
                    continue
            else:
                continue
        else:
            return PromptResult.Ok(value)
