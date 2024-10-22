from mergic.wizard import auto_name, spell_factory


def playground_cli():
    print("Wizard's playground")
    int_spell = int(input("integer spell: "))
    strength = int(input("strength: "))
    spell = spell_factory.generate(int_spell, strength)
    print(spell.traits)
    print(spell.alchemical_elements)
    print(spell.strength)
    print(spell.generator_integer)
    for language_code in ("en", "ja"):
        print(
            f"auto-generated name({language_code}): ", auto_name(spell, language_code)
        )


if __name__ == "__main__":
    playground_cli()
