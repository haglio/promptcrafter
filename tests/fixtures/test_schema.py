from promptcrafter.types import (
    Control,
    DisabledOrHiddenBy,
    GlobalSubstitution,
    Option,
    PluralText,
    Schema,
    Section,
    Submenu,
    SupplementedBy,
)

TEST_SCHEMA = Schema(sections=[
    Section(
        id="subject-core",
        text="subject-core",
        controls=[
            Control(
                id="subject-base",
                text="subject-base",
                kind="required",
                initially_selected_options=["space robo dino demon monster"],
                options=[Option(id="space robo dino demon monster", text="space robo dino demon monster")],
            ),
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
                id="silhouette",
                text="silhouette",
                kind="or-adv",
                custom_text="outline",
                options=[
                    Option(id="towering", text="towering"),
                    Option(id="lanky", text="lanky", custom_control_text="frame"),
                    Option(id="hulking", text="hulking"),
                ],
            ),
            Control(
                id="movement",
                text="movement",
                kind="or-adv",
                options=[
                    Option(id="swiftly", text="swiftly"),
                    Option(id="heavily", text="heavily"),
                ],
            ),
            Control(
                id="element prefix",
                text="element prefix",
                kind="or-prefix",
                options=[
                    Option(id="void", text="void"),
                    Option(id="plasma", text="plasma"),
                    Option(id="nebula", text="nebula"),
                ],
            ),
            Control(
                id="armor",
                text="armor",
                kind="or-adj",
                supplemented_bys=[
                    SupplementedBy(
                        control_id="element prefix",
                        supplemental_text="elemental",
                        side="adv",
                    ),
                    SupplementedBy(
                        control_id="movement",
                        supplemental_text="moving",
                        side="adj",
                    ),
                ],
                options=[
                    Option(id="chrome", text="chrome"),
                    Option(id="obsidian", text="obsidian"),
                    Option(id="bone", text="bone"),
                ],
            ),
            Control(
                id="surface treatment",
                text="surface treatment",
                kind="or-adj",
                custom_text="plating",
                supplemented_bys=[
                    SupplementedBy(
                        option_id="nebula",
                        supplemental_text="within nebula",
                        side="adv",
                    ),
                    SupplementedBy(
                        option_id="plasma",
                        supplemental_text="plasma",
                        side="adj",
                    ),
                ],
                options=[
                    Option(id="runed", text="runed"),
                    Option(id="etched", text="etched"),
                ],
            ),
        ],
    ),
    Section(
        id="details",
        text="details",
        controls=[
            Control(
                id="appendages",
                text="appendages",
                kind="and-commas",
                options=[
                    Option(
                        id="wings",
                        text="wings",
                        submenu=Submenu(
                            kind="or-adj",
                            options=[
                                Option(id="feathered", text="feathered"),
                                Option(id="mechanical", text="mechanical"),
                            ],
                        ),
                    ),
                    Option(
                        id="horns",
                        text="horns",
                        submenu=Submenu(
                            kind="or-adv",
                            options=[
                                Option(id="wishily", text="wishily"),
                                Option(id="washily", text="washily"),
                            ],
                        ),
                    ),
                    Option(
                        id="tail",
                        text="tail",
                        submenu=Submenu(
                            kind="and-adj",
                            options=[
                                Option(id="barbed", text="barbed"),
                                Option(id="segmented", text="segmented"),
                            ],
                        ),
                    ),
                    Option(
                        id="antennae",
                        text="antennae",
                        submenu=Submenu(
                            kind="and-adv",
                            options=[
                                Option(id="arched", text="arched"),
                                Option(id="flared", text="flared"),
                            ],
                        ),
                    ),
                ],
            ),
            Control(
                id="eye color",
                text="eye color",
                kind="or",
                options=[
                    Option(id="green", text="green"),
                    Option(id="black", text="black"),
                    Option(id="red", text="red"),
                ],
            ),
            Control(
                id="temperature",
                text="temperature",
                kind="or",
                options=[
                    Option(id="hot", text="hot"),
                    Option(id="cold-positive", text="cold"),
                ],
            ),
            Control(
                id="sitting on",
                text="sitting on",
                kind="and-commas-adv",
                custom_text="alighting upon",
                options=[
                    Option(id="etchings", text="etchings"),
                    Option(id="scars", text="scars"),
                    Option(id="glow", text="glow"),
                ],
            ),
            Control(
                id="surface borks",
                text="surface borks",
                kind="and-commas-adv",
                options=[
                    Option(id="fetchings", text="fetchings"),
                    Option(id="fscars", text="fscars"),
                    Option(id="fglow", text="fglow"),
                ],
            ),
            Control(
                id="stance",
                text=PluralText(singular="stance", plural="stances"),
                kind="and-commas-adv",
                options=[
                    Option(id="lunging", text="lunging"),
                    Option(id="roaring", text="roaring"),
                    Option(id="three-quarter", text="three-quarter"),
                ],
            ),
            Control(
                id="render style",
                text="render style",
                kind="and-spaces-adj",
                options=[
                    Option(id="cinematic", text="cinematic"),
                    Option(id="hyperdetailed", text="hyperdetailed"),
                    Option(id="volumetric", text="volumetric"),
                    Option(id="green tinted", text="green tinted"),
                    Option(id="black and white", text="black and white"),
                ],
            ),
            Control(
                id="finish profile",
                text="finish profile",
                kind="and-spaces-adj",
                custom_text=PluralText(singular="finish", plural="finishes"),
                options=[
                    Option(id="matte", text="matte"),
                    Option(id="pearlescent", text="pearlescent"),
                ],
            ),
        ],
    ),
    Section(
        id="accent",
        text=PluralText(singular="accent", plural="accents"),
        controls=[
            Control(
                id="accent",
                text="accent",
                kind="and-commas-adv",
                options=[Option(id="striped", text="striped")],
            ),
        ],
    ),
    Section(
        id="colorize",
        text="colorize",
        controls=[
            Control(
                id="colorize",
                text="colorize",
                kind="global-selector",
                options=[
                    Option(id="green", text="green"),
                    Option(id="black", text="black"),
                ],
            ),
        ],
    ),
    Section(
        id="modes",
        text="modes",
        controls=[
            Control(
                id="is portrait",
                text="is portrait",
                kind="toggle",
                options=[Option(id="portrait", text="portrait")],
            ),
            Control(
                id="thorax mode",
                text="thorax mode",
                kind="toggle",
                global_substitutions=[
                    GlobalSubstitution(
                        from_text="torso",
                        to_text="thorax",
                        from_plural="torsos",
                        to_plural="thoraces",
                    ),
                ],
                options=[Option(id="replace torso terminology", text="replace torso terminology")],
            ),
            Control(
                id="camera angle",
                text="camera angle",
                kind="or",
                disabled_bys=[DisabledOrHiddenBy(control_id="is portrait")],
                options=[
                    Option(id="low", text="low"),
                    Option(id="overhead", text="overhead"),
                    Option(id="dutch", text="dutch"),
                ],
            ),
            Control(
                id="portrait focus",
                text="portrait focus",
                kind="and-commas",
                hidden_bys=[DisabledOrHiddenBy(control_id="is portrait")],
                options=[
                    Option(id="face", text="face"),
                    Option(id="torso", text="torso"),
                    Option(id="torso side profile", text="torso side profile"),
                    Option(id="torsos", text="torsos"),
                ],
            ),
            Control(
                id="pose",
                text="pose",
                kind="or",
                options=[
                    Option(id="grounded", text="grounded"),
                    Option(
                        id="floating",
                        text="floating",
                        disabled_bys=[DisabledOrHiddenBy(control_id="is portrait")],
                    ),
                    Option(
                        id="airborne",
                        text="airborne",
                        hidden_bys=[DisabledOrHiddenBy(control_id="is portrait")],
                    ),
                ],
            ),
            Control(
                id="portrait pose",
                text="portrait pose",
                kind="or",
                revealed_bys=[DisabledOrHiddenBy(control_id="is portrait")],
                options=[
                    Option(
                        id="close crop",
                        text="close crop",
                        revealed_bys=[DisabledOrHiddenBy(control_id="is portrait")],
                    ),
                    Option(id="tight profile", text="tight profile"),
                ],
            ),
        ],
    ),
    Section(
        id="torso references",
        text="torso references",
        controls=[
            Control(
                id="torso mentions",
                text="torso mentions",
                kind="and-commas",
                options=[
                    Option(id="torso badge", text="torso badge"),
                    Option(id="torsos", text="torsos"),
                ],
            ),
        ],
    ),
    Section(
        id="portrait extras",
        text="portrait extras",
        revealed_bys=[DisabledOrHiddenBy(control_id="is portrait")],
        controls=[
            Control(
                id="portrait lighting",
                text="portrait lighting",
                kind="or-adj",
                options=[
                    Option(id="rim-lit", text="rim-lit"),
                    Option(id="soft-lit", text="soft-lit"),
                ],
            ),
        ],
    ),
    Section(
        id="section disabled target",
        text="section disabled target",
        disabled_bys=[DisabledOrHiddenBy(control_id="is portrait")],
        controls=[
            Control(
                id="section disabled sample",
                text="section disabled sample",
                kind="and-commas",
                options=[
                    Option(id="locked out while portrait", text="locked out while portrait"),
                ],
            ),
        ],
    ),
    Section(
        id="section hidden target",
        text="section hidden target",
        hidden_bys=[DisabledOrHiddenBy(control_id="is portrait")],
        controls=[
            Control(
                id="section hidden sample",
                text="section hidden sample",
                kind="and-commas",
                options=[
                    Option(id="gone while portrait", text="gone while portrait"),
                ],
            ),
        ],
    ),
    Section(
        id="negative modes",
        text="negative modes",
        prompt_target="negative",
        controls=[
            Control(
                id="negative-switch",
                text="negative-switch",
                kind="toggle",
                initially_selected_options=True,
                options=[Option(id="no clutter", text="no clutter")],
            ),
        ],
    ),
    Section(
        id="negative polish",
        text="negative polish",
        prompt_target="negative",
        controls=[
            Control(
                id="neg-quality",
                text="neg-quality",
                kind="and-commas",
                initially_selected_options=["blurry"],
                options=[
                    Option(id="blurry", text="blurry"),
                    Option(id="muddy", text="muddy"),
                    Option(id="extra limbs", text="extra limbs"),
                ],
            ),
            Control(
                id="neg-temperature-opposite",
                text="neg-temperature-opposite",
                kind="hidden-opposite",
                hidden_opposite_bys=[DisabledOrHiddenBy(option_id="hot")],
                initially_selected_options=["cold-negative"],
                options=[Option(id="cold-negative", text="cold")],
            ),
        ],
    ),
])
