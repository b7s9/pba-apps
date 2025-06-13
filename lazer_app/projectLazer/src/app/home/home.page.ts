import { Capacitor } from '@capacitor/core';
import { Camera, CameraResultType, CameraSource } from '@capacitor/camera';
import { Component, OnInit } from '@angular/core';
import { Device, DeviceInfo } from '@capacitor/device';
import { Geolocation, Position } from '@capacitor/geolocation';
import { LoadingController } from '@ionic/angular';
import { Storage } from '@ionic/storage-angular';

import { OnlineStatusService } from '../services/online.service';
import { PhotoService } from '../services/photo.service';

async function compressJpegDataUrl(
  dataUrl: string,
  quality: number,
): Promise<string> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => {
      const canvas = document.createElement('canvas');
      canvas.width = img.naturalWidth;
      canvas.height = img.naturalHeight;
      const ctx = canvas.getContext('2d');
      if (!ctx) {
        reject(new Error('Canvas context not available'));
        return;
      }
      ctx.drawImage(img, 0, 0);
      const compressedDataUrl = canvas.toDataURL('image/jpeg', quality);
      resolve(compressedDataUrl);
    };
    img.onerror = (error) => {
      reject(error);
    };
    img.src = dataUrl;
  });
}

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
    public onlineStatus: OnlineStatusService,
    private photos: PhotoService,
    private storage: Storage,
  ) {}

  async getCurrentPosition() {
    Geolocation.getCurrentPosition({
      enableHighAccuracy: true,
      maximumAge: 10000,
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

    console.log(savedImage);

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
    console.log(this.violationId);
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
      })
      .then((value) => {
        console.log(value);
      });
  }

  async selectVehicle(index: number) {
    this.lastViolationSelected = this.lastViolationData.vehicles[index];
    this.storage.get('violation-' + this.violationId).then((violation) => {
      violation.vehicle = this.lastViolationData.vehicles[index];
      this.storage.set('violation-' + this.violationId, violation);
    });
    console.log(this.lastViolationSelected);
  }

  async drawHitBoxes() {
    const image = document.getElementById('imagePreview') as HTMLImageElement;
    const rect = image.getBoundingClientRect();

    document.getElementById('imageOverlay')?.remove();

    const overlayDiv = document.createElement('div');
    overlayDiv.id = 'imageOverlay';
    overlayDiv.className = 'imageOverlay';
    overlayDiv.style.position = 'absolute';
    overlayDiv.style.width = rect.width + 'px';
    overlayDiv.style.height = rect.height + 'px';
    image.insertAdjacentElement('beforebegin', overlayDiv);

    const scale =
      (image!.width / image!.naturalWidth +
        image!.height / image!.naturalHeight) /
      2;

    this.lastViolationData.vehicles.forEach((element: any, index: number) => {
      if (element.vehicle) {
        const box = document.createElement('a');
        box.style.position = 'absolute';
        box.style.zIndex = `${15 - index}`;
        box.style.border = '3px solid lime';
        box.style.left = element.vehicle.box.xmin * scale + 'px';
        box.style.top = element.vehicle.box.ymin * scale + 'px';
        box.addEventListener('click', (event) => {
          this.selectVehicle(index);
        });
        box.style.width =
          (element.vehicle.box.xmax - element.vehicle.box.xmin) * scale + 'px';
        box.style.height =
          (element.vehicle.box.ymax - element.vehicle.box.ymin) * scale + 'px';
        overlayDiv.appendChild(box);
      }
      if (element.plate) {
        const box = document.createElement('div');
        box.style.position = 'absolute';
        box.style.zIndex = '8';
        box.style.border = '2px solid yellow';
        box.style.left =
          (element.plate.box.xmin / image!.naturalWidth) * image!.width + 'px';
        box.style.top =
          (element.plate.box.ymin / image!.naturalHeight) * image!.height +
          'px';
        box.style.width =
          ((element.plate.box.xmax - element.plate.box.xmin) /
            image!.naturalWidth) *
            image!.width +
          'px';
        box.style.height =
          ((element.plate.box.ymax - element.plate.box.ymin) /
            image!.naturalHeight) *
            image!.height +
          'px';
        overlayDiv.appendChild(box);
      }
    });
  }

  async submit() {
    function submitData(
      lat: number,
      long: number,
      dt: Date,
      img: string,
    ): Promise<any> {
      return new Promise((resolve, reject) => {
        let request = new XMLHttpRequest();
        request.addEventListener('readystatechange', () => {
          if (request.readyState === 4 && request.status === 200) {
            let data = JSON.parse(request.responseText);
            resolve(data);
          } else if (request.readyState === 4) {
            reject('error getting resources');
          }
        });

        compressJpegDataUrl(img, 0.3).then((newImg) => {
          const formData = new FormData();
          formData.append('latitude', JSON.stringify(lat));
          formData.append('longitude', JSON.stringify(long));
          formData.append('datetime', dt.toISOString());
          formData.append('image', newImg);

          request.open('POST', 'https://bikeaction.org/lazer/submit/');
          request.send(formData);
        });
      });
    }

    if (
      this.violationImage !== null &&
      this.violationTime !== null &&
      this.violationPosition !== null
    ) {
      this.loadingCtrl
        .create({
          message: 'Processing...',
          duration: 20000,
        })
        .then((loader) => {
          loader.present();
          submitData(
            this.violationPosition!.coords!.latitude,
            this.violationPosition!.coords!.longitude,
            this.violationTime!,
            this.violationImage!,
          )
            .then((data: any) => {
              this.lastViolationData = data;
              if (data.vehicles.length == 1) {
                this.selectVehicle(0);
              }
              this.lastImage = this.violationImage;
              this.lastTime = this.violationTime;
              this.lastPosition = this.violationPosition;
              this.violationPosition = null;
              this.violationTime = null;
              this.violationImage = null;
              this.storage
                .get('violation-' + this.violationId)
                .then((violation) => {
                  violation.processed = true;
                  violation.address = data.address;
                  this.storage.set('violation-' + this.violationId, violation);
                });
              setTimeout(() => {
                loader.dismiss();
                this.drawHitBoxes();
              }, 100);
            })
            .catch((err: any) => {
              console.log(err);
              setTimeout(() => {
                loader.dismiss();
              }, 100);
            });
        });
    }
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
