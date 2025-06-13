import { Component } from '@angular/core';
import { Storage } from '@ionic/storage-angular';

import { OnlineStatusService } from './services/online.service';

@Component({
  selector: 'app-root',
  templateUrl: 'app.component.html',
  styleUrls: ['app.component.scss'],
  standalone: false,
})
export class AppComponent {
  private xDown: number | null = null;
  private yDown: number | null = null;

  handleTouchStart(e: any) {
    this.xDown = e.touches[0].clientX;
    this.yDown = e.touches[0].clientY;
  }
  handleTouchMove(e: any) {
    if (!this.xDown || !this.yDown) {
      return;
    }

    let xUp = e.touches[0].clientX;
    let yUp = e.touches[0].clientY;

    let xDiff = this.xDown - xUp;
    let yDiff = this.yDown - yUp;

    if (Math.abs(xDiff) > Math.abs(yDiff)) {
      if (xDiff > 0) {
        /* left swipe */
        e.preventDefault();
      } else {
        /* right swipe */
        e.preventDefault();
      }
    }
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
