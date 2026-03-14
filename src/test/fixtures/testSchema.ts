import type { Schema } from "../../types";

export const testSchema: Schema = {
  sections: [
    {
      id: 'subject-core',
      promptTarget: 'positive',
      controls: [
        {
          id: 'subject-base',
          kind: 'required',
          options: [{ id: 'space robo dino demon monster', beginOn: true }],
        },
        {
          id: 'count',
          kind: 'or-prefix',
          options: [
            { id: 'or' },
            { 
              id: 'two', 
              submenu: {
                placement: 'after',
                options: [
                  { id: 'different' },
                ]
              }
            }
          ]
        },
        {
          id: 'alignment',
          kind: 'or',
          options: [
            { id: 'hero', plural: 'heroes' },
            { id: 'villain', plural: 'villains' }
          ]
        },
        {
          id: 'silhouette',
          kind: 'or-adv',
          customText: 'outline',
          options: [
            { id: 'towering' },
            { id: 'lanky' },
            { id: 'hulking' }
          ]
        },
        {
          id: 'element prefix',
          kind: 'or-prefix',
          options: [
            { id: 'void' },
            { id: 'plasma' },
            { id: 'nebula' }
          ]
        },
        {
          id: 'armor',
          kind: 'or-adj',
          options: [
            { id: 'chrome' },
            { id: 'obsidian' },
            { id: 'bone' }
          ]
        }
      ]
    },
    {
      id: 'details',
      promptTarget: 'positive',
      controls: [
        {
          id: 'appendages',
          kind: 'and-commas',
          options: [
            {
              id: 'wings',
              submenu: {
                options: [
                  { id: 'feathered' },
                  { id: 'mechanical' }
                ]
              }
            },
            { 
              id: 'horns', 
              submenu: {
                kind: 'or',
                placement: 'after',
                options: [
                  { id: 'wishily' },
                  { id: 'washily' }
                ]
              }
            },
            { id: 'tail' }
          ]
        },
        {
          id: 'sitting on',
          kind: 'and-commas-adv',
          customText: 'alighting upon', 
          options: [
            { id: 'etchings' },
            { id: 'scars' },
            { id: 'glow' }
          ]
        },
        {
          id: 'surface borks',
          kind: 'and-commas-adv',
          options: [
            { id: 'fetchings' },
            { id: 'fscars' },
            { id: 'fglow' }
          ]
        },
        {
          id: 'stance',
          kind: 'and-commas-adv',
          options: [
            { id: 'lunging' },
            { id: 'roaring' },
            { id: 'three-quarter' }
          ]
        },
        {
          id: 'render style',
          kind: 'and-spaces-adj',
          options: [
            { id: 'cinematic' },
            { id: 'hyperdetailed' },
            { id: 'volumetric' }
          ]
        }
      ]
    },
    {
      id: 'modes',
      promptTarget: 'positive',
      controls: [
        {
          id: 'is portrait',
          kind: 'toggle',
          beginOn: false,
          options: [{ id: 'portrait' }]
        },
        {
          id: 'camera angle',
          kind: 'or',
          disables: [{ type: 'toggle-on', controlId: 'is portrait' }],
          options: [
            { id: 'low' },
            { id: 'overhead' },
            { id: 'dutch' }
          ]
        },
        {
          id: 'portrait focus',
          kind: 'and-commas',
          hides: [{ type: 'toggle-on', controlId: 'is portrait' }],
          options: [
            { id: 'face' },
            { id: 'torso' }
          ]
        }
      ]
    },
    {
      id: 'negative modes',
      promptTarget: 'negative',
      controls: [
        {
          id: 'negative-switch',
          kind: 'toggle',
          beginOn: true,
          options: [{ id: 'no clutter' }]
        }
      ]
    },
    {
      id: 'negative polish',
      promptTarget: 'negative',
      controls: [
        {
          id: 'neg-quality',
          kind: 'and-commas',
          options: [
            { id: 'blurry' },
            { id: 'muddy' },
            { id: 'extra limbs' }
          ]
        }
      ]
    }
  ]
};