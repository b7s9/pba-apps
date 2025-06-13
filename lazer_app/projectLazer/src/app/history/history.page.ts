import { Component, OnInit } from '@angular/core';

import { Storage } from '@ionic/storage-angular';

import { OnlineStatusService } from '../online-service';

@Component({
  selector: 'app-history',
  templateUrl: './history.page.html',
  styleUrls: ['./history.page.scss'],
  standalone: false,
})
export class HistoryPage implements OnInit {
  constructor(
    public onlineStatus: OnlineStatusService,
    private storage: Storage,
  ) {}

  ngOnInit() {}
}
