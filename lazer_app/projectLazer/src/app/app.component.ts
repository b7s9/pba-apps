import { Component } from '@angular/core';
import { Storage } from '@ionic/storage-angular';

import { OnlineStatusService } from './online-service';

@Component({
  selector: 'app-root',
  templateUrl: 'app.component.html',
  styleUrls: ['app.component.scss'],
  standalone: false,
})
export class AppComponent {
  handleTouchStart(e: any) {}
  handleTouchMove(e: any) {
    e.preventDefault();
  }

  constructor(
    public onlineStatus: OnlineStatusService,
    private storage: Storage,
  ) {
    this.storage.create();
    document.addEventListener('touchstart', this.handleTouchStart, {
      passive: false,
    });
    document.addEventListener('touchmove', this.handleTouchMove, {
      passive: false,
    });
  }
}
