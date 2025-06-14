import { Component, Input, OnInit } from '@angular/core';
import { ModalController } from '@ionic/angular';

import { parseAddress } from 'vladdress';

import {
  best_match,
  get_options,
} from '../violation-matcher/violation-matcher';

@Component({
  selector: 'app-confirm-violation-details-modal',
  templateUrl: './confirm-violation-details-modal.component.html',
  styleUrls: ['./confirm-violation-details-modal.component.scss'],
  standalone: false,
})
export class ConfirmViolationDetailsModalComponent implements OnInit {
  make!: string;
  model!: string;
  bodyStyle!: string;
  vehicleColor!: string;

  frequency: string = 'Unsure';

  blockNumber!: string;
  streetName!: string;
  zipCode!: string;

  fields: string[] = [
    'Body Style',
    'Make',
    'Vehicle Color',

    'Block Number',
    'Street Name',
    'Zip Code',

    'How frequently does this occur?',
  ];

  @Input() violation: any;
  @Input() form: any;

  constructor(private modalCtrl: ModalController) {}

  cancel() {
    return this.modalCtrl.dismiss(null, 'cancel');
  }

  confirm() {
    this.modalCtrl.dismiss(this.form, 'save');
  }
  getOptions(field: string): string[] {
    return get_options(field) as string[];
  }

  ngOnInit(): void {
    const parsedAddress = parseAddress(this.violation.address);
    this.blockNumber = parsedAddress.streetNumber as string;
    this.streetName = best_match(
      'Street Name',
      `${parsedAddress.streetName} ${parsedAddress.streetSuffix}`,
    );
    this.zipCode = best_match('Zip Code', parsedAddress.zipCode as string);

    if (this.violation.vehicle!.vehicle?.props?.make_model[0].make) {
      this.make = best_match(
        'Make',
        this.violation.vehicle.vehicle.props.make_model[0].make,
      );
    }
    if (this.violation.vehicle!.vehicle?.props?.make_model[0].model) {
      this.model = this.violation.vehicle.vehicle.props.make_model[0].model;
    }
    if (this.violation.vehicle!.vehicle?.props?.color[0].value) {
      this.vehicleColor = best_match(
        'Vehicle Color',
        this.violation.vehicle.vehicle.props.color[0].value,
      );
    }
    if (this.violation.vehicle!.vehicle?.type) {
      console.log(this.violation.vehicle.vehicle.type);
      this.bodyStyle = best_match(
        'Body Style',
        this.violation.vehicle.vehicle.type,
      );
    }
    console.log(this.blockNumber, this.streetName, this.zipCode);
    console.log(this.make, this.model, this.vehicleColor, this.bodyStyle);
  }
}
