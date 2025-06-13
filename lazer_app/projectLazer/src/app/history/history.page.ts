import { Component, OnInit, ChangeDetectorRef } from '@angular/core';

import { Storage } from '@ionic/storage-angular';

import { OnlineStatusService } from '../services/online.service';
import { PhotoService, UserPhoto } from '../services/photo.service';

@Component({
  selector: 'app-history',
  templateUrl: './history.page.html',
  styleUrls: ['./history.page.scss'],
  standalone: false,
})
export class HistoryPage implements OnInit {
  violationHistory: any[] = [];

  constructor(
    public onlineStatus: OnlineStatusService,
    private storage: Storage,
    public photos: PhotoService,
    public changeDetectorRef: ChangeDetectorRef,
  ) {}

  async renderPhoto(filename: string): Promise<UserPhoto> {
    return await this.photos.fetchPicture(filename);
  }

  trackViolations(index: number, violation: any) {
    return violation.id;
  }

  deleteViolation(violationId: number) {
    let violation = null;
    this.storage.get('violation-' + violationId).then((violation) => {
      this.photos.deletePicture(violation!.image);
    });
    this.storage.remove('violation-' + violationId);
    this.violationHistory = this.violationHistory.filter(
      (item) => item.id !== violationId,
    );
    this.changeDetectorRef.detectChanges();
  }

  actionButtons(violationId: number) {
    return [
      {
        text: 'Cancel',
        role: 'cancel',
        handler: () => {},
      },
      {
        text: 'OK',
        role: 'confirm',
        handler: () => {
          this.deleteViolation(violationId);
        },
      },
    ];
  }

  sortViolations() {
    return this.violationHistory
      .sort(function (a, b) {
        var x = new Date(a.time);
        var y = new Date(b.time);
        return x > y ? -1 : x < y ? 1 : 0;
      })
      .slice(0, 20);
  }

  ionViewWillEnter() {
    this.violationHistory = [];
    this.storage.forEach((value, key, index) => {
      if (key.startsWith('violation-')) {
        this.violationHistory.push(value);
      }
    });
  }

  ngOnInit() {}
}
