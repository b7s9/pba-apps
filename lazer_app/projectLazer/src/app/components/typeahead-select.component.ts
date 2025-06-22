import { Component, Input, Output, EventEmitter } from '@angular/core';
import type { OnInit } from '@angular/core';

import { Item } from './types';

@Component({
  selector: 'app-typeahead',
  templateUrl: 'typeahead-select.component.html',
  standalone: false,
})
export class TypeaheadComponent implements OnInit {
  @Input() items: Item[] = [];
  @Input() selectedItem: string | undefined = undefined;
  @Input() title = 'Select Item';

  @Output() selectionCancel = new EventEmitter<void>();
  @Output() selectionChange = new EventEmitter<string>();

  filteredItems: Item[] = [];
  workingSelectedValue: string | undefined = undefined;

  ngOnInit() {
    this.filteredItems = [...this.items];
    this.workingSelectedValue = this.selectedItem;
  }

  cancelChanges() {
    this.selectionCancel.emit();
  }

  confirmChanges() {
    this.selectionChange.emit(this.workingSelectedValue);
  }

  searchbarInput(event: Event) {
    const inputElement = event.target as HTMLInputElement;
    this.filterList(inputElement.value);
  }

  /**
   * Update the rendered view with
   * the provided search query. If no
   * query is provided, all data
   * will be rendered.
   */
  filterList(searchQuery: string | undefined) {
    /**
     * If no search query is defined,
     * return all options.
     */
    if (searchQuery === undefined || searchQuery.trim() === '') {
      this.filteredItems = [...this.items];
    } else {
      /**
       * Otherwise, normalize the search
       * query and check to see which items
       * contain the search query as a substring.
       */
      const normalizedQuery = searchQuery.toLowerCase();
      this.filteredItems = this.items.filter((item) =>
        item.text.toLowerCase().includes(normalizedQuery)
      );
    }
  }

  isChecked(value: string): boolean {
    return this.workingSelectedValue == value;
  }

  checkboxChange(event: CustomEvent<{ checked: boolean; value: string }>) {
    const { checked, value } = event.detail;

    if (checked) {
      this.workingSelectedValue = value;
    }
  }
}
