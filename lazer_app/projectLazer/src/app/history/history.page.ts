import { Component, OnInit } from '@angular/core';

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
  ) {}

  async renderPhoto(filename: string): Promise<UserPhoto> {
    return await this.photos.fetchPicture(filename);
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
