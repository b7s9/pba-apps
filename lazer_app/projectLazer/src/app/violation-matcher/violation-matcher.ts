import Fuse from 'fuse.js';
import * as LazerData from './lazer.json';

export function get_fields() {
  return Object.keys(LazerData);
}

export function get_options(field: string) {
  return Object.entries(LazerData).find(
    ([key]) => key === field,
  )?.[1] as readonly string[];
}

export function best_match(field: string, userValue: string) {
  const fuse = new Fuse(get_options(field));
  return fuse.search(userValue)[0].item;
}
