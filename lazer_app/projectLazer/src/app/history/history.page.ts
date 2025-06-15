import { Component, ChangeDetectorRef } from '@angular/core';

import { Storage } from '@ionic/storage-angular';
import { Directory, Filesystem } from '@capacitor/filesystem';

import { OnlineStatusService } from '../services/online.service';
import { PhotoService, UserPhoto } from '../services/photo.service';

@Component({
  selector: 'app-history',
  templateUrl: './history.page.html',
  styleUrls: ['./history.page.scss'],
  standalone: false,
})
export class HistoryPage {
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

  getThumb(violation: any) {
    if (violation.thumbnail) {
      return violation.thumbnail;
    }
    return violation.image;
  }

  deleteViolation(violationId: number) {
    let violation = null;
    this.storage.get('violation-' + violationId).then((violation) => {
      this.photos.deletePicture(violation!.image);
      this.photos.deletePicture(violation!.thumbnail);
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

  async saveImage(violationId: number) {
    this.storage.get('violation-' + violationId).then((violation) => {
      Filesystem.readFile({
        path: violation.image,
        directory: Directory.External,
      }).then((readFile) => {
        const hiddenElement = document.createElement('a');
        hiddenElement.target = '_blank';
        hiddenElement.download = violation.image;
        hiddenElement.href = `data:image/jpeg;base64,${readFile.data}`;
        hiddenElement.click();
      });
    });
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
}
