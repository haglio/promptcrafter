import { promises as fs } from 'node:fs';
import path from 'node:path';
import process from 'node:process';
import { fileURLToPath } from 'node:url';

const CONTROL_KINDS = new Set([
  'or',
  'or-adv',
  'or-adj',
  'or-prefix',
  'and-commas',
  'and-commas-adj',
  'and-commas-adv',
  'and-spaces-adj',
  'required',
  'hidden-opposite',
  'toggle',
  'global-selector',
]);

const RADIO_CONTROL_KINDS = new Set(['or', 'or-adv', 'or-adj', 'or-prefix']);
const MULTISELECT_CONTROL_KINDS = new Set([
  'and-commas',
  'and-commas-adj',
  'and-commas-adv',
  'and-spaces-adj',
  'required',
  'hidden-opposite',
]);
const SUBMENU_DISCRIMINANTS = new Set(['or', 'and']);

const UNCOUNTABLE_WORDS = new Set([
  'advice',
  'air',
  'armor',
  'art',
  'black',
  'blood',
  'blue',
  'bronze',
  'chrome',
  'clothing',
  'clutter',
  'code',
  'copper',
  'darkness',
  'data',
  'equipment',
  'furniture',
  'gold',
  'gray',
  'green',
  'hair',
  'heat',
  'homework',
  'information',
  'iron',
  'knowledge',
  'light',
  'lightning',
  'love',
  'magic',
  'mist',
  'money',
  'music',
  'obsidian',
  'plasma',
  'rain',
  'red',
  'research',
  'sand',
  'silver',
  'smoky',
  'snow',
  'space',
  'steam',
  'stone',
  'traffic',
  'violence',
  'water',
  'weather',
  'white',
  'wood',
]);

const IRREGULAR_PLURALS = new Map([
  ['appendix', 'appendices'],
  ['child', 'children'],
  ['foot', 'feet'],
  ['goose', 'geese'],
  ['hero', 'heroes'],
  ['knife', 'knives'],
  ['leaf', 'leaves'],
  ['life', 'lives'],
  ['loaf', 'loaves'],
  ['man', 'men'],
  ['mouse', 'mice'],
  ['person', 'people'],
  ['scarf', 'scarves'],
  ['self', 'selves'],
  ['shelf', 'shelves'],
  ['thief', 'thieves'],
  ['tooth', 'teeth'],
  ['torso', 'torsos'],
  ['wife', 'wives'],
  ['wolf', 'wolves'],
  ['woman', 'women'],
]);

const ADJECTIVE_OR_ADVERB_SUFFIXES = [
  'ed',
  'ic',
  'ical',
  'ing',
  'ish',
  'ive',
  'less',
  'like',
  'ly',
  'ous',
  'ward',
  'wise',
];

const CSV_COLUMNS = {
  section: 0,
  promptTarget: 1,
  controlKind: 2,
  revealedBy: 3,
  customText: 4,
  supplementedBy: 5,
  globalSubstitutions: 6,
  allOptionsInitiallySelected: 7,
  controlId: 8,
  firstOption: 9,
};

function createDiagnostic(level, message, row, column) {
  return { level, message, row, column };
}

function pushError(diagnostics, message, row, column) {
  diagnostics.push(createDiagnostic('error', message, row, column));
}

function pushWarning(diagnostics, message, row, column) {
  diagnostics.push(createDiagnostic('warning', message, row, column));
}

function locationLabel(row, column) {
  if (!row) return 'file';
  if (!column) return `row ${row}`;
  return `row ${row}, column ${column}`;
}

function normalizeLookupKey(value) {
  return value.trim().replace(/\s+/g, ' ').toLowerCase();
}

function isRowEmpty(row) {
  return row.every((cell) => !cell.trim());
}

function getCell(row, index) {
  return (row[index] ?? '').trim();
}

function parseCsv(input) {
  const rows = [];
  let row = [];
  let cell = '';
  let inQuotes = false;

  for (let index = 0; index < input.length; index += 1) {
    const current = input[index];
    const next = input[index + 1];

    if (current === '"') {
      if (inQuotes && next === '"') {
        cell += '"';
        index += 1;
        continue;
      }

      inQuotes = !inQuotes;
      continue;
    }

    if (!inQuotes && current === ',') {
      row.push(cell);
      cell = '';
      continue;
    }

    if (!inQuotes && (current === '\n' || current === '\r')) {
      if (current === '\r' && next === '\n') {
        index += 1;
      }

      row.push(cell);
      rows.push(row);
      row = [];
      cell = '';
      continue;
    }

    cell += current;
  }

  if (inQuotes) {
    throw new Error('CSV ended while still inside a quoted value.');
  }

  if (cell.length > 0 || row.length > 0) {
    row.push(cell);
    rows.push(row);
  }

  return rows;
}

function splitOnSemicolons(raw) {
  return raw
    .split(';')
    .map((part) => part.trim())
    .filter(Boolean);
}

function splitOnOr(raw) {
  return raw
    .split(/\s+OR\s+/i)
    .map((part) => part.trim())
    .filter(Boolean);
}

