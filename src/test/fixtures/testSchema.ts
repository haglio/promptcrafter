import type { Schema } from "../../types";

export const testSchema: Schema = {
  sections: [
    {
      text: 'subject-core',
      controls: [
        {
          text: 'subject-base',
          kind: 'required',
          initiallySelectedOptions: ['space robo dino demon monster'],
          options: [{ text: 'space robo dino demon monster' }],
        },
        {
          text: 'count',
          kind: 'or-prefix',
          options: [
            { text: 'or' },
            { 
              text: 'two', 
              submenu: {
                kind: 'and-adv',
                options: [
                  { text: 'different' },
                ]
              }
            }
          ]
        },
        {
          text: 'alignment',
          kind: 'or',
          options: [
            { text: 'hero', pluralText: 'heroes' },
            { text: 'villain', pluralText: 'villains' }
          ]
        },
        {
          text: 'silhouette',
          kind: 'or-adv',
          customText: 'outline',
          options: [
            { text: 'towering' },
            { text: 'lanky' },
            { text: 'hulking' }
          ]
        },
        {
          text: 'movement',
          kind: 'or-adv',
          options: [
            { text: 'swiftly' },
            { text: 'heavily' }
          ]
        },
        {
          text: 'element prefix',
          kind: 'or-prefix',
          options: [
            { text: 'void' },
            { text: 'plasma' },
            { text: 'nebula' }
          ]
        },
        {
          text: 'armor',
          kind: 'or-adj',
          options: [
            { text: 'chrome' },
            { text: 'obsidian' },
            { text: 'bone' }
          ]
        },
        {
          text: 'surface treatment',
          kind: 'or-adj',
          customText: 'plating',
          options: [
            { text: 'runed' },
            { text: 'etched' }
          ]
        }
      ]
    },
    {
      text: 'details',
      controls: [
        {
          text: 'appendages',
          kind: 'and-commas',
          options: [
            {
              text: 'wings',
              submenu: {
                kind: 'or-adj',
                options: [
                  { text: 'feathered' },
                  { text: 'mechanical' }
                ]
              }
            },
            { 
              text: 'horns', 
              submenu: {
                kind: 'or-adv',
                options: [
                  { text: 'wishily' },
                  { text: 'washily' }
                ]
              }
            },
            {
              text: 'tail',
              submenu: {
                kind: 'and-adj',
                options: [
                  { text: 'barbed' },
                  { text: 'segmented' }
                ]
              }
            },
            {
              text: 'antennae',
              submenu: {
                kind: 'and-adv',
                options: [
                  { text: 'arched' },
                  { text: 'flared' }
                ]
              }
            }
          ]
        },
        {
          text: 'sitting on',
          kind: 'and-commas-adv',
          customText: 'alighting upon', 
          options: [
            { text: 'etchings' },
            { text: 'scars' },
            { text: 'glow' }
          ]
        },
        {
          text: 'surface borks',
          kind: 'and-commas-adv',
          options: [
            { text: 'fetchings' },
            { text: 'fscars' },
            { text: 'fglow' }
          ]
        },
        {
          text: 'stance',
          kind: 'and-commas-adv',
          pluralText: 'stances',
          options: [
            { text: 'lunging' },
            { text: 'roaring' },
            { text: 'three-quarter' }
          ]
        },
        {
          text: 'render style',
          kind: 'and-spaces-adj',
          options: [
            { text: 'cinematic' },
            { text: 'hyperdetailed' },
            { text: 'volumetric' }
          ]
        },
        {
          text: 'finish profile',
          kind: 'and-spaces-adj',
          customText: 'finish',
          customPluralText: 'finishes',
          options: [
            { text: 'matte' },
            { text: 'pearlescent' }
          ]
        }
      ]
    },
    {
      text: 'accent',
      pluralText: 'accents',
      controls: [
        {
          text: 'accent',
          kind: 'and-commas-adv',
          options: [
            { text: 'striped' }
          ]
        }
      ]
    },
    {
      text: 'modes',
      controls: [
        {
          text: 'is portrait',
          kind: 'toggle',
          options: [{ text: 'portrait' }]
        },
        {
          text: 'camera angle',
          kind: 'or',
          disabledBys: [{ controlText: 'is portrait' }],
          options: [
            { text: 'low' },
            { text: 'overhead' },
            { text: 'dutch' }
          ]
        },
        {
          text: 'portrait focus',
          kind: 'and-commas',
          hiddenBys: [{ controlText: 'is portrait' }],
          options: [
            { text: 'face' },
            { text: 'torso' }
          ]
        },
        {
          text: 'pose',
          kind: 'or',
          options: [
            { text: 'grounded' },
            { text: 'floating', disabledBys: [{ controlText: 'is portrait' }] },
            { text: 'airborne', hiddenBys: [{ controlText: 'is portrait' }] }
          ]
        }
      ]
    },
    {
      text: 'section disabled target',
      disabledBys: [{ controlText: 'is portrait' }],
      controls: [
        {
          text: 'section disabled sample',
          kind: 'and-commas',
          options: [
            { text: 'locked out while portrait' }
          ]
        }
      ]
    },
    {
      text: 'section hidden target',
      hiddenBys: [{ controlText: 'is portrait' }],
      controls: [
        {
          text: 'section hidden sample',
          kind: 'and-commas',
          options: [
            { text: 'gone while portrait' }
          ]
        }
      ]
    },
    {
      text: 'negative modes',
      promptTarget: 'negative',
      controls: [
        {
          text: 'negative-switch',
          kind: 'toggle',
          initiallySelectedOptions: true,
          options: [{ text: 'no clutter' }]
        }
      ]
    },
    {
      text: 'negative polish',
      promptTarget: 'negative',
      controls: [
        {
          text: 'neg-quality',
          kind: 'and-commas',
          initiallySelectedOptions: ['blurry'],
          options: [
            { text: 'blurry' },
            { text: 'muddy' },
            { text: 'extra limbs' }
          ]
        }
      ]
    }
  ]
};