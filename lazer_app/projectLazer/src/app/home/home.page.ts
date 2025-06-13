import { Capacitor } from '@capacitor/core';
import { Camera, CameraResultType, CameraSource } from '@capacitor/camera';
import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { LoadingController } from '@ionic/angular';

import { Device, DeviceInfo } from '@capacitor/device';
import { Geolocation, Position } from '@capacitor/geolocation';
import { Storage } from '@ionic/storage-angular';

import { OnlineStatusService } from '../services/online.service';
import { PhotoService } from '../services/photo.service';

@Component({
  selector: 'app-home',
  templateUrl: 'home.page.html',
  styleUrls: ['home.page.scss'],
  standalone: false,
})
export class HomePage implements OnInit {
  deviceInfo: DeviceInfo | null = null;
  geoPerms: boolean | null = null;

  violationId: number | null = null;
  violationImage: string | undefined | null = null;
  violationPosition: Position | null = null;
  violationTime: Date | null = null;

  lastImage: string | undefined | null = null;
  lastPosition: Position | null = null;
  lastTime: Date | null = null;
  lastViolationData: any = null;
  lastViolationSelected: any = null;

  constructor(
    private loadingCtrl: LoadingController,
    private router: Router,
    public onlineStatus: OnlineStatusService,
    private photos: PhotoService,
    private storage: Storage,
  ) {}

  async getCurrentPosition() {
    Geolocation.getCurrentPosition({
      enableHighAccuracy: true,
      timeout: 30000,
      maximumAge: 20000,
    }).then((coordinates) => {
      this.violationPosition = coordinates;
      this.geoPerms = true;
    });
  }

  async takePicture() {
    this.violationImage = null;
    this.violationPosition = null;
    this.violationTime = null;
    this.getCurrentPosition();

    const image = await Camera.getPhoto({
      quality: 60,
      resultType: CameraResultType.Uri,
      source: CameraSource.Camera,
      webUseInput: true,
    });

    const savedImage = await this.photos.savePicture(image);

    this.violationImage = savedImage.webviewPath;
    this.violationTime = new Date();
    this.violationId = await this.storage.get('violationId').then((value) => {
      let violationId;
      if (value !== null) {
        violationId = value;
      } else {
        violationId = 1;
      }
      this.storage.set('violationId', violationId! + 1);
      return violationId;
    });
    this.storage
      .set('violation-' + this.violationId, {
        id: this.violationId,
        image: JSON.parse(JSON.stringify(savedImage.filepath)),
        time: JSON.parse(JSON.stringify(this.violationTime)),
        position: JSON.parse(JSON.stringify(this.violationPosition)),
        processed: false,
        submitted: false,
        violationType: null,
        vehicle: null,
        address: null,
        raw: null,
      })
      .then((data) => {
        this.loadingCtrl
          .create({
            message: 'Waiting for geolocation data...',
            duration: 30000,
          })
          .then((loader) => {
            loader.present();
            let check = function (dis: any) {
              setTimeout(function () {
                if (dis.violationPosition !== null) {
                  const violationData = dis.storage
                    .get('violation-' + dis.violationId)
                    .then((data: any) => {
                      data.position = JSON.parse(
                        JSON.stringify(dis.violationPosition),
                      );
                      dis.violationPosition = null;
                      dis.storage
                        .set('violation-' + dis.violationId, data)
                        .then((data: any) => {
                          loader.dismiss();
                          dis.router.navigate(['/violation-detail', data.id]);
                        });
                    });
                } else {
                  check(dis);
                }
              }, 100);
            };
            check(this);
          });
      });
  }

  requestGeoPerms = () => {
    if (Capacitor.isNativePlatform()) {
      Geolocation.requestPermissions();
    } else {
      this.getCurrentPosition();
    }
    this.checkPermission();
  };

  checkPermission = async () => {
    if (Capacitor.isNativePlatform()) {
      try {
        const status = await Geolocation.checkPermissions();
        if (status) {
          this.geoPerms = true;
        }
        this.geoPerms = false;
      } catch (e) {
        console.log(e);
        this.geoPerms = false;
      }
    } else {
      navigator.permissions.query({ name: 'geolocation' }).then((result) => {
        if (result.state === 'granted') {
          this.geoPerms = true;
        } else if (result.state === 'prompt') {
          if (
            this.deviceInfo !== null &&
            this.deviceInfo.operatingSystem === 'ios'
          ) {
            this.geoPerms = true;
          } else {
            this.geoPerms = false;
          }
        } else {
          this.geoPerms = false;
        }
      });
    }
  };

  ngOnInit(): void {
    Device.getInfo().then((deviceInfo) => {
      this.deviceInfo = deviceInfo;
      this.checkPermission();
    });
  }
}