function splitSubmenuOptions(raw) {
  return raw
    .split(',')
    .map((part) => part.trim())
    .filter(Boolean);
}

function parseBooleanCell(raw, diagnostics, rowNumber, columnNumber) {
  if (!raw) return false;
  if (/^true$/i.test(raw)) return true;
  if (/^false$/i.test(raw)) return false;

  pushError(
    diagnostics,
    `Expected TRUE, FALSE, or an empty cell but received "${raw}".`,
    rowNumber,
    columnNumber,
  );
  return false;
}

function containsReferenceSyntax(value) {
  return value.includes('[') || value.includes(']');
}

function parseTextTemplate(raw, diagnostics, rowNumber, columnNumber, fieldName) {
  const trimmed = raw.trim();
  const tokens = [];
  let cursor = 0;

  while (cursor < trimmed.length) {
    const openIndex = trimmed.indexOf('[', cursor);
    if (openIndex === -1) {
      const tail = trimmed.slice(cursor);
      if (tail) tokens.push({ kind: 'text', value: tail });
      break;
    }

    const head = trimmed.slice(cursor, openIndex);
    if (head) tokens.push({ kind: 'text', value: head });

    const closeIndex = trimmed.indexOf(']', openIndex + 1);
    if (closeIndex === -1) {
      pushError(diagnostics, `Unclosed "[" in ${fieldName}.`, rowNumber, columnNumber);
      return {
        raw: trimmed,
        tokens: [{ kind: 'text', value: trimmed }],
      };
    }

    const reference = trimmed.slice(openIndex + 1, closeIndex).trim();
    if (!reference) {
      pushError(diagnostics, `Empty "[]" reference in ${fieldName}.`, rowNumber, columnNumber);
    } else {
      tokens.push({ kind: 'ref', query: reference });
    }

    cursor = closeIndex + 1;
  }

  if (trimmed.includes(']') && !trimmed.includes('[')) {
    pushError(
      diagnostics,
      `Found "]" without a matching "[" in ${fieldName}.`,
      rowNumber,
      columnNumber,
    );
  }

  return {
    raw: trimmed,
    tokens,
  };
}

function parseReferenceQuery(rawQuery) {
  const trimmed = rawQuery.trim();
  const selectorMatch = /^(section|control|option)\s*:\s*(.+)$/i.exec(trimmed);
  if (selectorMatch) {
    return {
      selector: selectorMatch[1].toLowerCase(),
      query: selectorMatch[2].trim(),
    };
  }

  return {
    selector: null,
    query: trimmed,
  };
}

function buildOptionDraft(labelRaw, submenuRaw, side, diagnostics, rowNumber, columnNumber) {
  const labelTemplate = parseTextTemplate(
    labelRaw,
    diagnostics,
    rowNumber,
    columnNumber,
    'option text',
  );

  const draft = {
    kind: 'option',
    rowNumber,
    columnNumber,
    rawLabel: labelRaw.trim(),
    labelTemplate,
    text: null,
    id: null,
    aliases: labelRaw.trim() ? [labelRaw.trim()] : [],
    submenu: undefined,
  };

  if (!submenuRaw) {
    return draft;
  }

  const submenuMatch = /^(or|and)\s*:\s*(.+)$/i.exec(submenuRaw.trim());
  const submenuDiscriminant = submenuMatch ? submenuMatch[1].toLowerCase() : 'and';
  const submenuOptionsRaw = submenuMatch ? submenuMatch[2] : submenuRaw;

  if (!SUBMENU_DISCRIMINANTS.has(submenuDiscriminant)) {
    pushError(
      diagnostics,
      `Unsupported submenu prefix "${submenuDiscriminant}". Use "or:" or "and:" when you need to override the default.`,
      rowNumber,
      columnNumber,
    );
    return draft;
  }

  const submenuOptions = splitSubmenuOptions(submenuOptionsRaw).map((optionText, index) => ({
    kind: 'submenu-option',
    rowNumber,
    columnNumber,
    rawLabel: optionText,
    labelTemplate: parseTextTemplate(
      optionText,
      diagnostics,
      rowNumber,
      columnNumber,
      `submenu option ${index + 1}`,
    ),
    text: null,
    id: null,
    aliases: optionText.trim() ? [optionText.trim()] : [],
  }));

  if (submenuOptions.length === 0) {
    pushError(
      diagnostics,
      `Option "${labelRaw.trim()}" declares a submenu but does not contain any submenu options.`,
      rowNumber,
      columnNumber,
    );
    return draft;
  }

  draft.submenu = {
    kind: `${submenuDiscriminant}-${side}`,
    options: submenuOptions,
  };

  return draft;
}

