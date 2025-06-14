import { Component, Input } from '@angular/core';
import { ModalController } from '@ionic/angular';

import { get_options } from '../violation-matcher/violation-matcher';

@Component({
  selector: 'app-choose-violation-modal',
  templateUrl: './choose-violation-modal.component.html',
  styleUrls: ['./choose-violation-modal.component.scss'],
  standalone: false,
})
export class ChooseViolationModalComponent {
  selection!: string;
  violations: string[] = get_options('Violation Observed') as string[];

  constructor(private modalCtrl: ModalController) {}

  renderViolationText(violation: string): string {
    if (violation.split('(').length > 1) {
      return `<div style="display: flex; flex-direction: column;"><div>${violation.split('(')[0]}</div><div><small>(${violation.split('(')[1]}</small></div>`;
    } else {
      return `<div>${violation}</div>`;
    }
  }

  setViolation(violation: string) {
    this.selection = violation;
    this.modalCtrl.dismiss(this.selection, 'save');
  }

  cancel() {
    return this.modalCtrl.dismiss({ note: null }, 'cancel');
  }

  confirm() {
    this.modalCtrl.dismiss(this.selection, 'save');
  }
}
