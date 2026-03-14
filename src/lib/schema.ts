import type { Schema } from '../types';

export const schema: Schema = {
  sections: [
    {
      text: 'or types',
      controls: [
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
          text: 'climbing',
          kind: 'or-adv',
          options: [
            { text: 'funnily' },
            { text: 'weirdly' },
            { text: 'happily' }
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
        }
      ]
    },
    {
      text: 'and types',
      controls: [
        {
          text: 'reading',
          kind: 'and-commas-adv',
          options: [
            { text: 'books' },
            { text: 'magazines' },
            { text: 'blogs' }
          ]
        },
        {
          text: 'kicking',
          kind: 'and-commas-adv',
          options: [
            { text: 'the bucket' },
            {
              text: 'redacted',
              submenu: {
                kind: 'or-adj',
                options: [
                  { text: 'big' },
                  { text: 'small' }
                ]
              }
            },
            { 
              text: 'pigeons', 
              submenu: {
                kind: 'or-adv',
                options: [
                  { text: 'in the park' },
                  { text: 'with a vengeance' }
                ]
              }
            },
          ]
        },
        {
          text: 'render',
          kind: 'and-spaces-adj',
          customText: 'rendering',
          options: [
            { text: 'cinematic' },
            { text: 'hyperdetailed' },
            { text: 'volumetric' }
          ]
        }
      ]
    },
    {
      text: 'negative prompt',
      promptTarget: 'negative',
      controls: [
        {
          text: 'stay safe',
          kind: 'required',
          options: [{ text: 'space robo dino demon monster', initiallySelected: true }],
        },
        {
          text: 'wakka',
          kind: 'toggle',
          initiallySelected: true,
          options: [{ text: 'no clutter' }]
        },
        {
          text: 'camera angle',
          kind: 'and-commas',
          disabledBys: [{ controlText: 'wakka' }],
          options: [
            { text: 'low' },
            { text: 'overhead' },
            { text: 'dutch' }
          ]
        }
      ]
    }
  ]
};