function parseOptionCell(raw, diagnostics, rowNumber, columnNumber) {
  const trimmed = raw.trim();
  if (!trimmed) return null;

  const beforeMatch = /^\((.+)\)\s+(.+)$/.exec(trimmed);
  const afterMatch = /^(.+?)\s+\((.+)\)$/.exec(trimmed);

  if (beforeMatch && afterMatch) {
    pushError(
      diagnostics,
      `Option "${trimmed}" looks like it has both leading and trailing submenu syntax.`,
      rowNumber,
      columnNumber,
    );
    return null;
  }

  if (beforeMatch) {
    return buildOptionDraft(
      beforeMatch[2],
      beforeMatch[1],
      'adj',
      diagnostics,
      rowNumber,
      columnNumber,
    );
  }

  if (afterMatch) {
    return buildOptionDraft(
      afterMatch[1],
      afterMatch[2],
      'adv',
      diagnostics,
      rowNumber,
      columnNumber,
    );
  }

  if (trimmed.includes('(') || trimmed.includes(')')) {
    pushError(
      diagnostics,
      `Option "${trimmed}" has parentheses, but not in a supported "(submenu) option" or "option (submenu)" form.`,
      rowNumber,
      columnNumber,
    );
    return null;
  }

  return buildOptionDraft(trimmed, '', null, diagnostics, rowNumber, columnNumber);
}

function preserveCase(sample, replacement) {
  if (!sample) return replacement;
  if (sample.toUpperCase() === sample) return replacement.toUpperCase();
  if (sample[0] === sample[0].toUpperCase() && sample.slice(1) === sample.slice(1).toLowerCase()) {
    return replacement[0].toUpperCase() + replacement.slice(1);
  }
  return replacement;
}

function pluralizeWord(word) {
  const lower = word.toLowerCase();

  if (!/[a-z]/i.test(word)) return word;
  if (UNCOUNTABLE_WORDS.has(lower)) return word;

  const irregular = IRREGULAR_PLURALS.get(lower);
  if (irregular) return preserveCase(word, irregular);

  if (/[^s]s$/i.test(word)) return word;

  if (
    lower.endsWith('ly') ||
    ADJECTIVE_OR_ADVERB_SUFFIXES.some((suffix) => lower.endsWith(suffix) && lower.length > suffix.length + 1)
  ) {
    return word;
  }

  if (/(s|x|z|ch|sh)$/i.test(word)) return `${word}es`;
  if (/[^aeiou]y$/i.test(word)) return `${word.slice(0, -1)}ies`;
  if (/(?:fe)$/i.test(word)) return `${word.slice(0, -2)}ves`;
  if (/([lr])f$/i.test(word)) return `${word.slice(0, -1)}ves`;
  if (/is$/i.test(word)) return `${word.slice(0, -2)}es`;
  return `${word}s`;
}

