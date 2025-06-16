import { Component, Input, OnInit } from '@angular/core';
import { ModalController } from '@ionic/angular';

import { Browser } from '@capacitor/browser';

import { parseAddress } from 'vladdress';
import { usaStates } from 'typed-usa-states/dist/states';

import { RenderImagePipe } from '../render-image.pipe';
import { PhotoService } from '../services/photo.service';

import {
  best_match,
  get_options,
} from '../violation-matcher/violation-matcher';

function mapToUrlParams(map: any) {
  const params = new URLSearchParams();
  for (const key in map) {
    if (map.hasOwnProperty(key)) {
      params.append(key, map[key]);
    }
  }
  return params.toString();
}

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

  plateState!: string;
  plateNumber!: string;

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

  constructor(
    private modalCtrl: ModalController,
    private photos: PhotoService,
  ) {}

  cancel() {
    return this.modalCtrl.dismiss(null, 'cancel');
  }

  submit() {
    const imageBase64 = this.photos.readAsBase64(this.violation.image);
    const violationTime = new Date(this.violation.time!);
    let additionalInfo = 'none at this time';
    if (this.plateNumber || this.plateState) {
      additionalInfo = `Plate: ${this.plateState!} ${this.plateNumber}`;
    }
    const params = {
      'Date Observed': violationTime.toLocaleDateString('en-US', {
        month: '2-digit',
        day: '2-digit',
        year: 'numeric',
      }),
      'Time Observed': violationTime.toLocaleTimeString('en-US'),
      Make: this.make,
      Model: this.model,
      'Body Style': this.bodyStyle,
      'Vehicle Color': this.vehicleColor,
      'Violation Observed': this.violation.violationType,
      'How frequently does this occur?': this.frequency,
      'Block Number': this.blockNumber,
      'Street Name': this.streetName,
      'Zip Code': this.zipCode,
      'Additional Information': additionalInfo,
    };
    const submissionUrl =
      'https://app.smartsheet.com/b/form/463e9faa2a644f4fae2a956f331f451c?' +
      mapToUrlParams(params);
    console.log(submissionUrl);
    Browser.open({ url: submissionUrl });
  }

  confirm() {
    this.modalCtrl.dismiss(this.form, 'save');
  }
  getOptions(field: string): string[] {
    return get_options(field) as string[];
  }
  getStates(): Map<string, string> {
    return new Map(
      usaStates.map(
        (obj) => [obj.abbreviation as string, obj.name as string] as const,
      ),
    );
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
      this.bodyStyle = best_match(
        'Body Style',
        this.violation.vehicle.vehicle.type,
      );
    }
    if (this.violation.vehicle!.plate) {
      this.plateNumber =
        this.violation.vehicle.plate.props.plate[0].value.toUpperCase();
      this.plateState = this.violation.vehicle.plate.props.region[0].value
        .replace('us-', '')
        .toUpperCase();
    }
    console.log(this.plateNumber, this.plateState);
    console.log(this.blockNumber, this.streetName, this.zipCode);
    console.log(this.make, this.model, this.vehicleColor, this.bodyStyle);
  }
}
