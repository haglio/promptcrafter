from promptcrafter.types import (
    Control,
    DisabledOrHiddenBy,
    Option,
    PluralText,
    Schema,
    Section,
    Submenu,
)

schema = Schema(sections=[
    Section(
        id="or types",
        text="or types",
        controls=[
            Control(
                id="count",
                text="count",
                kind="or-prefix",
                options=[
                    Option(id="or", text="or"),
                    Option(
                        id="two",
                        text="two",
                        submenu=Submenu(
                            kind="and-adv",
                            options=[Option(id="different", text="different")],
                        ),
                    ),
                ],
            ),
            Control(
                id="alignment",
                text="alignment",
                kind="or",
                options=[
                    Option(id="hero", text=PluralText(singular="hero", plural="heroes")),
                    Option(id="villain", text=PluralText(singular="villain", plural="villains")),
                ],
            ),
            Control(
                id="climbing",
                text="climbing",
                kind="or-adv",
                options=[
                    Option(id="funnily", text="funnily"),
                    Option(id="weirdly", text="weirdly"),
                    Option(id="happily", text="happily"),
                ],
            ),
            Control(
                id="armor",
                text="armor",
                kind="or-adj",
                options=[
                    Option(id="chrome", text="chrome"),
                    Option(id="obsidian", text="obsidian"),
                    Option(id="bone", text="bone"),
                ],
            ),
        ],
    ),
    Section(
        id="and types",
        text="and types",
        controls=[
            Control(
                id="reading",
                text="reading",
                kind="and-commas-adv",
                options=[
                    Option(id="books", text="books"),
                    Option(id="magazines", text="magazines"),
                    Option(id="blogs", text="blogs"),
                ],
            ),
            Control(
                id="kicking",
                text="kicking",
                kind="and-commas-adv",
                options=[
                    Option(id="the bucket", text="the bucket"),
                    Option(
                        id="the ladder",
                        text="the ladder",
                        submenu=Submenu(
                            kind="or-adj",
                            options=[
                                Option(id="big", text="big"),
                                Option(id="small", text="small"),
                            ],
                        ),
                    ),
                    Option(
                        id="pigeons",
                        text="pigeons",
                        submenu=Submenu(
                            kind="or-adv",
                            options=[
                                Option(id="in the park", text="in the park"),
                                Option(id="with a vengeance", text="with a vengeance"),
                            ],
                        ),
                    ),
                ],
            ),
            Control(
                id="render",
                text="render",
                kind="and-spaces-adj",
                custom_text="rendering",
                options=[
                    Option(id="cinematic", text="cinematic"),
                    Option(id="hyperdetailed", text="hyperdetailed"),
                    Option(id="volumetric", text="volumetric"),
                ],
            ),
        ],
    ),
    Section(
        id="negative prompt",
        text="negative prompt",
        prompt_target="negative",
        controls=[
            Control(
                id="stay safe",
                text="stay safe",
                kind="required",
                initially_selected_options=["space robo dino demon monster"],
                options=[Option(id="space robo dino demon monster", text="space robo dino demon monster")],
            ),
            Control(
                id="wakka",
                text="wakka",
                kind="toggle",
                initially_selected_options=True,
                options=[Option(id="no clutter", text="no clutter")],
            ),
            Control(
                id="camera angle",
                text="camera angle",
                kind="and-commas",
                disabled_bys=[DisabledOrHiddenBy(control_id="wakka")],
                options=[
                    Option(id="low", text="low"),
                    Option(id="overhead", text="overhead"),
                    Option(id="dutch", text="dutch"),
                ],
            ),
        ],
    ),
])