function derivePluralPhrase(text) {
  const trimmed = text.trim();
  if (!trimmed) return trimmed;

  const match = /([A-Za-z][A-Za-z'-]*)\s*$/.exec(trimmed);
  if (!match) return trimmed;

  const word = match[1];
  const plural = pluralizeWord(word);
  if (plural === word) return trimmed;

  return `${trimmed.slice(0, match.index)}${plural}`;
}

function createLiteralTextValue(raw) {
  const singular = raw.trim().replace(/\s+/g, ' ');
  return {
    singular,
    plural: derivePluralPhrase(singular),
  };
}

function templateHasReferences(template) {
  return template.tokens.some((token) => token.kind === 'ref');
}

function normalizeTemplateParts(parts) {
  const merged = [];

  for (const part of parts) {
    if (typeof part !== 'string') {
      merged.push(part);
      continue;
    }

    const normalized = part.replace(/\s+/g, ' ');
    if (!normalized) continue;

    const previous = merged[merged.length - 1];
    if (typeof previous === 'string') {
      merged[merged.length - 1] = `${previous}${normalized}`;
    } else {
      merged.push(normalized);
    }
  }

  while (typeof merged[0] === 'string' && !merged[0].trim()) {
    merged.shift();
  }

  while (typeof merged[merged.length - 1] === 'string' && !merged[merged.length - 1].trim()) {
    merged.pop();
  }

  if (typeof merged[0] === 'string') {
    merged[0] = merged[0].trimStart();
  }

  if (typeof merged[merged.length - 1] === 'string') {
    merged[merged.length - 1] = merged[merged.length - 1].trimEnd();
  }

  return merged.filter((part) => (typeof part === 'string' ? part.length > 0 : true));
}

function pluralizeTemplateParts(parts) {
  const cloned = parts.map((part) =>
    typeof part === 'string'
      ? part
      : {
          ref: { ...part.ref },
        },
  );

  for (let index = cloned.length - 1; index >= 0; index -= 1) {
    const current = cloned[index];
    if (typeof current !== 'string') continue;

    const pluralized = derivePluralPhrase(current);
    if (pluralized !== current) {
      cloned[index] = pluralized;
      break;
    }
  }

  return normalizeTemplateParts(cloned);
}

function buildTextValue(template, indexes, diagnostics, rowNumber, columnNumber) {
  if (!templateHasReferences(template)) {
    return createLiteralTextValue(template.raw);
  }

  const singularParts = [];
  for (const token of template.tokens) {
    if (token.kind === 'text') {
      singularParts.push(token.value);
      continue;
    }

    const reference = resolveReferenceQuery(
      token.query,
      indexes,
      diagnostics,
      rowNumber,
      columnNumber,
      ['section', 'control', 'option'],
    );
    if (!reference) continue;

    singularParts.push({
      ref: {
        kind: reference.kind,
        id: reference.id,
      },
    });
  }

  const singular = normalizeTemplateParts(singularParts);
  return {
    singular,
    plural: pluralizeTemplateParts(singular),
  };
}

function createOptionId(option) {
  if (templateHasReferences(option.labelTemplate)) {
    return option.rawLabel.trim().replace(/\s+/g, ' ');
  }

  return createLiteralTextValue(option.rawLabel).singular;
}

function addToLookup(map, key, value) {
  if (!key) return;
  const normalized = normalizeLookupKey(key);
  const bucket = map.get(normalized);
  if (bucket) {
    bucket.push(value);
  } else {
    map.set(normalized, [value]);
  }
}

function validateOptionCounts(controlDraft, diagnostics) {
  const optionCount = controlDraft.options.length;

  if (optionCount === 0) {
    pushError(
      diagnostics,
      `Control "${controlDraft.id}" does not have any options.`,
      controlDraft.rowNumber,
      CSV_COLUMNS.firstOption + 1,
    );
    return;
  }

  if (controlDraft.controlKind === 'toggle' && optionCount === 1) {
    return;
  }

  if (controlDraft.controlKind === 'required' && optionCount === 0) {
    pushError(
      diagnostics,
      `Control "${controlDraft.id}" uses "${controlDraft.controlKind}", which requires at least one option.`,
      controlDraft.rowNumber,
      CSV_COLUMNS.firstOption + 1,
    );
  }
}

function buildDrafts(csvRows, diagnostics) {
  const sections = [];
  const sectionsById = new Map();
  const controlsById = new Map();
  const optionEntries = [];

  for (let rowIndex = 1; rowIndex < csvRows.length; rowIndex += 1) {
    const row = csvRows[rowIndex];
    const rowNumber = rowIndex + 1;

    if (!row || isRowEmpty(row)) continue;

    const sectionId = getCell(row, CSV_COLUMNS.section);
    const promptTargetRaw = getCell(row, CSV_COLUMNS.promptTarget).toLowerCase();
    const controlKind = getCell(row, CSV_COLUMNS.controlKind);
    const revealedByRaw = getCell(row, CSV_COLUMNS.revealedBy);
    const customTextRaw = getCell(row, CSV_COLUMNS.customText);
    const supplementedByRaw = getCell(row, CSV_COLUMNS.supplementedBy);
    const globalSubstitutionsRaw = getCell(row, CSV_COLUMNS.globalSubstitutions);
    const allOptionsInitiallySelected = parseBooleanCell(
      getCell(row, CSV_COLUMNS.allOptionsInitiallySelected),
      diagnostics,
      rowNumber,
      CSV_COLUMNS.allOptionsInitiallySelected + 1,
    );
    const controlId = getCell(row, CSV_COLUMNS.controlId);

    if (!sectionId) {
      pushError(diagnostics, 'Section is required.', rowNumber, CSV_COLUMNS.section + 1);
      continue;
    }

    if (!controlId) {
      pushError(diagnostics, 'Control id is required.', rowNumber, CSV_COLUMNS.controlId + 1);
      continue;
    }

    if (containsReferenceSyntax(sectionId)) {
      pushError(
        diagnostics,
        'Section ids are structural ids and cannot contain square-bracket references.',
        rowNumber,
        CSV_COLUMNS.section + 1,
      );
    }

    if (containsReferenceSyntax(controlId)) {
      pushError(
        diagnostics,
        'Control ids are structural ids and cannot contain square-bracket references.',
        rowNumber,
        CSV_COLUMNS.controlId + 1,
      );
    }

    if (promptTargetRaw && promptTargetRaw !== 'positive' && promptTargetRaw !== 'negative') {
      pushError(
        diagnostics,
        `Unsupported promptTarget "${promptTargetRaw}". Expected "positive", "negative", or blank.`,
        rowNumber,
        CSV_COLUMNS.promptTarget + 1,
      );
    }

    if (!CONTROL_KINDS.has(controlKind)) {
      pushError(diagnostics, `Unsupported control kind "${controlKind}".`, rowNumber, CSV_COLUMNS.controlKind + 1);
      continue;
    }

    let section = sectionsById.get(sectionId);
    if (!section) {
      section = {
        kind: 'section',
        id: sectionId,
        text: createLiteralTextValue(sectionId),
        promptTarget: undefined,
        rowNumber,
        controls: [],
      };
      sectionsById.set(sectionId, section);
      sections.push(section);
    }

    if (promptTargetRaw) {
      if (section.promptTarget && section.promptTarget !== promptTargetRaw) {
        pushError(
          diagnostics,
          `Section "${sectionId}" appears with conflicting promptTarget values ("${section.promptTarget}" and "${promptTargetRaw}").`,
          rowNumber,
          CSV_COLUMNS.promptTarget + 1,
        );
      } else {
        section.promptTarget = promptTargetRaw;
      }
    }

    if (controlsById.has(controlId)) {
      pushError(
        diagnostics,
        `Control id "${controlId}" is duplicated. Control ids must be unique across the whole schema.`,
        rowNumber,
        CSV_COLUMNS.controlId + 1,
      );
      continue;
    }

    const controlDraft = {
      kind: 'control',
      id: controlId,
      text: createLiteralTextValue(controlId),
      rowNumber,
      controlKind,
      revealedByRaw,
      customTextTemplate: customTextRaw
        ? parseTextTemplate(customTextRaw, diagnostics, rowNumber, CSV_COLUMNS.customText + 1, 'customText')
        : null,
      supplementedByRaw,
      globalSubstitutionsRaw,
      allOptionsInitiallySelected,
      options: [],
    };

    controlsById.set(controlId, controlDraft);
    section.controls.push(controlDraft);

    for (let columnIndex = CSV_COLUMNS.firstOption; columnIndex < row.length; columnIndex += 1) {
      const optionRaw = row[columnIndex] ?? '';
      if (!optionRaw.trim()) continue;

      const optionDraft = parseOptionCell(optionRaw, diagnostics, rowNumber, columnIndex + 1);
      if (!optionDraft) continue;

      controlDraft.options.push(optionDraft);
      optionEntries.push({ ownerControlId: controlId, option: optionDraft });

      for (const submenuOption of optionDraft.submenu?.options ?? []) {
        optionEntries.push({ ownerControlId: controlId, option: submenuOption });
      }
    }

    validateOptionCounts(controlDraft, diagnostics);
  }

  return {
    sections,
    controlsById,
    optionEntries,
  };
}

function buildReferenceIndexes(draftState) {
  const sectionsByKey = new Map();
  const controlsByKey = new Map();
  const optionsByKey = new Map();
  const optionsByControlAndKey = new Map();

  for (const section of draftState.sections) {
    addToLookup(sectionsByKey, section.id, section);
  }

  for (const control of draftState.controlsById.values()) {
    addToLookup(controlsByKey, control.id, control);
  }

  for (const { ownerControlId, option } of draftState.optionEntries) {
    for (const alias of option.aliases) {
      addToLookup(optionsByKey, alias, option);

      const scopedKey = `${normalizeLookupKey(ownerControlId)}::${normalizeLookupKey(alias)}`;
      const bucket = optionsByControlAndKey.get(scopedKey);
      if (bucket) {
        bucket.push(option);
      } else {
        optionsByControlAndKey.set(scopedKey, [option]);
      }
    }
  }

  return {
    sectionsByKey,
    controlsByKey,
    optionsByKey,
    optionsByControlAndKey,
  };
}

function resolveSingleCandidate(candidates, diagnostics, rowNumber, columnNumber, label, allowKinds) {
  const filtered = candidates.filter((candidate) => allowKinds.includes(candidate.kind));

  if (filtered.length === 1) return filtered[0];

  if (filtered.length > 1) {
    pushError(
      diagnostics,
      `Reference "${label}" is ambiguous. Use "section:", "control:", or "option:" to make it explicit.`,
      rowNumber,
      columnNumber,
    );
    return null;
  }

  pushError(diagnostics, `Reference "${label}" could not be resolved.`, rowNumber, columnNumber);
  return null;
}

function resolveReferenceQuery(rawQuery, indexes, diagnostics, rowNumber, columnNumber, allowKinds) {
  const { selector, query } = parseReferenceQuery(rawQuery);
  const normalized = normalizeLookupKey(query);

  if (!normalized) {
    pushError(diagnostics, 'Empty reference query.', rowNumber, columnNumber);
    return null;
  }

  if ((selector === 'option' || !selector) && query.includes('/')) {
    const parts = query.split('/').map((part) => part.trim()).filter(Boolean);
    if (parts.length === 2) {
      const scopedCandidates =
        indexes.optionsByControlAndKey.get(
          `${normalizeLookupKey(parts[0])}::${normalizeLookupKey(parts[1])}`,
        ) ?? [];

      if (selector === 'option') {
        return resolveSingleCandidate(scopedCandidates, diagnostics, rowNumber, columnNumber, rawQuery, ['option']);
      }

      if (scopedCandidates.length === 1 && allowKinds.includes('option')) {
        return scopedCandidates[0];
      }
    }
  }

  if (selector === 'section') {
    return resolveSingleCandidate(
      indexes.sectionsByKey.get(normalized) ?? [],
      diagnostics,
      rowNumber,
      columnNumber,
      rawQuery,
      ['section'],
    );
  }

  if (selector === 'control') {
    return resolveSingleCandidate(
      indexes.controlsByKey.get(normalized) ?? [],
      diagnostics,
      rowNumber,
      columnNumber,
      rawQuery,
      ['control'],
    );
  }

  if (selector === 'option') {
    return resolveSingleCandidate(
      indexes.optionsByKey.get(normalized) ?? [],
      diagnostics,
      rowNumber,
      columnNumber,
      rawQuery,
      ['option'],
    );
  }

  const combined = [
    ...(indexes.sectionsByKey.get(normalized) ?? []),
    ...(indexes.controlsByKey.get(normalized) ?? []),
    ...(indexes.optionsByKey.get(normalized) ?? []),
  ];

  return resolveSingleCandidate(combined, diagnostics, rowNumber, columnNumber, rawQuery, allowKinds);
}

function resolveTextTemplate(template, indexes, diagnostics, rowNumber, columnNumber, cache, stack = []) {
  const singularParts = [];
  const pluralParts = [];
  let sawPluralizableReference = false;

  for (const token of template.tokens) {
    if (token.kind === 'text') {
      singularParts.push(token.value);
      pluralParts.push(token.value);
      continue;
    }

    const entry = resolveReferenceQuery(
      token.query,
      indexes,
      diagnostics,
      rowNumber,
      columnNumber,
      ['section', 'control', 'option'],
    );
    if (!entry) continue;

    const resolved = resolveEntryText(entry, indexes, diagnostics, cache, stack);
    singularParts.push(resolved.singular);
    pluralParts.push(resolved.plural);
    if (resolved.singular !== resolved.plural) {
      sawPluralizableReference = true;
    }
  }

  const singular = singularParts.join('').trim().replace(/\s+/g, ' ');
  const pluralBase = pluralParts.join('').trim().replace(/\s+/g, ' ');
  const plural = sawPluralizableReference ? pluralBase : derivePluralPhrase(pluralBase);

  return {
    singular,
    plural,
  };
}

function resolveEntryText(entry, indexes, diagnostics, cache, stack) {
  if (cache.has(entry)) {
    const cached = cache.get(entry);
    if (cached.state === 'resolving') {
      pushError(
        diagnostics,
        `Circular text reference detected: ${[...stack, entry.id ?? entry.rawLabel ?? entry.kind].join(' -> ')}.`,
        entry.rowNumber,
        entry.columnNumber,
      );
      const fallback = entry.id ?? entry.rawLabel ?? '';
      return { singular: fallback, plural: fallback };
    }
    return cached.value;
  }

  cache.set(entry, { state: 'resolving', value: { singular: '', plural: '' } });

  let value;
  if (entry.kind === 'section' || entry.kind === 'control') {
    value = entry.text;
  } else {
    value = resolveTextTemplate(
      entry.labelTemplate,
      indexes,
      diagnostics,
      entry.rowNumber,
      entry.columnNumber,
      cache,
      [...stack, entry.rawLabel],
    );
  }

  cache.set(entry, { state: 'resolved', value });
  return value;
}

function finalizeOptionTexts(draftState, diagnostics) {
  for (const { ownerControlId, option } of draftState.optionEntries) {
    option.id = createOptionId(option);

    if (!option.id) {
      pushError(
        diagnostics,
        `Option in control "${ownerControlId}" resolved to an empty id.`,
        option.rowNumber,
        option.columnNumber,
      );
      continue;
    }

    option.aliases = Array.from(new Set([option.rawLabel.trim(), option.id].filter(Boolean)));
  }

  const indexes = buildReferenceIndexes(draftState);

  for (const { option } of draftState.optionEntries) {
    option.text = buildTextValue(option.labelTemplate, indexes, diagnostics, option.rowNumber, option.columnNumber);
  }

  for (const control of draftState.controlsById.values()) {
    const seen = new Set();
    for (const option of control.options) {
      if (seen.has(option.id)) {
        pushError(
          diagnostics,
          `Control "${control.id}" contains duplicate option id "${option.id}".`,
          option.rowNumber,
          option.columnNumber,
        );
      } else {
        seen.add(option.id);
      }
    }

    for (const option of control.options) {
      if (!option.submenu) continue;
      const submenuSeen = new Set();
      for (const submenuOption of option.submenu.options) {
        if (submenuSeen.has(submenuOption.id)) {
          pushError(
            diagnostics,
            `Option "${option.id}" contains duplicate submenu option id "${submenuOption.id}".`,
            submenuOption.rowNumber,
            submenuOption.columnNumber,
          );
        } else {
          submenuSeen.add(submenuOption.id);
        }
      }
    }
  }
}

function parseRevealedBys(raw, indexes, diagnostics, rowNumber, columnNumber) {
  if (!raw) return undefined;

  const revealedBys = [];
  for (const part of splitOnOr(raw)) {
    const reference = resolveReferenceQuery(part, indexes, diagnostics, rowNumber, columnNumber, ['control', 'option']);
    if (!reference) continue;

    if (reference.kind === 'control') {
      revealedBys.push({ controlId: reference.id });
    } else {
      revealedBys.push({ optionId: reference.id });
    }
  }

  return revealedBys.length > 0 ? revealedBys : undefined;
}

function parseSupplementedBys(raw, indexes, diagnostics, rowNumber, columnNumber) {
  if (!raw) return undefined;

  const supplementedBys = [];
  for (const entry of splitOnSemicolons(raw)) {
    const match = /^(.*\S)\s*:\s+(.+)$/.exec(entry);
    if (!match) {
      pushError(
        diagnostics,
        `Supplement entry "${entry}" is missing a ":" separator.`,
        rowNumber,
        columnNumber,
      );
      continue;
    }

    const referenceLabel = match[1].trim();
    let supplementRaw = match[2].trim();
    let side;

    const sideMatch = /^\((adj|adv)\)\s*(.+)$/i.exec(supplementRaw);
    if (sideMatch) {
      side = sideMatch[1].toLowerCase();
      supplementRaw = sideMatch[2].trim();
    }

    const reference = resolveReferenceQuery(
      referenceLabel,
      indexes,
      diagnostics,
      rowNumber,
      columnNumber,
      ['control', 'option'],
    );
    if (!reference) continue;

    const supplementalText = buildTextValue(
      parseTextTemplate(supplementRaw, diagnostics, rowNumber, columnNumber, 'supplementedBy text'),
      indexes,
      diagnostics,
      rowNumber,
      columnNumber,
    );

    if (reference.kind === 'control') {
      supplementedBys.push({
        controlId: reference.id,
        supplementalText,
        ...(side ? { side } : {}),
      });
    } else {
      supplementedBys.push({
        optionId: reference.id,
        supplementalText,
        ...(side ? { side } : {}),
      });
    }
  }

  return supplementedBys.length > 0 ? supplementedBys : undefined;
}

function parseGlobalSubstitutions(raw, indexes, diagnostics, rowNumber, columnNumber) {
  if (!raw) return undefined;

  const substitutions = [];
  for (const entry of splitOnSemicolons(raw)) {
    const pair = entry.split(/\s*(?:→|->)\s*/);
    if (pair.length !== 2) {
      pushError(
        diagnostics,
        `Global substitution "${entry}" must be in the form "from → to".`,
        rowNumber,
        columnNumber,
      );
      continue;
    }

    const fromText = buildTextValue(
      parseTextTemplate(pair[0], diagnostics, rowNumber, columnNumber, 'globalSubstitutions from'),
      indexes,
      diagnostics,
      rowNumber,
      columnNumber,
    );
    const toText = buildTextValue(
      parseTextTemplate(pair[1], diagnostics, rowNumber, columnNumber, 'globalSubstitutions to'),
      indexes,
      diagnostics,
      rowNumber,
      columnNumber,
    );

    substitutions.push({
      from: fromText,
      to: toText,
    });
  }

  return substitutions.length > 0 ? substitutions : undefined;
}

function determineInitialSelection(control, diagnostics) {
  const optionIds = control.options.map((option) => option.id);

  if (control.controlKind === 'required') {
    return optionIds;
  }

  if (!control.allOptionsInitiallySelected) return undefined;

  if (control.controlKind === 'toggle') {
    if (optionIds.length === 1) return true;
    return optionIds;
  }

  if (MULTISELECT_CONTROL_KINDS.has(control.controlKind)) {
    return optionIds;
  }

  if (control.controlKind === 'global-selector') {
    if (optionIds.length === 1) return optionIds[0];
    pushError(
      diagnostics,
      `Control "${control.id}" is a global-selector with multiple options, so "all options initially selected" cannot be represented.`,
      control.rowNumber,
      CSV_COLUMNS.allOptionsInitiallySelected + 1,
    );
    return undefined;
  }

  if (RADIO_CONTROL_KINDS.has(control.controlKind)) {
    if (optionIds.length === 1) return optionIds[0];
    pushError(
      diagnostics,
      `Control "${control.id}" is a single-select control, so "all options initially selected" cannot be represented.`,
      control.rowNumber,
      CSV_COLUMNS.allOptionsInitiallySelected + 1,
    );
    return undefined;
  }

  return undefined;
}

function toSchema(draftState, diagnostics) {
  finalizeOptionTexts(draftState, diagnostics);
  const indexes = buildReferenceIndexes(draftState);

  const schema = {
    sections: draftState.sections.map((section) => ({
      id: section.id,
      text: section.text,
      ...(section.promptTarget === 'negative' ? { promptTarget: 'negative' } : {}),
      controls: section.controls.map((control) => {
        const revealedBys = parseRevealedBys(
          control.revealedByRaw,
          indexes,
          diagnostics,
          control.rowNumber,
          CSV_COLUMNS.revealedBy + 1,
        );
        const supplementedBys = parseSupplementedBys(
          control.supplementedByRaw,
          indexes,
          diagnostics,
          control.rowNumber,
          CSV_COLUMNS.supplementedBy + 1,
        );
        const globalSubstitutions = parseGlobalSubstitutions(
          control.globalSubstitutionsRaw,
          indexes,
          diagnostics,
          control.rowNumber,
          CSV_COLUMNS.globalSubstitutions + 1,
        );
        const initiallySelectedOptions = determineInitialSelection(control, diagnostics);

        return {
          id: control.id,
          text: control.text,
          kind: control.controlKind,
          ...(control.customTextTemplate
            ? {
                customText: buildTextValue(
                  control.customTextTemplate,
                  indexes,
                  diagnostics,
                  control.rowNumber,
                  CSV_COLUMNS.customText + 1,
                ),
              }
            : {}),
          ...(revealedBys ? { revealedBys } : {}),
          ...(supplementedBys ? { supplementedBys } : {}),
          ...(globalSubstitutions ? { globalSubstitutions } : {}),
          ...(initiallySelectedOptions !== undefined ? { initiallySelectedOptions } : {}),
          options: control.options.map((option) => ({
            id: option.id,
            text: option.text,
            ...(option.submenu
              ? {
                  submenu: {
                    kind: option.submenu.kind,
                    options: option.submenu.options.map((submenuOption) => ({
                      id: submenuOption.id,
                      text: submenuOption.text,
                    })),
                  },
                }
              : {}),
          })),
        };
      }),
    })),
  };

  return schema;
}

function isPlainIdentifier(key) {
  return /^[A-Za-z_$][A-Za-z0-9_$]*$/.test(key);
}

function escapeString(value) {
  return value.replace(/\\/g, '\\\\').replace(/'/g, "\\'");
}

function formatTs(value, depth = 0) {
  const indent = '  '.repeat(depth);
  const childIndent = '  '.repeat(depth + 1);

  if (typeof value === 'string') {
    return `'${escapeString(value)}'`;
  }

  if (typeof value === 'boolean' || typeof value === 'number') {
    return String(value);
  }

  if (Array.isArray(value)) {
    if (value.length === 0) return '[]';
    return `[\n${value
      .map((item) => `${childIndent}${formatTs(item, depth + 1)}`)
      .join(',\n')}\n${indent}]`;
  }

  if (value && typeof value === 'object') {
    const entries = Object.entries(value).filter(([, current]) => current !== undefined);
    if (entries.length === 0) return '{}';

    return `{\n${entries
      .map(([key, current]) => {
        const renderedKey = isPlainIdentifier(key) ? key : `'${escapeString(key)}'`;
        return `${childIndent}${renderedKey}: ${formatTs(current, depth + 1)}`;
      })
      .join(',\n')}\n${indent}}`;
  }

  return 'undefined';
}

function createImportPath(outputPath, repoRoot) {
  const typesPath = path.resolve(repoRoot, 'src/types.ts');
  let relativePath = path.relative(path.dirname(outputPath), typesPath).replace(/\\/g, '/');
  relativePath = relativePath.replace(/\.ts$/i, '');

  if (!relativePath.startsWith('.')) {
    relativePath = `./${relativePath}`;
  }

  return relativePath;
}

function formatSource(schema, outputPath, repoRoot, exportName) {
  const importPath = createImportPath(outputPath, repoRoot);

  return `import type { Schema } from '${importPath}';

export const ${exportName}: Schema = ${formatTs(schema)};
`;
}

export function convertCsvTextToSchema(csvText, options = {}) {
  const diagnostics = [];
  const normalizedCsvText = csvText.replace(/^\uFEFF/, '');
  let csvRows = [];

  try {
    csvRows = parseCsv(normalizedCsvText);
  } catch (error) {
    pushError(diagnostics, error instanceof Error ? error.message : String(error));
  }

  if (csvRows.length === 0) {
    pushError(diagnostics, 'The CSV is empty.');
    return {
      schema: null,
      source: '',
      diagnostics,
    };
  }

  const draftState = buildDrafts(csvRows, diagnostics);
  const schema = toSchema(draftState, diagnostics);

  if (diagnostics.some((diagnostic) => diagnostic.level === 'error')) {
    return {
      schema: null,
      source: '',
      diagnostics,
    };
  }

  const repoRoot = options.repoRoot ?? path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
  const outputPath = options.outputPath ?? path.resolve(repoRoot, 'src/lib/schema.ts');
  const exportName = options.exportName ?? 'schema';

  return {
    schema,
    source: formatSource(schema, outputPath, repoRoot, exportName),
    diagnostics,
  };
}

function printDiagnostics(diagnostics) {
  for (const diagnostic of diagnostics) {
    const level = diagnostic.level.toUpperCase();
    const location = locationLabel(diagnostic.row, diagnostic.column);
    console.error(`${level}: ${location}: ${diagnostic.message}`);
  }
}

function usage() {
  console.log('Usage: node ./scripts/csv-to-schema.mjs <input.csv> [output.ts]');
}

async function main() {
  const [, , inputArg, outputArg] = process.argv;

  if (!inputArg || inputArg === '--help' || inputArg === '-h') {
    usage();
    process.exitCode = inputArg ? 0 : 1;
    return;
  }

  const scriptDir = path.dirname(fileURLToPath(import.meta.url));
  const repoRoot = path.resolve(scriptDir, '..');
  const inputPath = path.resolve(process.cwd(), inputArg);
  const outputPath = path.resolve(process.cwd(), outputArg ?? 'src/lib/schema.ts');

  const csvText = await fs.readFile(inputPath, 'utf8');
  const result = convertCsvTextToSchema(csvText, {
    repoRoot,
    outputPath,
    exportName: 'schema',
  });

  if (result.diagnostics.length > 0) {
    printDiagnostics(result.diagnostics);
  }

  if (result.diagnostics.some((diagnostic) => diagnostic.level === 'error') || !result.source) {
    process.exitCode = 1;
    return;
  }

  await fs.mkdir(path.dirname(outputPath), { recursive: true });
  await fs.writeFile(outputPath, result.source, 'utf8');

  const relativeOutput = path.relative(process.cwd(), outputPath) || path.basename(outputPath);
  console.log(`Wrote ${relativeOutput}`);
}

const isMainModule = process.argv[1]
  ? path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)
  : false;

if (isMainModule) {
  main().catch((error) => {
    console.error(error instanceof Error ? error.message : String(error));
    process.exitCode = 1;
  });
}
