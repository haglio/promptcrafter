import type { Schema } from './types';

export const schema: Schema = {
  sections: [
    {
      id: 'subject-core',
      defaultWeight: 1,
      promptTarget: 'positive',
      controls: [
        {
          id: 'subject-base',
          kind: 'required',
          options: [{ id: 'space robo dino demon monster', defaultSelected: true }],
        },
        {
          id: 'count',
          kind: 'or-no-comma-prefix-of-next',
          options: [
            { id: 'one' },
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
          kind: 'or-leading-title-if-non-empty',
          titleText: 'silhouette',
          options: [
            { id: 'towering' },
            { id: 'lanky' },
            { id: 'hulking' }
          ]
        },
        {
          id: 'element prefix',
          kind: 'or-no-comma-prefix-of-next',
          options: [
            { id: 'void' },
            { id: 'plasma' },
            { id: 'nebula' }
          ]
        },
        {
          id: 'armor',
          titleText: 'armor',
          kind: 'or-trailing-title-if-non-empty',
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
      defaultWeight: 1,
      promptTarget: 'positive',
      controls: [
        {
          id: 'appendages',
          kind: 'and-comma-separated',
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
                selectionMode: 'one',
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
          kind: 'and-comma-leading-text',
          leadingText: 'sitting on', 
          options: [
            { id: 'etchings' },
            { id: 'scars' },
            { id: 'glow' }
          ]
        },
        {
          id: 'surface borks',
          kind: 'and-comma-leading-text',
          options: [
            { id: 'fetchings' },
            { id: 'fscars' },
            { id: 'fglow' }
          ]
        },
        {
          id: 'stance',
          kind: 'and-space-separated',
          options: [
            { id: 'lunging' },
            { id: 'roaring' },
            { id: 'three-quarter' }
          ]
        },
        {
          id: 'render style',
          kind: 'and-space-trailing-title-if-non-empty',
          titleText: 'render',
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
      defaultWeight: 1,
      promptTarget: 'positive',
      controls: [
        {
          id: 'is portrait',
          kind: 'toggle',
          defaultToggleOn: false,
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
          kind: 'and-comma-separated',
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
      defaultWeight: 1,
      promptTarget: 'negative',
      controls: [
        {
          id: 'negative-switch',
          kind: 'toggle',
          defaultToggleOn: true,
          options: [{ id: 'no clutter' }]
        }
      ]
    },
    {
      id: 'negative polish',
      defaultWeight: 1,
      promptTarget: 'negative',
      controls: [
        {
          id: 'neg-quality',
          kind: 'and-comma-separated',
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