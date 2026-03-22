import type { Schema } from "../../types";

export const testSchema: Schema = {
  sections: [
    {
      id: 'subject-core',
      text: 'subject-core',
      controls: [
        {
          id: 'subject-base',
          text: 'subject-base',
          kind: 'required',
          initiallySelectedOptions: ['space robo dino demon monster'],
          options: [{ id: 'space robo dino demon monster', text: 'space robo dino demon monster' }],
        },
        {
          id: 'count',
          text: 'count',
          kind: 'or-prefix',
          options: [
            { id: 'or', text: 'or' },
            {
              id: 'two',
              text: 'two',
              submenu: {
                kind: 'and-adv',
                options: [
                  { id: 'different', text: 'different' },
                ]
              }
            }
          ]
        },
        {
          id: 'alignment',
          text: 'alignment',
          kind: 'or',
          options: [
            { id: 'hero', text: { singular: 'hero', plural: 'heroes' } },
            { id: 'villain', text: { singular: 'villain', plural: 'villains' } }
          ]
        },
        {
          id: 'silhouette',
          text: 'silhouette',
          kind: 'or-adv',
          customText: 'outline',
          options: [
            { id: 'towering', text: 'towering' },
            { id: 'lanky', text: 'lanky', customControlText: 'frame' },
            { id: 'hulking', text: 'hulking' }
          ]
        },
        {
          id: 'movement',
          text: 'movement',
          kind: 'or-adv',
          options: [
            { id: 'swiftly', text: 'swiftly' },
            { id: 'heavily', text: 'heavily' }
          ]
        },
        {
          id: 'element prefix',
          text: 'element prefix',
          kind: 'or-prefix',
          options: [
            { id: 'void', text: 'void' },
            { id: 'plasma', text: 'plasma' },
            { id: 'nebula', text: 'nebula' }
          ]
        },
        {
          id: 'armor',
          text: 'armor',
          kind: 'or-adj',
          supplementedBys: [
            {
              controlId: 'element prefix',
              supplementalText: 'elemental',
              side: 'adv'
            },
            {
              controlId: 'movement',
              supplementalText: 'moving',
              side: 'adj'
            }
          ],
          options: [
            { id: 'chrome', text: 'chrome' },
            { id: 'obsidian', text: 'obsidian' },
            { id: 'bone', text: 'bone' }
          ]
        },
        {
          id: 'surface treatment',
          text: 'surface treatment',
          kind: 'or-adj',
          customText: 'plating',
          supplementedBys: [
            {
              optionId: 'nebula',
              supplementalText: 'within nebula',
              side: 'adv'
            },
            {
              optionId: 'plasma',
              supplementalText: 'plasma',
              side: 'adj'
            }
          ],
          options: [
            { id: 'runed', text: 'runed' },
            { id: 'etched', text: 'etched' }
          ]
        }
      ]
    },
    {
      id: 'details',
      text: 'details',
      controls: [
        {
          id: 'appendages',
          text: 'appendages',
          kind: 'and-commas',
          options: [
            {
              id: 'wings',
              text: 'wings',
              submenu: {
                kind: 'or-adj',
                options: [
                  { id: 'feathered', text: 'feathered' },
                  { id: 'mechanical', text: 'mechanical' }
                ]
              }
            },
            {
              id: 'horns',
              text: 'horns',
              submenu: {
                kind: 'or-adv',
                options: [
                  { id: 'wishily', text: 'wishily' },
                  { id: 'washily', text: 'washily' }
                ]
              }
            },
            {
              id: 'tail',
              text: 'tail',
              submenu: {
                kind: 'and-adj',
                options: [
                  { id: 'barbed', text: 'barbed' },
                  { id: 'segmented', text: 'segmented' }
                ]
              }
            },
            {
              id: 'antennae',
              text: 'antennae',
              submenu: {
                kind: 'and-adv',
                options: [
                  { id: 'arched', text: 'arched' },
                  { id: 'flared', text: 'flared' }
                ]
              }
            }
          ]
        },
        {
          id: 'eye color',
          text: 'eye color',
          kind: 'or',
          options: [
            { id: 'green', text: 'green' },
            { id: 'black', text: 'black' },
            { id: 'red', text: 'red' }
          ]
        },
        {
          id: 'temperature',
          text: 'temperature',
          kind: 'or',
          options: [
            { id: 'hot', text: 'hot' },
            { id: 'cold-positive', text: 'cold' }
          ]
        },
        {
          id: 'sitting on',
          text: 'sitting on',
          kind: 'and-commas-adv',
          customText: 'alighting upon',
          options: [
            { id: 'etchings', text: 'etchings' },
            { id: 'scars', text: 'scars' },
            { id: 'glow', text: 'glow' }
          ]
        },
        {
          id: 'surface borks',
          text: 'surface borks',
          kind: 'and-commas-adv',
          options: [
            { id: 'fetchings', text: 'fetchings' },
            { id: 'fscars', text: 'fscars' },
            { id: 'fglow', text: 'fglow' }
          ]
        },
        {
          id: 'stance',
          text: { singular: 'stance', plural: 'stances' },
          kind: 'and-commas-adv',
          options: [
            { id: 'lunging', text: 'lunging' },
            { id: 'roaring', text: 'roaring' },
            { id: 'three-quarter', text: 'three-quarter' }
          ]
        },
        {
          id: 'render style',
          text: 'render style',
          kind: 'and-spaces-adj',
          options: [
            { id: 'cinematic', text: 'cinematic' },
            { id: 'hyperdetailed', text: 'hyperdetailed' },
            { id: 'volumetric', text: 'volumetric' },
            { id: 'green tinted', text: 'green tinted' },
            { id: 'black and white', text: 'black and white' }
          ]
        },
        {
          id: 'finish profile',
          text: 'finish profile',
          kind: 'and-spaces-adj',
          customText: { singular: 'finish', plural: 'finishes' },
          options: [
            { id: 'matte', text: 'matte' },
            { id: 'pearlescent', text: 'pearlescent' }
          ]
        }
      ]
    },
    {
      id: 'accent',
      text: { singular: 'accent', plural: 'accents' },
      controls: [
        {
          id: 'accent',
          text: 'accent',
          kind: 'and-commas-adv',
          options: [
            { id: 'striped', text: 'striped' }
          ]
        }
      ]
    },
    {
      id: 'colorize',
      text: 'colorize',
      controls: [
        {
          id: 'colorize',
          text: 'colorize',
          kind: 'global-selector',
          options: [
            { id: 'green', text: 'green' },
            { id: 'black', text: 'black' }
          ]
        }
      ]
    },
    {
      id: 'modes',
      text: 'modes',
      controls: [
        {
          id: 'is portrait',
          text: 'is portrait',
          kind: 'toggle',
          options: [{ id: 'portrait', text: 'portrait' }]
        },
        {
          id: 'thorax mode',
          text: 'thorax mode',
          kind: 'toggle',
          globalSubstitutions: [
            {
              from: 'torso',
              to: 'thorax',
              fromPlural: 'torsos',
              toPlural: 'thoraces'
            }
          ],
          options: [{ id: 'replace torso terminology', text: 'replace torso terminology' }]
        },
        {
          id: 'camera angle',
          text: 'camera angle',
          kind: 'or',
          disabledBys: [{ controlId: 'is portrait' }],
          options: [
            { id: 'low', text: 'low' },
            { id: 'overhead', text: 'overhead' },
            { id: 'dutch', text: 'dutch' }
          ]
        },
        {
          id: 'portrait focus',
          text: 'portrait focus',
          kind: 'and-commas',
          hiddenBys: [{ controlId: 'is portrait' }],
          options: [
            { id: 'face', text: 'face' },
            { id: 'torso', text: 'torso' },
            { id: 'torso side profile', text: 'torso side profile' },
            { id: 'torsos', text: 'torsos' }
          ]
        },
        {
          id: 'pose',
          text: 'pose',
          kind: 'or',
          options: [
            { id: 'grounded', text: 'grounded' },
            { id: 'floating', text: 'floating', disabledBys: [{ controlId: 'is portrait' }] },
            { id: 'airborne', text: 'airborne', hiddenBys: [{ controlId: 'is portrait' }] }
          ]
        },
        {
          id: 'portrait pose',
          text: 'portrait pose',
          kind: 'or',
          revealedBys: [{ controlId: 'is portrait' }],
          options: [
            { id: 'close crop', text: 'close crop', revealedBys: [{ controlId: 'is portrait' }] },
            { id: 'tight profile', text: 'tight profile' }
          ]
        }
      ]
    },
    {
      id: 'torso references',
      text: 'torso references',
      controls: [
        {
          id: 'torso mentions',
          text: 'torso mentions',
          kind: 'and-commas',
          options: [
            { id: 'torso badge', text: 'torso badge' },
            { id: 'torsos', text: 'torsos' }
          ]
        }
      ]
    },
    {
      id: 'portrait extras',
      text: 'portrait extras',
      revealedBys: [{ controlId: 'is portrait' }],
      controls: [
        {
          id: 'portrait lighting',
          text: 'portrait lighting',
          kind: 'or-adj',
          options: [
            { id: 'rim-lit', text: 'rim-lit' },
            { id: 'soft-lit', text: 'soft-lit' }
          ]
        }
      ]
    },
    {
      id: 'section disabled target',
      text: 'section disabled target',
      disabledBys: [{ controlId: 'is portrait' }],
      controls: [
        {
          id: 'section disabled sample',
          text: 'section disabled sample',
          kind: 'and-commas',
          options: [
            { id: 'locked out while portrait', text: 'locked out while portrait' }
          ]
        }
      ]
    },
    {
      id: 'section hidden target',
      text: 'section hidden target',
      hiddenBys: [{ controlId: 'is portrait' }],
      controls: [
        {
          id: 'section hidden sample',
          text: 'section hidden sample',
          kind: 'and-commas',
          options: [
            { id: 'gone while portrait', text: 'gone while portrait' }
          ]
        }
      ]
    },
    {
      id: 'negative modes',
      text: 'negative modes',
      promptTarget: 'negative',
      controls: [
        {
          id: 'negative-switch',
          text: 'negative-switch',
          kind: 'toggle',
          initiallySelectedOptions: true,
          options: [{ id: 'no clutter', text: 'no clutter' }]
        }
      ]
    },
    {
      id: 'negative polish',
      text: 'negative polish',
      promptTarget: 'negative',
      controls: [
        {
          id: 'neg-quality',
          text: 'neg-quality',
          kind: 'and-commas',
          initiallySelectedOptions: ['blurry'],
          options: [
            { id: 'blurry', text: 'blurry' },
            { id: 'muddy', text: 'muddy' },
            { id: 'extra limbs', text: 'extra limbs' }
          ]
        },
        {
          id: 'neg-temperature-opposite',
          text: 'neg-temperature-opposite',
          kind: 'hidden-opposite',
          hiddenOppositeBys: [{ optionId: 'hot' }],
          initiallySelectedOptions: ['cold-negative'],
          options: [
            { id: 'cold-negative', text: 'cold' }
          ]
        }
      ]
    }
  ]
};
