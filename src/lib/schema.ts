import type { Schema } from '../types';

export const schema: Schema = {
  sections: [
    {
      id: 'or types',
      text: 'or types',
      controls: [
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
          id: 'climbing',
          text: 'climbing',
          kind: 'or-adv',
          options: [
            { id: 'funnily', text: 'funnily' },
            { id: 'weirdly', text: 'weirdly' },
            { id: 'happily', text: 'happily' }
          ]
        },
        {
          id: 'armor',
          text: 'armor',
          kind: 'or-adj',
          options: [
            { id: 'chrome', text: 'chrome' },
            { id: 'obsidian', text: 'obsidian' },
            { id: 'bone', text: 'bone' }
          ]
        }
      ]
    },
    {
      id: 'and types',
      text: 'and types',
      controls: [
        {
          id: 'reading',
          text: 'reading',
          kind: 'and-commas-adv',
          options: [
            { id: 'books', text: 'books' },
            { id: 'magazines', text: 'magazines' },
            { id: 'blogs', text: 'blogs' }
          ]
        },
        {
          id: 'kicking',
          text: 'kicking',
          kind: 'and-commas-adv',
          options: [
            { id: 'the bucket', text: 'the bucket' },
            {
              id: 'redacted',
              text: 'redacted',
              submenu: {
                kind: 'or-adj',
                options: [
                  { id: 'big', text: 'big' },
                  { id: 'small', text: 'small' }
                ]
              }
            },
            { 
              id: 'pigeons',
              text: 'pigeons', 
              submenu: {
                kind: 'or-adv',
                options: [
                  { id: 'in the park', text: 'in the park' },
                  { id: 'with a vengeance', text: 'with a vengeance' }
                ]
              }
            },
          ]
        },
        {
          id: 'render',
          text: 'render',
          kind: 'and-spaces-adj',
          customText: 'rendering',
          options: [
            { id: 'cinematic', text: 'cinematic' },
            { id: 'hyperdetailed', text: 'hyperdetailed' },
            { id: 'volumetric', text: 'volumetric' }
          ]
        }
      ]
    },
    {
      id: 'negative prompt',
      text: 'negative prompt',
      promptTarget: 'negative',
      controls: [
        {
          id: 'stay safe',
          text: 'stay safe',
          kind: 'required',
          initiallySelectedOptions: ['space robo dino demon monster'],
          options: [{ id: 'space robo dino demon monster', text: 'space robo dino demon monster' }],
        },
        {
          id: 'wakka',
          text: 'wakka',
          kind: 'toggle',
          initiallySelectedOptions: true,
          options: [{ id: 'no clutter', text: 'no clutter' }]
        },
        {
          id: 'camera angle',
          text: 'camera angle',
          kind: 'and-commas',
          disabledBys: [{ controlId: 'wakka' }],
          options: [
            { id: 'low', text: 'low' },
            { id: 'overhead', text: 'overhead' },
            { id: 'dutch', text: 'dutch' }
          ]
        }
      ]
    }
  ]
};
