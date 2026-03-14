import type { Schema } from '../types';

export const schema: Schema = {
  sections: [
    {
      id: 'or types',
      controls: [
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
          id: 'climbing',
          kind: 'or-adv',
          options: [
            { id: 'funnily' },
            { id: 'weirdly' },
            { id: 'happily' }
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
      id: 'and types',
      controls: [
        {
          id: 'reading',
          kind: 'and-commas-adv',
          options: [
            { id: 'books' },
            { id: 'magazines' },
            { id: 'blogs' }
          ]
        },
        {
          id: 'kicking',
          kind: 'and-commas-adv',
          options: [
            { id: 'the bucket' },
            {
              id: 'redacted',
              submenu: {
                options: [
                  { id: 'big' },
                  { id: 'small' }
                ]
              }
            },
            { 
              id: 'pigeons', 
              submenu: {
                kind: 'or',
                placement: 'after',
                options: [
                  { id: 'in the park' },
                  { id: 'with a vengeance' }
                ]
              }
            },
          ]
        },
        {
          id: 'render',
          kind: 'and-spaces-adj',
          customText: 'rendering',
          options: [
            { id: 'cinematic' },
            { id: 'hyperdetailed' },
            { id: 'volumetric' }
          ]
        }
      ]
    },
    {
      id: 'negative prompt',
      promptTarget: 'negative',
      controls: [
        {
          id: 'stay safe',
          kind: 'required',
          options: [{ id: 'space robo dino demon monster', beginOn: true }],
        },
        {
          id: 'wakka',
          kind: 'toggle',
          beginOn: true,
          options: [{ id: 'no clutter' }]
        },
        {
          id: 'camera angle',
          kind: 'and-commas',
          disables: [{ type: 'toggle-on', controlId: 'wakka' }],
          options: [
            { id: 'low' },
            { id: 'overhead' },
            { id: 'dutch' }
          ]
        }
      ]
    }
  ]
};
