from typing import Optional
from mergic.ui import PromptResult


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
